from dataclasses import dataclass


@dataclass(frozen=True)
class FeedSource:
    name: str
    url: str
    category: str
    authority: float = 1.0


# Authority is intentionally source-level, not story-level: primary sources
# should generally outrank commentary and aggregators before the LLM sees them.
SOURCES = [
    FeedSource("OpenAI", "https://openai.com/news/rss.xml", "industry", 1.00),
    FeedSource("Anthropic", "https://www.anthropic.com/rss.xml", "industry", 1.00),
    FeedSource("Google AI", "https://blog.google/technology/ai/rss/", "industry", 1.00),
    FeedSource("Google DeepMind", "https://deepmind.google/blog/rss.xml", "research", 1.00),
    FeedSource("Microsoft Research", "https://www.microsoft.com/en-us/research/feed/", "research", 0.95),
    FeedSource("Hugging Face", "https://huggingface.co/blog/feed.xml", "open-source", 0.95),
    FeedSource("Meta AI", "https://ai.meta.com/blog/rss/", "industry", 0.95),
    FeedSource("NVIDIA AI", "https://blogs.nvidia.com/feed/", "industry", 0.95),
    FeedSource("arXiv AI", "https://export.arxiv.org/rss/cs.AI", "research", 0.90),
    FeedSource("arXiv ML", "https://export.arxiv.org/rss/cs.LG", "research", 0.90),
    FeedSource("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/", "news", 0.75),
    FeedSource("VentureBeat AI", "https://venturebeat.com/category/ai/feed/", "news", 0.70),
]
