from backend.agents.base import BaseAgent

PATH_AGENT_PROMPT = """你是一位**学习路径规划师**。你擅长根据学生的知识水平、学习目标和可用资源，设计科学合理的学习路径。

## 你的任务
根据学生画像和已有的学习资源，规划一条个性化的学习路径。

## 输出要求
以 JSON 格式输出学习路径，包含以下结构：

```json
{
  "title": "学习路径标题",
  "total_duration_hours": 20,
  "phases": [
    {
      "phase": 1,
      "name": "阶段名称",
      "goal": "本阶段目标",
      "duration_hours": 5,
      "nodes": [
        {
          "order": 1,
          "title": "学习节点标题",
          "type": "study|practice|review|project|assessment",
          "resource_type": "doc|mindmap|exercise|reading|video_script|code_case",
          "duration_min": 30,
          "description": "节点描述",
          "books": [
            {"title": "推荐书名", "author": "作者", "why": "推荐理由"}
          ],
          "links": [
            {"title": "网页标题", "url": "https://example.com/...", "why": "推荐理由"}
          ]
        }
      ]
    }
  ],
  "advice": "学习建议"
}
```

## 设计原则
1. 遵循 **先理论后实践** 的顺序
2. 知识薄弱点安排更多练习节点
3. 根据 learning_pace 调整节点密度
4. 穿插复习节点巩固记忆
5. 每阶段结束安排评估节点
6. 根据 preferred_modalities 调整资源类型配比

## 重要：书籍与链接推荐
- 每个节点必须包含 1-3 本**真实存在**的经典书籍推荐（书名+作者），用 books 数组给出
- 每个节点必须包含 1-3 个**高质量**的网页/在线教程链接，用 links 数组给出
- 书籍和链接必须与该节点的学习主题**强相关**
- 链接 URL 必须真实可用（优先推荐知名网站如官方文档、菜鸟教程、MDN、Coursera、B站等）
- 推荐理由需简短说明（15字以内）

直接输出 JSON，不要其他文字。"""


class PathAgent(BaseAgent):
    """学习路径规划智能体。"""

    def __init__(self):
        super().__init__(name="PathAgent", system_prompt=PATH_AGENT_PROMPT)

    def plan(self, profile: dict, resources: list[dict], course_goal: str = "") -> dict:
        """Generate a personalized learning path."""
        prompt = self._build_prompt(profile, resources, course_goal)
        response = self.chat(prompt, temperature=0.5)
        return self._parse_json(response)

    def plan_stream(self, profile: dict, resources: list[dict], course_goal: str = ""):
        """Stream learning path generation."""
        prompt = self._build_prompt(profile, resources, course_goal)
        full_response = ""
        for token in self.chat_stream(prompt, temperature=0.5):
            full_response += token
            yield token
        yield self._parse_json(full_response)

    def _build_prompt(self, profile: dict, resources: list[dict], course_goal: str) -> str:
        resources_summary = []
        for r in resources:
            resources_summary.append({
                "id": r.get("id"),
                "type": r.get("resource_type"),
                "title": r.get("title"),
            })

        return f"""学生画像：
{profile}

可用学习资源：
{resources_summary}

学习目标：{course_goal or profile.get('motivation_factors', {}).get('primary_goal', '掌握课程知识')}

请为此学生规划个性化学习路径。"""

    @staticmethod
    def _parse_json(text: str) -> dict:
        import json
        import re
        text = text.strip()
        text = re.sub(r'^```(?:json)?\s*\n?', '', text)
        text = re.sub(r'\n?```\s*$', '', text)
        start = text.find('{')
        if start == -1:
            return {"error": "No JSON found", "raw": text}
        depth = 0
        for i in range(start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        return {"error": "Failed to parse path JSON", "raw": text[start:i + 1]}
        return {"error": "Unmatched braces", "raw": text}
