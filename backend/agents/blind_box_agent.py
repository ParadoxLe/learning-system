from typing import Optional, List
from backend.agents.base import BaseAgent

BLIND_BOX_PROMPT = """你是一位**每日知识盲盒策划师**。你的任务是根据学生的学习画像，每天生成一个有趣、有料的知识小卡片。

## 要求
1. 根据学生的**学习目标、薄弱环节、当前水平、兴趣方向**，生成一个与他们学习路径相关的知识点
2. 内容要有惊喜感——可以是他们领域内的冷知识、实用技巧、常见误区、或者跨领域的趣味关联
3. 语言通俗易懂，像朋友分享趣闻一样，不要教科书式的说教
4. 控制长度：title不超过15个字，content在80-150字之间
5. 难度与学生当前水平匹配（入门级给基础但有趣的内容，高级给有深度的insight）

## 输出格式
严格输出 JSON，不要有其他内容：

```json
{
  "title": "知识点标题",
  "content": "知识点内容，80-150字，轻松有趣",
  "category": "分类（如：编程/AI/计算机基础/学习方法/软件工程/数学等）",
  "difficulty": "beginner/intermediate/advanced"
}
```"""


class BlindBoxAgent(BaseAgent):
    def __init__(self):
        super().__init__("盲盒策划师", BLIND_BOX_PROMPT)

    def generate_card(self, profile: dict, rag_context: Optional[List[str]] = None) -> dict:
        """Generate a personalized daily knowledge card based on student profile + RAG context."""
        import json

        # Build profile summary for the prompt
        kb = profile.get("knowledge_base", {}) if profile else {}
        cs = profile.get("cognitive_style", {}) if profile else {}
        lp = profile.get("learning_pace", {}) if profile else {}
        mf = profile.get("motivation_factors", {}) if profile else {}

        level = kb.get("level", "beginner")
        topics = kb.get("topics", [])
        weak_points = kb.get("weak_points", [])
        strengths = kb.get("strengths", [])
        goal = mf.get("primary_goal", "未设定")
        style = cs.get("primary_style", "未知")
        interests = mf.get("interests", [])

        prompt_parts = ["请根据以下学生画像生成今日知识盲盒卡片："]
        prompt_parts.append(f"- 当前水平：{level}")
        if topics:
            prompt_parts.append(f"- 已学主题：{', '.join(str(t) for t in topics[:8])}")
        if weak_points:
            prompt_parts.append(f"- 薄弱环节：{', '.join(str(w) for w in weak_points[:5])}")
        if strengths:
            prompt_parts.append(f"- 擅长领域：{', '.join(str(s) for s in strengths[:5])}")
        if goal:
            prompt_parts.append(f"- 学习目标：{goal}")
        if interests:
            prompt_parts.append(f"- 兴趣方向：{', '.join(str(i) for i in interests[:5])}")
        if style:
            prompt_parts.append(f"- 学习风格：{style}")

        # Add RAG context if available
        if rag_context:
            prompt_parts.append(f"\n## 该学生相关资料片段（来自其学习资源和上传文件）")
            for i, chunk in enumerate(rag_context, 1):
                # Truncate each chunk to avoid oversized prompt
                snippet = chunk[:300]
                prompt_parts.append(f"片段{i}：{snippet}")

        prompt_parts.append(f"\n请确保难度匹配{level}水平，生成一个与学生画像相关的知识点。如有资料片段，尽量围绕相关内容生成。")

        user_message = "\n".join(prompt_parts)

        try:
            text = self.chat(user_message, temperature=0.9)
            # Extract JSON from response (may have ```json fences)
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            result = json.loads(text.strip())
            return {
                "title": str(result.get("title", "")),
                "content": str(result.get("content", "")),
                "category": str(result.get("category", "综合")),
                "difficulty": str(result.get("difficulty", level)),
            }
        except Exception:
            return None
