import cv2
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import IMAGE_WEIGHT, TEXT_WEIGHT


def image_similarity(path1: str, path2: str) -> float:
    """Calculate image similarity using OpenCV histogram comparison."""
    try:
        img1 = cv2.imread(path1)
        img2 = cv2.imread(path2)
        if img1 is None or img2 is None:
            return 0.0

        # Resize to same dimensions for fair comparison
        img1 = cv2.resize(img1, (256, 256))
        img2 = cv2.resize(img2, (256, 256))

        # Convert to HSV for better color comparison
        hsv1 = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)
        hsv2 = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)

        # Calculate histograms
        hist1 = cv2.calcHist([hsv1], [0, 1, 2], None, [8, 8, 8], [0, 180, 0, 256, 0, 256])
        hist2 = cv2.calcHist([hsv2], [0, 1, 2], None, [8, 8, 8], [0, 180, 0, 256, 0, 256])

        # Normalize
        cv2.normalize(hist1, hist1)
        cv2.normalize(hist2, hist2)

        # Compare using correlation method
        score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        return max(0.0, min(1.0, score))
    except Exception:
        return 0.0


def text_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity using TF-IDF and cosine similarity."""
    try:
        if not text1.strip() or not text2.strip():
            return 0.0

        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return max(0.0, min(1.0, float(score)))
    except Exception:
        return 0.0


def combined_score(img_sim: float, txt_sim: float) -> float:
    """Calculate weighted combined similarity score."""
    return round(IMAGE_WEIGHT * img_sim + TEXT_WEIGHT * txt_sim, 4)
