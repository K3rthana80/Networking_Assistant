from backend.models.distilbert import classifier

CANDIDATE_LABELS = [
    "Artificial Intelligence",
    "Machine Learning",
    "Data Science",
    "Cyber Security",
    "Cloud Computing",
    "Software Development",
    "Blockchain",
    "Healthcare",
    "Finance",
    "Business",
    "Marketing",
    "Entrepreneurship",
    "Education",
    "Networking",
    "Innovation",
    "Research",
    "Technology",
    "Startups",
    "Leadership",
    "Career Development"
]


def analyze_event(event_description: str):

    if not event_description.strip():
        return []

    try:
        result = classifier(
            event_description,
            CANDIDATE_LABELS,
            multi_label=True
        )

        themes = []

        for label, score in zip(result["labels"], result["scores"]):
            if score >= 0.30:
                themes.append({
                    "theme": label,
                    "confidence": round(score, 3)
                })

        return themes

    except Exception as e:
        return [
            {
                "theme": "Analysis Error",
                "confidence": 0.0,
                "error": str(e)
            }
        ]