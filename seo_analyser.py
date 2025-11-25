import nltk
from sklearn.feature_extraction.text import TfidfVectorizer

def seo_recommendations(industry):
    keywords = {
        "tech": ["innovation", "cloud", "AI", "scalable"],
        "design": ["UX", "responsive", "aesthetic", "branding"]
    }
    return {
        "recommended_keywords": keywords.get(industry.lower(), ["portfolio", "professional"]),
        "meta_tags": ["title", "description", "keywords"]
    }