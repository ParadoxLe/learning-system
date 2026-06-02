from backend.agents.base import BaseAgent

TUTOR_AGENT_PROMPT = """你是一位**智能辅导老师**。你擅长用多种方式解答学生的问题，帮助学生真正理解知识点。

## 你的任务
根据学生的画像和学习问题，提供个性化的多模态解答。

## 解答方式（根据问题类型选择）
1. **文字解答**：清晰的分步解释
2. **图解说明**：用 ASCII 图、流程图或文字描述可视化
3. **类比讲解**：用生活中的例子类比
4. **视频讲解建议**：如果适合，给出短视频讲解要点

## 输出格式
用 Markdown 输出，包含：

### 📝 问题分析
- 问题涉及的知识点
- 可能的理解误区

### 📖 详细解答
- 分步讲解
- 关键公式/概念

### 🎨 图解说明
- 流程图/示意图描述
- 关系图

### 💡 举一反三
- 类似问题举例
- 变式练习

### 🔗 相关知识
- 前置知识回顾
- 后续知识预览

根据学生的 cognitive_style 调整讲解方式：
- visual → 重点放在图解说明
- verbal → 重点放在文字类比
- logical → 重点放在推导步骤
- hands_on → 给一个可操作的例子"""


class TutorAgent(BaseAgent):
    """智能辅导智能体 — 多模态答疑。"""

    def __init__(self):
        super().__init__(name="TutorAgent", system_prompt=TUTOR_AGENT_PROMPT)

    def answer(self, question: str, profile: dict, context: str = "") -> str:
        """Answer a student's question with personalized explanation."""
        prompt = self._build_prompt(question, profile, context)
        return self.chat(prompt, temperature=0.7)

    def answer_stream(self, question: str, profile: dict, context: str = ""):
        """Stream a personalized answer token by token."""
        prompt = self._build_prompt(question, profile, context)
        yield from self.chat_stream(prompt, temperature=0.7)

    def _build_prompt(self, question: str, profile: dict, context: str = "") -> str:
        return f"""学生画像：{profile}
课程上下文：{context or '通用学习场景'}

学生提问：{question}

请为该学生提供个性化解答。"""
