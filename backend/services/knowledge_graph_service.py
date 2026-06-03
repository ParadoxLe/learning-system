"""
Knowledge Graph Service — builds a visualizable graph from student profile data.
Nodes = topics/concepts/skills, Edges = prerequisite / related-to / part-of relationships.
"""

import json
import logging

logger = logging.getLogger(__name__)

# Warm color palette for node categories
PALETTE = {
    "mastered": "#3D7A5C",      # forest green
    "weak": "#722F37",          # wine red
    "target": "#C8A25C",        # bronze gold
    "core": "#5D3A2C",          # walnut brown
    "style": "#7FA08E",         # sage green
    "modality": "#5D7A8A",      # slate blue
    "error": "#A0403D",         # muted red
    "goal": "#B8934F",          # dark gold
}

CATEGORY_LABELS = {
    "mastered": "已掌握",
    "weak": "薄弱点",
    "target": "目标主题",
    "core": "核心概念",
    "style": "认知风格",
    "modality": "学习模态",
    "error": "易错模式",
    "goal": "学习目标",
}


def build_knowledge_graph(profile: dict) -> dict:
    """Build a knowledge graph (nodes + edges) from a student profile dict.

    Returns a dict with:
      - nodes: [{id, name, category, value (size), symbolSize, itemStyle}]
      - edges: [{source, target, label}]
      - categories: [{name, itemStyle}]
    """
    nodes = []
    edges = []
    kb = profile.get("knowledge_base", {}) or {}
    cs = profile.get("cognitive_style", {}) or {}
    lp = profile.get("learning_pace", {}) or {}
    mf = profile.get("motivation_factors", {}) or {}
    mods = profile.get("preferred_modalities", []) or []
    errs = profile.get("error_patterns", []) or []

    # --- Central node ---
    central_id = "student"
    nodes.append({
        "id": central_id,
        "name": profile.get("student_name", "我"),
        "category": "core",
        "symbolSize": 64,
        "value": 100,
        "itemStyle": {"color": PALETTE["core"]},
        "label": {"fontSize": 15, "fontWeight": "bold"},
    })

    # --- Knowledge base topics ---
    mastered = kb.get("mastered_topics", []) or []
    weak = kb.get("weak_points", []) or []
    targets = kb.get("target_topics", []) or []

    for topic in mastered:
        tid = f"mastered_{topic}"
        nodes.append(_topic_node(tid, topic, "mastered", 42))
        edges.append({"source": central_id, "target": tid, "label": "已掌握"})

    for topic in weak:
        tid = f"weak_{topic}"
        nodes.append(_topic_node(tid, topic, "weak", 40))
        edges.append({"source": central_id, "target": tid, "label": "薄弱"})

    for topic in targets:
        tid = f"target_{topic}"
        nodes.append(_topic_node(tid, topic, "target", 46))
        edges.append({"source": central_id, "target": tid, "label": "目标"})

    # Connect mastered → target (prerequisite edges)
    for m in mastered:
        for t in targets:
            edges.append({
                "source": f"mastered_{m}",
                "target": f"target_{t}",
                "label": "前置知识",
                "lineStyle": {"type": "dashed", "opacity": 0.4},
            })

    # --- Cognitive style ---
    style = cs.get("primary_style", "")
    if style:
        sid = f"style_{style}"
        nodes.append({
            "id": sid,
            "name": _style_label(style),
            "category": "style",
            "symbolSize": 34,
            "value": 60,
            "itemStyle": {"color": PALETTE["style"]},
        })
        edges.append({"source": central_id, "target": sid, "label": "认知风格"})

    # --- Learning pace ---
    speed = lp.get("speed", "")
    hours = lp.get("weekly_hours", 0)
    if speed or hours:
        pid = "pace"
        nodes.append({
            "id": pid,
            "name": f"节奏: {speed or '未知'} · {hours}h/周",
            "category": "modality",
            "symbolSize": 32,
            "value": 50,
            "itemStyle": {"color": PALETTE["modality"]},
        })
        edges.append({"source": central_id, "target": pid, "label": "学习节奏"})

    # --- Preferred modalities ---
    for mod in mods:
        mid = f"mod_{mod}"
        nodes.append({
            "id": mid,
            "name": _modality_label(mod),
            "category": "modality",
            "symbolSize": 30,
            "value": 45,
            "itemStyle": {"color": PALETTE["modality"]},
        })
        edges.append({"source": central_id, "target": mid, "label": "偏好"})

    # --- Error patterns ---
    for err in errs:
        eid = f"err_{err}"
        nodes.append({
            "id": eid,
            "name": err,
            "category": "error",
            "symbolSize": 30,
            "value": 40,
            "itemStyle": {"color": PALETTE["error"]},
        })
        edges.append({"source": central_id, "target": eid, "label": "易错"})

    # --- Motivation ---
    goal = mf.get("primary_goal", "")
    if goal:
        gid = "goal"
        nodes.append({
            "id": gid,
            "name": goal,
            "category": "goal",
            "symbolSize": 40,
            "value": 55,
            "itemStyle": {"color": PALETTE["goal"]},
        })
        edges.append({"source": central_id, "target": gid, "label": "目标"})

    # --- Categories meta ---
    categories = [
        {"name": cat, "itemStyle": {"color": PALETTE.get(cat, "#999")}}
        for cat in sorted(set(n["category"] for n in nodes))
    ]

    total_topics = len(mastered) + len(weak) + len(targets)
    mastery_pct = round(len(mastered) / total_topics * 100) if total_topics > 0 else 0

    return {
        "nodes": nodes,
        "edges": edges,
        "categories": categories,
        "summary": {
            "mastered_count": len(mastered),
            "weak_count": len(weak),
            "target_count": len(targets),
            "total_topics": total_topics,
            "mastery_pct": mastery_pct,
            "level": kb.get("level", "unknown"),
        },
    }


def _topic_node(tid: str, name: str, category: str, size: int) -> dict:
    return {
        "id": tid,
        "name": name,
        "category": category,
        "symbolSize": size,
        "value": size * 2,
        "itemStyle": {"color": PALETTE.get(category, "#999")},
    }


def _style_label(s: str) -> str:
    MAP = {
        "visual": "视觉型",
        "verbal": "文字型",
        "logical": "逻辑型",
        "hands_on": "动手型",
        "social": "社交型",
    }
    return MAP.get(s, s)


def _modality_label(m: str) -> str:
    MAP = {
        "text": "文本",
        "video": "视频",
        "audio": "音频",
        "interactive": "互动",
        "code": "代码",
    }
    return MAP.get(m, m)
