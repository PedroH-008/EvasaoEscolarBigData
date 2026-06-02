DROP TABLE IF EXISTS interventions;
DROP TABLE IF EXISTS digital_engagement;
DROP TABLE IF EXISTS grades;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS socioeconomic;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS classes;
DROP TABLE IF EXISTS guardians;
DROP TABLE IF EXISTS students;

CREATE TABLE students (
    student_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    gender TEXT NOT NULL,
    race_ethnicity TEXT NOT NULL,
    neighborhood TEXT NOT NULL,
    distance_km REAL NOT NULL,
    transport_access INTEGER NOT NULL,
    special_needs INTEGER NOT NULL
);

CREATE TABLE guardians (
    guardian_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    guardian_name TEXT NOT NULL,
    relationship TEXT NOT NULL,
    education_level TEXT NOT NULL,
    employment_status TEXT NOT NULL,
    phone_valid INTEGER NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE classes (
    class_id INTEGER PRIMARY KEY,
    grade_level TEXT NOT NULL,
    shift TEXT NOT NULL,
    room TEXT NOT NULL,
    school_year INTEGER NOT NULL
);

CREATE TABLE subjects (
    subject_id INTEGER PRIMARY KEY,
    subject_name TEXT NOT NULL,
    workload_hours INTEGER NOT NULL
);

CREATE TABLE teachers (
    teacher_id INTEGER PRIMARY KEY,
    teacher_name TEXT NOT NULL,
    subject_id INTEGER NOT NULL,
    experience_years INTEGER NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

CREATE TABLE enrollments (
    enrollment_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    enrollment_date TEXT NOT NULL,
    status TEXT NOT NULL,
    dropout_date TEXT,
    dropout_reason TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (class_id) REFERENCES classes(class_id)
);

CREATE TABLE socioeconomic (
    student_id INTEGER PRIMARY KEY,
    family_income_brl REAL NOT NULL,
    household_size INTEGER NOT NULL,
    internet_access INTEGER NOT NULL,
    receives_social_benefit INTEGER NOT NULL,
    works_after_school INTEGER NOT NULL,
    food_insecurity_score INTEGER NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE attendance (
    attendance_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    month INTEGER NOT NULL,
    school_year INTEGER NOT NULL,
    classes_offered INTEGER NOT NULL,
    absences INTEGER NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

CREATE TABLE grades (
    grade_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    bimester INTEGER NOT NULL,
    school_year INTEGER NOT NULL,
    grade REAL NOT NULL,
    recovery_exam INTEGER NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

CREATE TABLE digital_engagement (
    engagement_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    month INTEGER NOT NULL,
    school_year INTEGER NOT NULL,
    platform_logins INTEGER NOT NULL,
    homework_submitted INTEGER NOT NULL,
    messages_to_teacher INTEGER NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE interventions (
    intervention_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    intervention_date TEXT NOT NULL,
    intervention_type TEXT NOT NULL,
    responsible_team TEXT NOT NULL,
    result TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);
