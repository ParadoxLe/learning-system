from backend.agents.base import BaseAgent

EXERCISE_AGENT_PROMPT = """你是一位**题库设计专家**。你擅长根据学生的知识水平和易错模式，设计针对性的练习题。

## 你的任务
根据学生画像和知识点，生成一套个性化练习题。

## 输出要求
生成以下4种类型的题目，每种至少2道：
1. **概念辨析题**（选择题）— 考察概念理解
2. **计算应用题** — 考察公式应用能力
3. **案例分析题** — 考察综合分析能力
4. **易错陷阱题** — 针对学生的 error_patterns 设计

每道题包含：
- 题目描述
- 参考答案/解析
- 难度等级 (easy/medium/hard)
- 对应知识点

用 Markdown 格式输出，包含分隔线区分不同类型。"""


class ExerciseAgent(BaseAgent):
    """练习题生成智能体。"""

    def __init__(self):
        super().__init__(name="ExerciseAgent", system_prompt=EXERCISE_AGENT_PROMPT)

    def generate(self, profile: dict, topic: str, difficulty: str = "medium") -> str:
        """Generate personalized exercises."""
        error_patterns = profile.get("error_patterns", {})
        knowledge = profile.get("knowledge_base", {})

        prompt = f"""学生画像：{profile}
知识点主题：{topic}
难度偏好：{difficulty}

请针对此学生的知识薄弱点({knowledge.get('weak_points', [])})和易错模式({error_patterns})，
生成一套个性化练习题。"""
        return self.chat(prompt, temperature=0.8)
