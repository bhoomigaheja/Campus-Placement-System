def calculate_resume_match(student_skills, job_skills):
    if not student_skills or not job_skills:
        return 0.0
    
    student_set = set(student_skills.lower().split())
    job_set = set(job_skills.lower().split())
    
    if not job_set:
        return 0.0
        
    match_count = len(student_set.intersection(job_set))
    return round((match_count / len(job_set)) * 100, 2)
