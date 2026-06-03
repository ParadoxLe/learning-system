from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db
from backend.routers import profile, resource, path, tutor, student, video, auth, library, plan, digital_human, blind_box, rag, knowledge_graph, quiz


app = FastAPI(
    title="多智能体个性化学习资源生成系统",
    description="基于DeepSeek API的多智能体协作学习系统",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(profile.router)
app.include_router(resource.router)
app.include_router(path.router)
app.include_router(tutor.router)
app.include_router(student.router)
app.include_router(video.router)
app.include_router(auth.router)
app.include_router(library.router)
app.include_router(plan.router)
app.include_router(digital_human.router)
app.include_router(blind_box.router)
app.include_router(rag.router)
app.include_router(knowledge_graph.router)
app.include_router(quiz.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"message": "多智能体个性化学习资源生成系统 API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}
