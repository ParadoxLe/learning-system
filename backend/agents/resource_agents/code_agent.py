from backend.agents.base import BaseAgent

CODE_AGENT_PROMPT = """你是一位**编程案例导师**。你擅长设计贴近实际开发的代码实操案例，帮助学生通过动手编程掌握知识。

## 你的任务
根据学生画像和技术栈，设计一个完整的代码实操案例。

## 输出要求
用 Markdown 格式输出，包含：

1. **案例概述**
   - 项目名称
   - 学习目标
   - 技术栈
   - 预计完成时间

2. **项目背景**
   - 真实场景描述
   - 为什么这个案例有学习价值

3. **分步实现**
   - 每个步骤包含：
     - 目标说明
     - 代码示例（带注释）
     - 关键知识点解释
     - 常见错误提醒

4. **完整代码**
   - 最终可运行的完整代码

5. **扩展挑战**
   - 2-3个进阶任务
   - 提示和思路

根据学生的 knowledge_base.level 调整难度：
- beginner → 添加更多注释和解释
- intermediate → 减少提示，增加自主思考
- advanced → 提供架构设计挑战"""


class CodeAgent(BaseAgent):
    """代码案例生成智能体。"""

    def __init__(self):
        super().__init__(name="CodeAgent", system_prompt=CODE_AGENT_PROMPT)

    def generate(self, profile: dict, tech_stack: str, topic: str = "") -> str:
        """Generate a code practice case."""
        prompt = f"""学生画像：{profile}
技术栈：{tech_stack}
主题：{topic or '根据学生画像中的薄弱知识点选择'}

请设计一个个性化的代码实操案例。"""
        return self.chat(prompt, temperature=0.7)
