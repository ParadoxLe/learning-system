from backend.agents.base import BaseAgent

ORCHESTRATOR_PROMPT = """你是一个**多智能体学习系统的总协调者**。你负责理解学生的意图，并将任务分发给合适的专业智能体。

## 你能协调的智能体
1. **ProfileAgent** — 学习画像构建（对话了解学生）
2. **ResourceAgents** — 资源生成（doc课程文档, mindmap思维导图, exercise练习题, reading拓展阅读, video_script视频脚本, code_case代码案例）
3. **PathAgent** — 学习路径规划
4. **TutorAgent** — 智能答疑辅导
5. **AssessmentAgent** — 学习效果评估

## 你的任务
分析用户输入，判断用户意图属于以下哪种：

- **build_profile**: 用户在描述自己的学习情况 → 调用 ProfileAgent 构建/更新画像
- **generate_resources**: 用户想要学习资料 → 调用 ResourceAgents 生成资源
- **plan_path**: 用户想要学习计划 → 调用 PathAgent 规划路径
- **ask_question**: 用户提了学习问题 → 调用 TutorAgent 答疑
- **assessment**: 用户想做测试/评估 → 调用 AssessmentAgent

## 输出格式
只输出以下 JSON，不要其他文字：
```json
{
  "intent": "build_profile|generate_resources|plan_path|ask_question|assessment|chat",
  "response": "给用户的简短回复",
  "params": {
    "resource_types": ["doc", "mindmap"],
    "course_topic": "提取的课程主题",
    "tech_stack": "提取的技术栈"
  }
}
```

如果用户只是闲聊或意图不明确，intent 用 "chat"。"""


class Orchestrator(BaseAgent):
    """主编排智能体 — 理解意图、分发任务。"""

    def __init__(self):
        super().__init__(name="Orchestrator", system_prompt=ORCHESTRATOR_PROMPT)

    def analyze_intent(self, user_message: str) -> dict:
        """Analyze user message and return intent + params."""
        import json
        import re
        response = self.chat(user_message, temperature=0.3)
        text = response.strip()
        text = re.sub(r'^```(?:json)?\s*\n?', '', text)
        text = re.sub(r'\n?```\s*$', '', text)
        start = text.find('{')
        if start != -1:
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
                            break
        return {"intent": "chat", "response": response, "params": {}}
