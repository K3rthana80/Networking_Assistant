from backend.models.wiki_client import wiki


def verify_topic(topic: str):
    """
    Verify a topic using Wikipedia.

    Returns:
    {
        verified: bool,
        topic: str,
        summary: str
    }
    """

    topic = topic.strip()

    if not topic:
        return {
            "verified": False,
            "topic": "",
            "summary": "No topic provided."
        }

    try:
        page = wiki.page(topic)

        if page.exists():

            summary = page.summary

            # Keep only the first 3 sentences
            sentences = summary.split(". ")
            short_summary = ". ".join(sentences[:3])

            if not short_summary.endswith("."):
                short_summary += "."

            return {
                "verified": True,
                "topic": topic,
                "summary": short_summary
            }

        return {
            "verified": False,
            "topic": topic,
            "summary": "No verified Wikipedia article found."
        }

    except Exception as e:
        return {
            "verified": False,
            "topic": topic,
            "summary": str(e)
        }