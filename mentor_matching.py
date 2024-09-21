
def get_grade_level(student_id):
    level_prefix = student_id[:2]  # Extract the first two characters
    if level_prefix == "MS":
        level = "MS"
    elif level_prefix == "HS":
        level = "HS"
    else:
        print(f"Warning: Unexpected student ID format {student_id}, defaulting to HS")
        level = "HS"
    
    try:
        year = int(student_id[2:4])  # Extract the next two digits as year
    except ValueError:
        print(f"Error: Invalid year in student ID {student_id}, defaulting to year 1")
        year = 1
    
    return level, year

# Helper function to normalize subjects by stripping whitespace and converting to lowercase
def normalize_subject(subject):
    return subject.strip().lower()

# Function to calculate similarity between mentor and mentee based on subjects
def calculate_similarity(mentor_subjects, mentee_subjects):
    # Normalize subjects for accurate comparison
    mentor_subjects = [normalize_subject(subject) for subject in mentor_subjects]
    mentee_subjects = [normalize_subject(subject) for subject in mentee_subjects]
    
    # Find the common subjects and calculate similarity
    common_subjects = set(mentor_subjects) & set(mentee_subjects)
    total_subjects = set(mentor_subjects) | set(mentee_subjects)
    
    # If no subjects are present, return 0
    if len(total_subjects) == 0:
        return 0
    
    # Calculate similarity as the ratio of common subjects to total subjects
    similarity = len(common_subjects) / len(total_subjects)
    
    return round(similarity, 2)  # Return the similarity rounded to 2 decimal places

def match_mentors_mentees(mentors, mentees):
    matches = []
    
    # First pass: Match based on similarity > 0 and grade level compatibility
    for mentor in mentors:
        mentor_level, mentor_year = get_grade_level(mentor['id'])
        best_match = None
        best_similarity = -1
        for mentee in mentees:
            mentee_level, mentee_year = get_grade_level(mentee['id'])
            
            # Match only if mentor and mentee are from compatible levels
            if (mentor_level == "HS" and mentee_level in ["HS", "MS"]) or (mentor_level == mentee_level and mentor_year > mentee_year):
                if mentee['mentorCount'] == 0 and mentor_year != mentee_year:  # Unmatched mentee and no same-year matches
                    similarity = calculate_similarity(mentor['subjects'], mentee['subjects'])
                    if similarity > 0 and similarity > best_similarity:
                        best_similarity = similarity
                        best_match = mentee
        if best_match:
            mentor['menteeCount'] += 1
            best_match['mentorCount'] += 1
            matches.append((mentor['name'], f"{mentor_level}{mentor_year}", best_match['name'], f"{mentee_level}{mentee_year}", best_similarity))

    # Second pass: Assign unmatched mentors with any mentee, even if similarity is 0
    for mentor in mentors:
        if mentor['menteeCount'] == 0:  # Unmatched mentor
            mentor_level, mentor_year = get_grade_level(mentor['id'])
            for mentee in mentees:
                mentee_level, mentee_year = get_grade_level(mentee['id'])
                if (mentor_level == "HS" and mentee_level in ["HS", "MS"]) or (mentor_level == mentee_level and mentor_year > mentee_year):
                    if mentee['mentorCount'] < 2 and mentor_year != mentee_year:  # Mentee with fewer than 2 mentors
                        similarity = calculate_similarity(mentor['subjects'], mentee['subjects'])
                        mentor['menteeCount'] += 1
                        mentee['mentorCount'] += 1
                        matches.append((mentor['name'], f"{mentor_level}{mentor_year}", mentee['name'], f"{mentee_level}{mentee_year}", similarity))
                        break

    # Third pass: Ensure every mentee is matched (even if no similarity)
    unmatched_mentees = [mentee for mentee in mentees if mentee['mentorCount'] == 0]
    for mentee in unmatched_mentees:
        mentee_level, mentee_year = get_grade_level(mentee['id'])
        for mentor in mentors:
            mentor_level, mentor_year = get_grade_level(mentor['id'])
            if mentor['menteeCount'] < 2 and ((mentor_level == "HS" and mentee_level in ["HS", "MS"]) or (mentor_level == mentee_level and mentor_year > mentee_year)):
                similarity = calculate_similarity(mentor['subjects'], mentee['subjects'])
                mentor['menteeCount'] += 1
                mentee['mentorCount'] += 1
                matches.append((mentor['name'], f"{mentor_level}{mentor_year}", mentee['name'], f"{mentee_level}{mentee_year}", similarity))
                break

    return matches

# Function to read and parse mentor and mentee data from text files
def read_data(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:
                parts = line.split('\t')
                data.append({
                    'id': parts[0],
                    'name': parts[1],
                    'category': parts[2],
                    'subjects': parts[3].split(', '),
                    'menteeCount': 0 if 'mentors' in file_path else None,
                    'mentorCount': 0 if 'mentees' in file_path else None
                })
    return data

# Load mentors and mentees from the text files
mentors = read_data('mentors.txt')
mentees = read_data('mentees.txt')

# Perform the matching
matches = match_mentors_mentees(mentors, mentees)

# Check the matching result
print(f"Matches: {matches}")  # 매칭 결과 출력

# Save the results to result.txt
with open("result.txt", "w", encoding="utf-8") as f:
    for match in matches:
        f.write(f"Mentor: {match[0]} ({match[1]}) - Mentee: {match[2]} ({match[3]}) (Similarity: {match[4]})\n")

# Confirm result file writing
print("Result saved to result.txt")