from dataclasses import dataclass


@dataclass(frozen=True)
class FeedSource:
    name: str
    url: str
    category: str


SOURCES = [
    FeedSource("OpenAI", "https://openai.com/news/rss.xml", "industry"),
    FeedSource("Anthropic", "https://www.anthropic.com/rss.xml", "industry"),
    FeedSource("Google AI", "https://blog.google/technology/ai/rss/", "industry"),
    FeedSource("Google DeepMind", "https://deepmind.google/blog/rss.xml", "research"),
    FeedSource("Microsoft Research", "https://www.microsoft.com/en-us/research/feed/", "research"),
    FeedSource("Hugging Face", "https://huggingface.co/blog/feed.xml", "open-source"),
    FeedSource("Meta AI", "https://ai.meta.com/blog/rss/", "industry"),
    FeedSource("NVIDIA AI", "https://blogs.nvidia.com/feed/", "industry"),
    FeedSource("arXiv AI", "https://export.arxiv.org/rss/cs.AI", "research"),
    FeedSource("arXiv ML", "https://export.arxiv.org/rss/cs.LG", "research"),
    FeedSource("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/", "news"),
    FeedSource("VentureBeat AI", "https://venturebeat.com/category/ai/feed/", "news"),
]
