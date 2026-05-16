import os
from dotenv import load_dotenv

load_dotenv()

GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "daily-digest:v1.0")

TOPICS = ["AI", "climate", "space", "cybersecurity"]

TOP_N = 10

REFRESH_HOUR = 7

# Keywords used to gate relevance — articles whose titles contain none of these are dropped
TOPIC_KEYWORDS: dict[str, list[str]] = {
    "AI": ["AI", "artificial intelligence", "machine learning", "LLM", "GPT",
           "neural", "chatbot", "Anthropic", "OpenAI", "Gemini", "deep learning",
           "generative", "foundation model"],
    "climate": ["climate", "warming", "carbon", "emissions", "renewable",
                "fossil fuel", "net zero", "greenhouse", "drought", "flood",
                "biodiversity", "deforestation", "sea level"],
    "space": ["space", "NASA", "SpaceX", "rocket", "satellite", "orbit",
              "Mars", "Moon", "asteroid", "telescope", "cosmos", "ISS",
              "launch", "astronaut", "galaxy", "exoplanet"],
    "cybersecurity": ["cybersecurity", "cyber", "hack", "breach", "ransomware",
                      "malware", "vulnerability", "phishing", "exploit",
                      "data leak", "zero-day", "encryption", "infosec"],
}

# Guardian API section filter per topic — narrows results significantly
TOPIC_GUARDIAN_SECTIONS: dict[str, str] = {
    "AI": "technology",
    "climate": "environment",
    "space": "science",
    "cybersecurity": "technology",
}

# Boolean search queries for Guardian — more precise than a bare topic name
TOPIC_GUARDIAN_QUERIES: dict[str, str] = {
    "AI": "artificial intelligence OR machine learning OR LLM OR generative AI",
    "climate": "climate change OR global warming OR carbon emissions OR net zero",
    "space": "space exploration OR NASA OR SpaceX OR rocket launch OR asteroid",
    "cybersecurity": "cybersecurity OR cyberattack OR data breach OR ransomware OR malware",
}

TRUSTED_DOMAINS = {
    "theguardian.com": 1.0,
    "arstechnica.com": 0.9,
    "reuters.com": 0.9,
    "bbc.com": 0.85,
    "apnews.com": 0.85,
    "wired.com": 0.8,
    "technologyreview.com": 0.8,
    "nature.com": 0.9,
    "scientificamerican.com": 0.85,
}

# Weights must sum to 1.0 — popularity weight is redistributed to recency/trust
# until Reddit is wired up; keep these as the intended long-term weights
SCORE_WEIGHTS = {
    "recency": 0.4,
    "trust": 0.3,
    "popularity": 0.3,
}
