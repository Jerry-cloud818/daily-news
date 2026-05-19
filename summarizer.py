import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class Summarizer:
    """AI摘要生成器，支持多种后端"""

    def __init__(self, config: dict):
        self.backend = config.get('summarizer_backend', 'local')
        self.api_key = config.get('api_key', '')
        self.api_base = config.get('api_base', '')
        self.model = config.get('model', '')

    def summarize(self, title: str, content: str) -> str:
        """生成摘要"""
        if self.backend == 'claude':
            return self._summarize_claude(title, content)
        elif self.backend == 'openai':
            return self._summarize_openai(title, content)
        else:
            return self._summarize_local(title, content)

    def _summarize_claude(self, title: str, content: str) -> str:
        """使用Claude API生成摘要"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)

            prompt = f"""请为以下新闻写一段50-100字的中文摘要，简洁明了地概括核心内容和关键信息。

标题：{title}
正文：{content[:2000]}

只输出摘要内容，不要加任何前缀或标签。"""

            message = client.messages.create(
                model=self.model or "claude-sonnet-4-6",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text.strip()
        except Exception as e:
            logger.warning(f"Claude摘要生成失败: {e}")
            return self._summarize_local(title, content)

    def _summarize_openai(self, title: str, content: str) -> str:
        """使用OpenAI兼容API生成摘要（DeepSeek/Moonshot/通义千问等）"""
        try:
            import requests

            prompt = f"""请为以下新闻写一段50-100字的中文摘要，简洁明了地概括核心内容和关键信息。

标题：{title}
正文：{content[:2000]}

只输出摘要内容，不要加任何前缀或标签。"""

            resp = requests.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model or "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.3,
                },
                timeout=30,
            )
            data = resp.json()
            return data['choices'][0]['message']['content'].strip()
        except Exception as e:
            logger.warning(f"OpenAI兼容API摘要生成失败: {e}")
            return self._summarize_local(title, content)

    def _summarize_local(self, title: str, content: str) -> str:
        """本地提取式摘要（不需要API）"""
        if not content:
            return f"【{title}】- 暂无更多详情，请点击链接查看原文。"

        # 分句
        sentences = re.split(r'[。！？\n]', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        if not sentences:
            return content[:150]

        # 选取前3个最有信息量的句子
        title_keywords = set(re.findall(r'[一-鿿]{2,}', title))
        scored = []
        for i, sent in enumerate(sentences[:20]):
            score = 0
            # 标题关键词出现加分
            for kw in title_keywords:
                if kw in sent:
                    score += 3
            # 数字出现加分（通常有具体数据）
            if re.search(r'\d+', sent):
                score += 1
            # 适当长度加分
            if 20 < len(sent) < 200:
                score += 1
            # 靠前的句子加分
            score += max(0, 5 - i)
            scored.append((score, i, sent))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_sentences = sorted(scored[:3], key=lambda x: x[1])
        summary = '。'.join([s[2] for s in top_sentences])

        return summary + '。' if not summary.endswith('。') else summary
