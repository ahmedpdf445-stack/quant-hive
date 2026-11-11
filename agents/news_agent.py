"""Optional news context analysis using the Groq chat-completions API."""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class NewsAgent:
    """Summarize publicly available context when a Groq key is configured."""

    def analyse(self, symbol: str) -> str:
        """Request a concise, non-actionable news context summary from Groq."""
        try:
            if not isinstance(symbol, str) or not symbol.strip():
                raise ValueError("symbol must be a non-empty string")
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                logger.info("GROQ_API_KEY is not configured; skipping news analysis")
                return "News analysis unavailable: GROQ_API_KEY is not configured."
            from groq import Groq

            client = Groq(api_key=api_key)
            response: Any = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Provide a brief, balanced market-news context summary. "
                            "Do not make price predictions or recommendations."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Summarize relevant recent context for {symbol.strip().upper()}.",
                    },
                ],
                temperature=0.2,
                max_tokens=300,
            )
            content = response.choices[0].message.content
            summary = str(content).strip() if content else "No news summary was returned."
            logger.info("News context generated for %s", symbol)
            return summary
        except Exception as exc:
            logger.exception("News analysis failed for %r", symbol)
            return f"News analysis unavailable: {type(exc).__name__}."
