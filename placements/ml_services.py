from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_resume_match(student_skills, job_skills):
    if not student_skills or not job_skills:
        return 0.0
    
    try:
        vectorizer = CountVectorizer().fit_transform([student_skills, job_skills])
        vectors = vectorizer.toarray()
        
        cos_sim = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
        return round(cos_sim * 100, 2)
    except ValueError:
        # Fallback to Jaccard-like set intersection if vocabulary is empty (e.g., only "C")
        student_set = set(student_skills.lower().split())
        job_set = set(job_skills.lower().split())
        if not job_set:
            return 0.0
        match_count = len(student_set.intersection(job_set))
        return round((match_count / len(job_set)) * 100, 2)
