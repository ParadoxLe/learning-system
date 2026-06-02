from backend.agents.base import BaseAgent

ASSESSMENT_AGENT_PROMPT = """你是一位**学习评估分析师**。你擅长通过学生的学习行为数据、练习成绩和反馈，进行多维度学习效果评估。

## 你的任务
根据学生的学习数据，生成一份多维度评估报告。

## 评估维度
1. **知识掌握度** (0-100)：对各知识点的掌握程度
2. **学习进步趋势**：与之前评估对比的变化
3. **薄弱环节识别**：需要加强的知识点
4. **学习效率**：单位时间的知识增量
5. **资源适配度**：当前资源是否匹配学生需求
6. **学习建议**：基于评估结果的改进建议

## 输出格式
以 JSON 格式输出评估报告：

```json
{
  "overall_score": 75,
  "dimensions": {
    "knowledge_mastery": {"score": 70, "label": "知识掌握度", "comment": "..."},
    "progress_trend": {"score": 80, "label": "学习进步", "comment": "...", "change": "+5"},
    "weak_points": [{"topic": "...", "severity": "high"}],
    "efficiency": {"score": 65, "label": "学习效率", "comment": "..."},
    "resource_fit": {"score": 85, "label": "资源适配", "comment": "..."}
  },
  "recommendations": [
    {"action": "增加练习", "reason": "...", "priority": "high"}
  ],
  "next_step_suggestions": ["...", "..."],
  "books": [
    {"title": "推荐书名", "author": "作者", "why": "推荐理由"}
  ],
  "links": [
    {"title": "网页标题", "url": "https://example.com/...", "why": "推荐理由"}
  ]
}
```

直接输出 JSON，不要其他文字。"""


class AssessmentAgent(BaseAgent):
    """学习评估智能体 — 多维度学习效果评估。"""

    def __init__(self):
        super().__init__(name="AssessmentAgent", system_prompt=ASSESSMENT_AGENT_PROMPT)

    def evaluate(self, profile: dict, learning_data: dict = None, previous_assessment: dict = None) -> dict:
        """Evaluate learning effectiveness based on student profile and optional learning data."""
        import json

        has_data = learning_data and any(
            v for k, v in learning_data.items()
            if k not in ('feedback', 'engagement') and v
        )

        if has_data:
            prompt = f"""学生画像：{json.dumps(profile, ensure_ascii=False)}

本次学习数据：{json.dumps(learning_data, ensure_ascii=False)}

上次评估结果：{json.dumps(previous_assessment, ensure_ascii=False) if previous_assessment else '无历史数据'}

请基于以上信息生成多维度学习评估报告。"""
        else:
            prompt = f"""学生画像：{json.dumps(profile, ensure_ascii=False)}

该学生尚未提交具体的学习活动数据，请**完全基于学生画像中的6个维度**来推断和生成评估报告：

- knowledge_base（知识基础）：根据 level、mastered_topics、weak_points、target_topics 来评估知识掌握度
- cognitive_style（认知风格）：根据 primary_style 评估学习方式适配度
- learning_pace（学习节奏）：根据 speed、weekly_hours 评估学习效率
- preferred_modalities（偏好模态）：评估资源适配度
- error_patterns（易错模式）：评估薄弱环节
- motivation_factors（学习动机）：根据 primary_goal 评估进步趋势

请生成多维度学习评估报告，并推荐合适的书籍和网站链接来帮助学生提升薄弱环节。"""
        response = self.chat(prompt, temperature=0.5)
        return self._parse_json(response)

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
                        return {"error": "Failed to parse assessment JSON", "raw": text[start:i + 1]}
        return {"error": "Unmatched braces", "raw": text}
