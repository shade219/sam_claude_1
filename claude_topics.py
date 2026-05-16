import os
import anthropic
from pydantic import BaseModel


class TopicConfig(BaseModel):
    keywords: list[str]
    guardian_section: str  # empty string if none fits
    guardian_query: str


def generate_topic_config(topic: str) -> TopicConfig:
    """Call Claude to produce keywords and Guardian search config for a topic."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is not set")

    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.parse(
        model="claude-opus-4-7",
        max_tokens=1024,
        system=(
            "You generate search configuration for a news digest app. "
            "Given a topic name, produce:\n"
            "1. keywords: 10-15 keywords/phrases that would appear in relevant article titles\n"
            "2. guardian_section: the best-matching Guardian API section from this exact list: "
            "'technology', 'science', 'environment', 'world', 'business', 'culture', 'sport', "
            "'politics', 'society', 'film', 'music', 'books' — use empty string if none fits\n"
            "3. guardian_query: a boolean search query using OR operators for the Guardian API, "
            "e.g. 'term1 OR term2 OR term3'"
        ),
        messages=[
            {"role": "user", "content": f"Generate search configuration for the news topic: {topic}"}
        ],
        output_format=TopicConfig,
    )
    return response.parsed_output
