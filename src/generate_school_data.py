import argparse
import csv
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRONZE = ROOT / "data" / "bronze"
DB_PATH = ROOT / "data" / "escola_evasao.db"
SCHEMA_PATH = ROOT / "sql" / "schema.sql"

FIRST_NAMES = [
    "Ana", "Beatriz", "Bruno", "Camila", "Carlos", "Daniel", "Davi", "Eduarda",
    "Fernanda", "Gabriel", "Guilherme", "Isabela", "Joao", "Julia", "Larissa",
    "Leticia", "Lucas", "Luana", "Marcos", "Maria", "Matheus", "Pedro", "Rafaela",
    "Rafael", "Sofia", "Thiago", "Vitoria", "Yasmin"
]
LAST_NAMES = [
    "Almeida", "Araujo", "Barbosa", "Batista", "Carvalho", "Costa", "Ferreira",
    "Gomes", "Lima", "Melo", "Nascimento", "Oliveira", "Pereira", "Ribeiro",
    "Rocha", "Santana", "Santos", "Silva", "Souza", "Teixeira"
]
NEIGHBORHOODS = [
    "Centro", "Farolandia", "Siqueira Campos", "Santos Dumont", "Atalaia",
    "Santa Maria", "Bugio", "Jardins", "Industrial", "Lamarão"
]
SUBJECTS = [
    ("Matematica", 120), ("Portugues", 120), ("Historia", 80), ("Geografia", 80),
    ("Biologia", 80), ("Fisica", 80), ("Quimica", 80), ("Ingles", 60)
]


def full_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)} {random.choice(LAST_NAMES)}"


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def write_csv(name, rows):
    rows = list(rows)
    if not rows:
        return
    path = BRONZE / f"{name}.csv"
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def dropout_probability(student, socio, avg_grade, absence_rate, engagement_rate):
    score = -3.1
    score += 3.0 * absence_rate
    score += 1.6 * max(0, 6.0 - avg_grade) / 6.0
    score += 0.9 if socio["works_after_school"] else 0
    score += 0.8 if not socio["internet_access"] else 0
    score += 0.6 if student["distance_km"] > 8 else 0
    score += 0.7 if not student["transport_access"] else 0
    score += 0.5 if socio["food_insecurity_score"] >= 4 else 0
    score -= 0.8 * engagement_rate
    return 1 / (1 + pow(2.71828, -score))


def generate(students_count, seed):
    random.seed(seed)
    BRONZE.mkdir(parents=True, exist_ok=True)

    subjects = [
        {"subject_id": i + 1, "subject_name": name, "workload_hours": hours}
        for i, (name, hours) in enumerate(SUBJECTS)
    ]
    teachers = [
        {
            "teacher_id": i + 1,
            "teacher_name": full_name(),
            "subject_id": subject["subject_id"],
            "experience_years": random.randint(2, 28),
        }
        for i, subject in enumerate(subjects)
    ]
    classes = []
    class_id = 1
    for grade in ["1 ano EM", "2 ano EM", "3 ano EM"]:
        for shift in ["Manha", "Tarde", "Noite"]:
            for room in ["A", "B"]:
                classes.append({
                    "class_id": class_id,
                    "grade_level": grade,
                    "shift": shift,
                    "room": f"{grade[0]}{room}-{shift[0]}",
                    "school_year": 2026,
                })
                class_id += 1

    students, guardians, enrollments, socioeconomic = [], [], [], []
    attendance, grades, engagement, interventions = [], [], [], []
    attendance_id = grade_id = engagement_id = intervention_id = 1

    for student_id in range(1, students_count + 1):
        age = random.choices([14, 15, 16, 17, 18, 19, 20], [12, 25, 25, 18, 10, 6, 4])[0]
        birth = date(2026 - age, random.randint(1, 12), random.randint(1, 28))
        neighborhood = random.choice(NEIGHBORHOODS)
        distance = round(random.triangular(0.4, 15.0, 4.5), 2)
        transport = 1 if random.random() > (0.18 if distance > 8 else 0.07) else 0
        special_needs = 1 if random.random() < 0.045 else 0
        student = {
            "student_id": student_id,
            "name": full_name(),
            "birth_date": birth.isoformat(),
            "gender": random.choice(["Feminino", "Masculino", "Outro"]),
            "race_ethnicity": random.choices(
                ["Parda", "Preta", "Branca", "Indigena", "Amarela"],
                [48, 16, 30, 3, 3],
            )[0],
            "neighborhood": neighborhood,
            "distance_km": distance,
            "transport_access": transport,
            "special_needs": special_needs,
        }
        students.append(student)

        guardians.append({
            "guardian_id": student_id,
            "student_id": student_id,
            "guardian_name": full_name(),
            "relationship": random.choice(["Mae", "Pai", "Avo", "Tio/Tia", "Responsavel legal"]),
            "education_level": random.choices(
                ["Fundamental incompleto", "Fundamental completo", "Medio completo", "Superior"],
                [35, 25, 32, 8],
            )[0],
            "employment_status": random.choices(
                ["Empregado", "Informal", "Desempregado", "Aposentado"],
                [42, 32, 20, 6],
            )[0],
            "phone_valid": 1 if random.random() > 0.12 else 0,
        })

        income = round(random.lognormvariate(8.15, 0.55), 2)
        socio = {
            "student_id": student_id,
            "family_income_brl": income,
            "household_size": random.randint(2, 8),
            "internet_access": 1 if random.random() > 0.23 else 0,
            "receives_social_benefit": 1 if income < 2200 or random.random() < 0.18 else 0,
            "works_after_school": 1 if random.random() < (0.25 if age >= 17 else 0.08) else 0,
            "food_insecurity_score": random.choices([1, 2, 3, 4, 5], [28, 26, 22, 15, 9])[0],
        }
        socioeconomic.append(socio)

        class_row = random.choice(classes)
        base_absence = random.uniform(0.02, 0.18)
        if socio["works_after_school"]:
            base_absence += random.uniform(0.04, 0.12)
        if not student["transport_access"]:
            base_absence += random.uniform(0.03, 0.10)
        if socio["food_insecurity_score"] >= 4:
            base_absence += random.uniform(0.02, 0.08)
        base_grade = random.normalvariate(7.1, 1.15)
        if socio["works_after_school"]:
            base_grade -= 0.45
        if not socio["internet_access"]:
            base_grade -= 0.35

        total_absences = total_classes = total_grades = 0
        logins_total = homework_total = 0

        for subject in subjects:
            subject_difficulty = 0.35 if subject["subject_name"] in ["Matematica", "Fisica", "Quimica"] else 0
            for month in range(2, 12):
                offered = random.randint(7, 11)
                absence_rate = clamp(random.normalvariate(base_absence, 0.035), 0, 0.65)
                absences = clamp(round(offered * absence_rate), 0, offered)
                attendance.append({
                    "attendance_id": attendance_id,
                    "student_id": student_id,
                    "subject_id": subject["subject_id"],
                    "month": month,
                    "school_year": 2026,
                    "classes_offered": offered,
                    "absences": absences,
                })
                attendance_id += 1
                total_absences += absences
                total_classes += offered

            for bimester in range(1, 5):
                grade = clamp(random.normalvariate(base_grade - subject_difficulty, 1.05), 0, 10)
                grades.append({
                    "grade_id": grade_id,
                    "student_id": student_id,
                    "subject_id": subject["subject_id"],
                    "bimester": bimester,
                    "school_year": 2026,
                    "grade": round(grade, 1),
                    "recovery_exam": 1 if grade < 6 else 0,
                })
                grade_id += 1
                total_grades += grade

        for month in range(2, 12):
            internet_factor = 1.0 if socio["internet_access"] else 0.35
            work_penalty = 0.65 if socio["works_after_school"] else 1.0
            logins = round(clamp(random.normalvariate(13 * internet_factor * work_penalty, 4), 0, 30))
            homework = round(clamp(random.normalvariate(18 * internet_factor * work_penalty, 5), 0, 28))
            engagement.append({
                "engagement_id": engagement_id,
                "student_id": student_id,
                "month": month,
                "school_year": 2026,
                "platform_logins": logins,
                "homework_submitted": homework,
                "messages_to_teacher": round(clamp(random.normalvariate(3, 2), 0, 14)),
            })
            engagement_id += 1
            logins_total += logins
            homework_total += homework

        avg_grade = total_grades / (len(subjects) * 4)
        absence_rate = total_absences / total_classes
        engagement_rate = clamp((logins_total / 160 + homework_total / 210) / 2, 0, 1)
        dropout_p = dropout_probability(student, socio, avg_grade, absence_rate, engagement_rate)
        dropped_out = random.random() < dropout_p
        dropout_reason = ""
        if dropped_out:
            dropout_reason = random.choices(
                ["Trabalho", "Faltas recorrentes", "Mudanca de cidade", "Desmotivacao", "Problemas familiares"],
                [30, 26, 10, 22, 12],
            )[0]
        enrollments.append({
            "enrollment_id": student_id,
            "student_id": student_id,
            "class_id": class_row["class_id"],
            "enrollment_date": "2026-02-02",
            "status": "Evadido" if dropped_out else "Ativo",
            "dropout_date": (date(2026, 8, 1) + timedelta(days=random.randint(0, 100))).isoformat() if dropped_out else "",
            "dropout_reason": dropout_reason,
        })

        if dropout_p > 0.35 or absence_rate > 0.22 or avg_grade < 5.8:
            result = random.choices(["Melhorou frequencia", "Sem retorno", "Encaminhado CRAS", "Em acompanhamento"], [42, 18, 16, 24])[0]
            interventions.append({
                "intervention_id": intervention_id,
                "student_id": student_id,
                "intervention_date": (date(2026, 5, 1) + timedelta(days=random.randint(0, 170))).isoformat(),
                "intervention_type": random.choice(["Busca ativa", "Reuniao com responsavel", "Reforco escolar", "Apoio psicossocial"]),
                "responsible_team": random.choice(["Coordenacao", "Orientacao pedagogica", "Assistencia social"]),
                "result": result,
            })
            intervention_id += 1

    datasets = {
        "students": students,
        "guardians": guardians,
        "classes": classes,
        "subjects": subjects,
        "teachers": teachers,
        "enrollments": enrollments,
        "socioeconomic": socioeconomic,
        "attendance": attendance,
        "grades": grades,
        "digital_engagement": engagement,
        "interventions": interventions,
    }
    for name, rows in datasets.items():
        write_csv(name, rows)
    build_sqlite(datasets)
    print(f"Dados gerados em {BRONZE}")
    print(f"Banco SQLite criado em {DB_PATH}")
    print(f"Alunos: {len(students)} | Frequencia: {len(attendance)} | Notas: {len(grades)}")


def build_sqlite(datasets):
    if DB_PATH.exists():
        DB_PATH.unlink()
    connection = sqlite3.connect(DB_PATH)
    try:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        for table, rows in datasets.items():
            if not rows:
                continue
            columns = list(rows[0].keys())
            placeholders = ", ".join(["?"] * len(columns))
            sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            connection.executemany(sql, [[row[column] for column in columns] for row in rows])
        connection.commit()
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description="Gera uma base escolar sintetica para analise de evasao.")
    parser.add_argument("--students", type=int, default=2500, help="Quantidade de alunos a simular.")
    parser.add_argument("--seed", type=int, default=2026, help="Semente para reprodutibilidade.")
    args = parser.parse_args()
    generate(args.students, args.seed)


if __name__ == "__main__":
    main()
