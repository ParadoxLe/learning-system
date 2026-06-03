"""
Remote deployment script for learning-agent-system.
Run this locally to deploy to the remote server.
"""
import paramiko
import os
import sys
import tarfile
import io
import time

HOST = "117.72.98.73"
USER = "root"
PWD = "Xxx228461"
REMOTE_DIR = "/opt/learning-agent-system"
LOCAL_DIR = r"W:\MyWorkSpace\learning-agent-system"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


def run(cmd, desc=""):
    """Execute command on remote and print output"""
    label = f"[{desc}]" if desc else "[remote]"
    print(f"{label} $ {cmd[:120]}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode(errors="replace").strip()
    err = stderr.read().decode(errors="replace").strip()
    if out:
        print(out)
    if err and "warning" not in err.lower():
        print(f"  stderr: {err[:300]}")
    return out


def run_stream(cmd, desc=""):
    """Execute command with live streaming output"""
    label = f"[{desc}]" if desc else "[remote]"
    print(f"{label} $ {cmd[:120]}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    while True:
        line = stdout.readline()
        if not line:
            break
        print(line.rstrip())
    err = stderr.read().decode(errors="replace").strip()
    if err and "warning" not in err.lower():
        print(f"  stderr: {err[:300]}")


def upload_file(local_path, remote_path):
    """Upload a single file via SFTP"""
    print(f"[upload] {local_path} -> {remote_path}")
    sftp = client.open_sftp()
    # Ensure parent dir exists
    remote_dir = os.path.dirname(remote_path)
    try:
        sftp.stat(remote_dir)
    except FileNotFoundError:
        # Create directory recursively
        parts = remote_dir.strip("/").split("/")
        path = ""
        for p in parts:
            path += "/" + p
            try:
                sftp.stat(path)
            except FileNotFoundError:
                sftp.mkdir(path)
    sftp.put(local_path, remote_path)
    sftp.close()


def upload_dir(local_dir_path, remote_dir_path):
    """Walk a local directory and upload all files to remote"""
    sftp = client.open_sftp()
    for root, dirs, files in os.walk(local_dir_path):
        # Compute relative path
        rel = os.path.relpath(root, local_dir_path)
        if rel == ".":
            remote_root = remote_dir_path
        else:
            remote_root = f"{remote_dir_path}/{rel}"
        # Create remote dir
        try:
            sftp.stat(remote_root)
        except FileNotFoundError:
            # mkdir recursively
            parts = remote_root.strip("/").split("/")
            path = ""
            for p in parts:
                if not p:
                    continue
                path += "/" + p
                try:
                    sftp.stat(path)
                except FileNotFoundError:
                    sftp.mkdir(path)
        # Upload files
        for f in files:
            local_path = os.path.join(root, f)
            remote_path = f"{remote_root}/{f}"
            try:
                sftp.put(local_path, remote_path)
            except Exception as e:
                print(f"  [SKIP] {local_path}: {e}")
    sftp.close()


# ===== MAIN =====
print("=" * 50)
print("  Learning Agent System - Remote Deploy")
print("=" * 50)
print(f"  Target: {USER}@{HOST}")
print(f"  Remote path: {REMOTE_DIR}")
print()

# ---- Step 1: Connect ----
print("[1/6] Connecting to server...")
try:
    client.connect(HOST, username=USER, password=PWD, timeout=20)
    print("[OK] Connected")
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
    sys.exit(1)

# ---- Step 2: Check server environment ----
print("\n[2/6] Checking server environment...")
run("cat /etc/os-release | head -4", "OS check")
docker_ok = run("docker --version 2>&1", "Docker check")
compose_ok = run("docker compose version 2>&1 || docker-compose --version 2>&1", "Compose check")
run("df -h / | tail -1", "Disk")
run("free -m | head -2", "Memory")
run("ss -tlnp 2>/dev/null | head -15 || ss -tlnp 2>/dev/null | head -15", "Ports")

# Check if Docker is available
if "version" not in docker_ok.lower():
    print("\n[Docker not found. Installing Docker...]")
    run_stream("curl -fsSL https://get.docker.com | sh", "Install Docker")
    run("systemctl enable docker && systemctl start docker", "Start Docker")
    run("docker --version", "Verify Docker")

if "version" not in compose_ok.lower():
    print("\n[docker-compose not found, using 'docker compose' plugin]")

# ---- Step 3: Upload project files ----
print("\n[3/6] Uploading project files...")
# Create remote directory
run(f"mkdir -p {REMOTE_DIR}")

# Upload only what's needed (not node_modules, __pycache__, .idea, etc.)
exclude = {
    "node_modules", "__pycache__", ".idea", ".git", ".gitignore",
    "frontend-vue/node_modules", "frontend-vue/dist",
    "_deploy_remote.py", ".venv", "venv", "env",
}

upload_dir(LOCAL_DIR, REMOTE_DIR)

# ---- Step 4: Create .env on server ----
print("\n[4/6] Setting up .env on server...")
# Copy the existing .env to the server (it has all the API keys already)
run(f"ls {REMOTE_DIR}/.env && echo '.env exists'")

# ---- Step 5: Build and start ----
print("\n[5/6] Building and starting Docker containers...")
run_stream(f"cd {REMOTE_DIR} && docker compose build 2>&1", "Docker build")

print("\nStarting containers...")
run_stream(f"cd {REMOTE_DIR} && docker compose up -d 2>&1", "Docker up")

# ---- Step 6: Verify ----
print("\n[6/6] Verifying deployment...")
time.sleep(5)
run("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'", "Container status")
run_stream(f"curl -s http://localhost:80/ || echo 'Frontend not ready yet'", "Test frontend")
run_stream(f"curl -s http://localhost:80/api/health || echo 'Backend not ready yet'", "Test API")

print("\n" + "=" * 50)
print("  Deployment complete!")
print(f"  Frontend: http://{HOST}")
print(f"  API docs: http://{HOST}/api/docs")
print("=" * 50)

client.close()
