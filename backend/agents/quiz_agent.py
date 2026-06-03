"""QuizAgent — generates targeted multiple-choice questions based on student's weak points."""

from backend.agents.base import BaseAgent

QUIZ_AGENT_PROMPT = """你是一位**学习评估与练习设计专家**。你擅长根据学生的知识薄弱点，设计针对性的选择题来帮助ta巩固知识。

## 你的任务
根据学生的画像数据（尤其是薄弱点 weak_points），生成 4~5 道单选题。

## 出题要求
1. 每道题针对一个薄弱点
2. 题目难度适中，适合该学生的当前水平
3. 选项要有干扰性（不能太明显）
4. 每题附带正确答案和解析（为什么对、为什么错）

## 输出格式
以 JSON 格式输出：

```json
{
  "questions": [
    {
      "id": 1,
      "topic": "相关知识点",
      "question": "题目内容",
      "options": [
        {"key": "A", "text": "选项A"},
        {"key": "B", "text": "选项B"},
        {"key": "C", "text": "选项C"},
        {"key": "D", "text": "选项D"}
      ],
      "correct": "A",
      "explanation": "解析：为什么A正确，其他选项为什么错误"
    }
  ]
}
```

直接输出 JSON，不要其他文字。"""


class QuizAgent(BaseAgent):
    """练习出题智能体 — 针对薄弱点生成选择题。"""

    def __init__(self):
        super().__init__(name="QuizAgent", system_prompt=QUIZ_AGENT_PROMPT)

    def generate(self, profile: dict, count: int = 5) -> dict:
        """Generate quiz questions targeting weak points in the student profile."""
        import json

        kb = profile.get("knowledge_base", {}) or {}
        weak_points = kb.get("weak_points", []) or []
        mastered = kb.get("mastered_topics", []) or []
        target = kb.get("target_topics", []) or []
        level = kb.get("level", "beginner")
        errs = profile.get("error_patterns", []) or []

        topics_str = json.dumps({
            "level": level,
            "weak_points": weak_points,
            "mastered_topics": mastered,
            "target_topics": target,
            "error_patterns": errs,
        }, ensure_ascii=False)

        prompt = f"""学生画像：{topics_str}

请根据以上信息生成 {count} 道单选题，重点针对薄弱点 {json.dumps(weak_points, ensure_ascii=False)} 出题。
题目难度应适合「{level}」水平的学生。"""

        response = self.chat(prompt, temperature=0.7)
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
                        return {"error": "Failed to parse quiz JSON", "raw": text[start:i + 1]}
        return {"error": "Unmatched braces", "raw": text}
