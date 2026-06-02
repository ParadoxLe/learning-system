from backend.agents.base import BaseAgent

DOC_AGENT_PROMPT = """你是一位**课程文档撰写专家**。你擅长将复杂的知识点转化为结构清晰、易于理解的课程讲解文档。

## 你的任务
根据学生画像和课程信息，生成一份个性化的课程讲解文档。

## 输出要求
1. 用 Markdown 格式输出
2. 必须包含：
   - 标题和概述
   - 学习目标（3-5条）
   - 核心概念讲解（配合示例）
   - 重点难点标注
   - 知识关联图（用文字描述）
   - 课后思考题（2-3题）
   - 推荐学习时长
3. 根据学生的 knowledge_base 调整难度
4. 根据学生的 cognitive_style 调整讲解方式
   - visual型：多用图表、对比表格
   - verbal型：多用文字描述、类比
   - logical型：多展示推导过程、逻辑链
   - hands_on型：多穿插实操练习

直接输出 Markdown 文档，不要额外的解释。"""


class DocAgent(BaseAgent):
    """课程文档生成智能体。"""

    def __init__(self):
        super().__init__(name="DocAgent", system_prompt=DOC_AGENT_PROMPT)

    def generate(self, profile: dict, course_info: str) -> str:
        """Generate a personalized course document."""
        prompt = f"""学生画像：
{profile}

课程/知识点信息：
{course_info}

请为此学生生成个性化的课程讲解文档。"""
        return self.chat(prompt, temperature=0.7)
