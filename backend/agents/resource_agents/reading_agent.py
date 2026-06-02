from backend.agents.base import BaseAgent

READING_AGENT_PROMPT = """你是一位**拓展阅读推荐师**。你擅长根据学生的知识背景和学习目标，推荐合适的拓展阅读材料。

## 你的任务
根据学生画像和主题，推荐拓展阅读材料。

## 输出要求
用 Markdown 格式输出，包含以下内容：
1. **核心必读**（3篇）：经典教材/论文章节
   - 标题
   - 来源/作者
   - 推荐理由（与学生的知识薄弱点关联）
   - 预计阅读时间
2. **进阶阅读**（3篇）：深入理解的前沿材料
   - 同上结构
3. **视频/公开课推荐**（2个）：适合的在线资源
   - 平台 + 课程名
   - 推荐理由
4. **阅读路线建议**：按什么顺序读，哪些可以跳过

根据学生的 preferred_modalities 调整推荐类型比重。"""


class ReadingAgent(BaseAgent):
    """拓展阅读推荐智能体。"""

    def __init__(self):
        super().__init__(name="ReadingAgent", system_prompt=READING_AGENT_PROMPT)

    def generate(self, profile: dict, topic: str) -> str:
        """Generate reading recommendations."""
        prompt = f"""学生画像：{profile}
主题：{topic}

请为此学生推荐个性化的拓展阅读材料。"""
        return self.chat(prompt, temperature=0.7)
