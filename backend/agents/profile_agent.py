import json
from backend.agents.base import BaseAgent

PROFILE_AGENT_PROMPT = """你是一位专业的**学习画像分析师**。你的任务是通过自然对话了解学生的学习情况，并从对话中提取6个维度的学习画像。

## 你的工作方式
1. **首先倾听学生的自由表述**，不要急于提问。让学生先充分描述自己的学习情况
2. 听完学生的描述后，判断信息是否覆盖了6个维度的核心内容。如果学生的描述已经足够丰富，**直接生成画像JSON**，不要再追问
3. 只有当某些维度**确实缺乏信息**时，才**每次追问1个关键问题**。不要一次性抛出多个问题
4. 当你收集到足够信息后，立即输出完整的 JSON 格式学习画像
5. 画像必须包含6个维度，缺少信息的维度根据对话内容合理推断

## 6个维度说明

1. **knowledge_base（知识基础）**:
   - level: "beginner" | "intermediate" | "advanced"
   - mastered_topics: 已掌握的知识点列表
   - weak_points: 薄弱知识点列表
   - target_topics: 想学习的目标知识点

2. **cognitive_style（认知风格）**:
   - primary_style: "visual" | "verbal" | "logical" | "hands_on" | "social"
   - score: 0.0-1.0 置信度
   - description: 简短描述

3. **learning_pace（学习节奏）**:
   - speed: "slow_and_deep" | "moderate" | "fast"
   - attention_span: "short" | "medium" | "long"
   - weekly_hours: 每周可投入学习时间（小时）

4. **preferred_modalities（偏好学习模态）**:
   - modalities: 从 ["text", "video", "audio", "interactive", "diagram", "code_practice"] 中选择
   - reason: 选择原因

5. **error_patterns（易错模式）**:
   - patterns: [{"topic": "知识点", "error_type": "概念混淆"|"计算错误"|"逻辑错误"|"记忆遗忘", "frequency": "high"|"medium"|"low"}]

6. **motivation_factors（学习动机）**:
   - primary_goal: 主要学习目标
   - intrinsic_motivation: 内在动机（如兴趣、成就感）
   - extrinsic_motivation: 外在动机（如考试、就业）

## 输出格式
当你有足够信息后，只输出以下JSON，不要输出其他文字：
```json
{
  "knowledge_base": {...},
  "cognitive_style": {...},
  "learning_pace": {...},
  "preferred_modalities": {...},
  "error_patterns": {...},
  "motivation_factors": {...},
  "summary": "一句话总结学生画像"
}
```

如果信息不足需要追问，则用自然语言回复，不要输出 JSON。"""


class ProfileAgent(BaseAgent):
    """学习画像分析师 — 通过对话构建学生画像。"""

    def __init__(self):
        super().__init__(name="ProfileAgent", system_prompt=PROFILE_AGENT_PROMPT)

    def build_profile(self, user_input: str, conversation_history: list[dict] = None) -> dict:
        """Analyze user input and conversation history, return profile dict or follow-up question.

        Returns:
            {"status": "need_more_info", "message": "追问内容"}
            {"status": "complete", "profile": {...}}
        """
        history = conversation_history or []
        history.append({"role": "user", "content": user_input})

        # If input is structured onboarding data, force JSON output with a stronger prompt
        is_onboarding = '直接生成学习画像JSON' in user_input or '[学习画像信息]' in user_input

        if is_onboarding:
            response = self.chat(user_input, temperature=0.3)
        else:
            response = self.chat_with_history(history)

        # Try to parse JSON from response
        json_str = self._extract_json(response)
        if json_str:
            try:
                profile = json.loads(json_str)
                return {"status": "complete", "profile": profile}
            except json.JSONDecodeError:
                pass

        # If onboarding input didn't produce JSON, retry with stronger prompt
        if is_onboarding:
            retry_prompt = f"""你必须只输出JSON，不要任何解释或追问。根据以下信息生成学习画像：
{user_input}

直接输出JSON："""
            response = self.chat(retry_prompt, temperature=0.1)
            json_str = self._extract_json(response)
            if json_str:
                try:
                    profile = json.loads(json_str)
                    return {"status": "complete", "profile": profile}
                except json.JSONDecodeError:
                    pass

        return {"status": "need_more_info", "message": response}

    def build_profile_stream(self, user_input: str, conversation_history: list[dict] = None):
        """Streaming version — yields tokens, last yield is the result dict."""
        history = conversation_history or []
        history.append({"role": "user", "content": user_input})

        full_response = ""
        for token in self.chat_with_history_stream(history):
            full_response += token
            yield token

        json_str = self._extract_json(full_response)
        if json_str:
            try:
                profile = json.loads(json_str)
                yield {"status": "complete", "profile": profile}
                return
            except json.JSONDecodeError:
                pass

        yield {"status": "need_more_info", "message": full_response}

    async def build_profile_stream_async(self, user_input: str, conversation_history: list[dict] = None):
        """Async streaming version — yields tokens, last yield is the result dict."""
        history = conversation_history or []
        history.append({"role": "user", "content": user_input})

        full_response = ""
        async for token in self.chat_with_history_stream_async(history):
            full_response += token
            yield token

        json_str = self._extract_json(full_response)
        if json_str:
            try:
                profile = json.loads(json_str)
                yield {"status": "complete", "profile": profile}
                return
            except json.JSONDecodeError:
                pass

        yield {"status": "need_more_info", "message": full_response}

    def update_profile(self, existing_profile: dict, new_info: str) -> dict:
        """Update an existing profile with new information.

        Returns (updated_profile, raw_response) — raw_response is for debugging when JSON parse fails.
        """
        import logging
        logger = logging.getLogger(__name__)

        prompt = f"""现有学生画像：
{json.dumps(existing_profile, ensure_ascii=False, indent=2)}

新的信息：{new_info}

请根据新信息更新画像JSON。保持6个维度结构不变，只更新相关字段。只输出更新后的JSON。"""

        response = self.chat(prompt, temperature=0.5)
        json_str = self._extract_json(response)
        if json_str:
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning(f"[ProfileAgent] JSON parse failed for update, raw response: {response[:500]}")
        else:
            logger.warning(f"[ProfileAgent] No JSON found in update response: {response[:500]}")
        return existing_profile

    @staticmethod
    def _extract_json(text: str):  # -> str | None (Python 3.10+)
        """Extract JSON object from LLM response, even if wrapped in markdown or prefixed with text."""
        import re
        text = text.strip()
        # Remove markdown code block wrappers
        text = re.sub(r'^```(?:json)?\s*\n?', '', text)
        text = re.sub(r'\n?```\s*$', '', text)
        # Find the outermost JSON object
        start = text.find('{')
        if start == -1:
            return None
        # Track braces to find matching closing brace
        depth = 0
        for i in range(start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
        return None
