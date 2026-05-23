from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_resume_match(student_skills, job_skills):
    if not student_skills or not job_skills:
        return 0.0
    
    vectorizer = CountVectorizer().fit_transform([student_skills, job_skills])
    vectors = vectorizer.toarray()
    
    cos_sim = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
    return round(cos_sim * 100, 2)
