# 과목 데이터를 정규화하여 비교 정확성을 높이는 함수
def normalize_subject(subject):
    return subject.strip().lower()

# Function to calculate similarity between mentor and mentee based on subjects
# Now returns similarity as a fraction of common subjects over total unique subjects
def calculate_similarity(mentor_subjects, mentee_subjects):
    # Normalize subjects (lowercase, strip whitespace)
    mentor_subjects = [normalize_subject(subject) for subject in mentor_subjects]
    mentee_subjects = [normalize_subject(subject) for subject in mentee_subjects]
    
    # Calculate similarity
    common_subjects = set(mentor_subjects) & set(mentee_subjects)
    total_subjects = set(mentor_subjects) | set(mentee_subjects)
    
    if len(total_subjects) == 0:
        return 0
    similarity = len(common_subjects) / len(total_subjects)  # Fraction of common to total subjects
    return round(similarity, 2)  # Round to two decimal places

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
    print(f"Data read from {file_path}: {data}")  # 확인을 위한 데이터 출력
    return data

# Function to match mentors and mentees based on similarity
def match_mentors_mentees(mentors, mentees):
    matches = []
    # First pass: Match based on similarity
    for mentor in mentors:
        best_match = None
        best_similarity = -1
        for mentee in mentees:
            if mentee['mentorCount'] == 0:  # Unmatched mentee
                similarity = calculate_similarity(mentor['subjects'], mentee['subjects'])
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = mentee
        if best_match:
            mentor['menteeCount'] += 1
            best_match['mentorCount'] += 1
            matches.append((mentor['name'], best_match['name'], best_similarity))

    # Second pass: Assign unmatched mentors to any mentee
    for mentor in mentors:
        if mentor['menteeCount'] == 0:  # Unmatched mentor
            for mentee in mentees:
                if mentee['mentorCount'] < 2:  # Mentee with fewer than 2 mentors
                    mentee['mentorCount'] += 1
                    mentor['menteeCount'] += 1
                    matches.append((mentor['name'], mentee['name'], 0))
                    break
    return matches

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
        f.write(f"Mentor: {match[0]} - Mentee: {match[1]} (Similarity: {match[2]})\n")

# Confirm result file writing
print("Result saved to result.txt")