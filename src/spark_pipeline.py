import builtins
from pathlib import Path
import os
import sys
import subprocess

from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.functions import vector_to_array
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    avg,
    col,
    count,
    expr,
    lit,
    round,
    sum as spark_sum,
    when,
)


ROOT = Path(__file__).resolve().parents[1]
BRONZE = ROOT / "data" / "bronze"
SILVER = ROOT / "data" / "silver"
GOLD = ROOT / "data" / "gold"


def read_csv(spark, name):
    return spark.read.option("header", True).option("inferSchema", True).csv(str(BRONZE / f"{name}.csv"))


def write_dataset(df, path):
    target = str(path)
    df.write.mode("overwrite").parquet(target + "_parquet")
    df.coalesce(1).write.mode("overwrite").option("header", True).csv(target + "_csv")


def main():
    # Verifica se JAVA_HOME está configurado e se o java é executável
    java_home = os.environ.get("JAVA_HOME")
    if not java_home:
        print(
            "ERROR: JAVA_HOME is not set. Please set JAVA_HOME to your JDK 17 installation path (e.g. /usr/lib/jvm/java-17-openjdk-amd64)",
            file=sys.stderr,
        )
        sys.exit(1)
    java_bin = os.path.join(java_home, "bin", "java")
    if not os.path.isfile(java_bin):
        print(f"ERROR: java executable not found at {java_bin}. Check your JAVA_HOME.", file=sys.stderr)
        sys.exit(1)
    try:
        completed = subprocess.run([java_bin, "-version"], capture_output=True, text=True, timeout=10)
        if completed.returncode != 0:
            print(
                "ERROR: running java -version failed. Check your Java installation and JAVA_HOME.", file=sys.stderr
            )
            print(completed.stderr or completed.stdout, file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: unable to run java: {e}", file=sys.stderr)
        sys.exit(1)

    spark = (
        SparkSession.builder
        .appName("EvasaoEscolarBigData")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    students = read_csv(spark, "students")
    socioeconomic = read_csv(spark, "socioeconomic")
    enrollments = read_csv(spark, "enrollments")
    classes = read_csv(spark, "classes")
    subjects = read_csv(spark, "subjects")
    attendance = read_csv(spark, "attendance")
    grades = read_csv(spark, "grades")
    engagement = read_csv(spark, "digital_engagement")
    interventions = read_csv(spark, "interventions")

    attendance_features = (
        attendance
        .groupBy("student_id")
        .agg(
            spark_sum("classes_offered").alias("classes_offered_total"),
            spark_sum("absences").alias("absences_total"),
        )
        .withColumn("absence_rate", col("absences_total") / col("classes_offered_total"))
    )

    subject_absences = (
        attendance
        .join(subjects, "subject_id")
        .groupBy("subject_name")
        .agg(
            spark_sum("classes_offered").alias("classes_offered_total"),
            spark_sum("absences").alias("absences_total"),
        )
        .withColumn("absence_rate", round(col("absences_total") / col("classes_offered_total"), 4))
        .orderBy(col("absence_rate").desc())
    )

    grade_features = (
        grades
        .groupBy("student_id")
        .agg(
            round(avg("grade"), 2).alias("avg_grade"),
            spark_sum("recovery_exam").alias("recovery_exams"),
        )
    )

    engagement_features = (
        engagement
        .groupBy("student_id")
        .agg(
            spark_sum("platform_logins").alias("platform_logins_total"),
            spark_sum("homework_submitted").alias("homework_submitted_total"),
            spark_sum("messages_to_teacher").alias("messages_to_teacher_total"),
        )
    )

    intervention_features = (
        interventions
        .groupBy("student_id")
        .agg(count("*").alias("intervention_count"))
    )

    student_profile = (
        students
        .join(socioeconomic, "student_id")
        .join(enrollments, "student_id")
        .join(classes, "class_id")
        .join(attendance_features, "student_id")
        .join(grade_features, "student_id")
        .join(engagement_features, "student_id")
        .join(intervention_features, "student_id", "left")
        .fillna({"intervention_count": 0})
        .withColumn("dropout_label", when(col("status") == "Evadido", 1.0).otherwise(0.0))
        .withColumn("low_income", when(col("family_income_brl") < 2200, 1.0).otherwise(0.0))
        .withColumn("high_distance", when(col("distance_km") > 8, 1.0).otherwise(0.0))
        .withColumn("no_transport", when(col("transport_access") == 0, 1.0).otherwise(0.0))
        .withColumn("no_internet", when(col("internet_access") == 0, 1.0).otherwise(0.0))
        .withColumn("works_flag", col("works_after_school").cast("double"))
        .withColumn("benefit_flag", col("receives_social_benefit").cast("double"))
        .withColumn("food_insecurity_score", col("food_insecurity_score").cast("double"))
    )

    feature_columns = [
        "absence_rate",
        "avg_grade",
        "recovery_exams",
        "platform_logins_total",
        "homework_submitted_total",
        "distance_km",
        "low_income",
        "high_distance",
        "no_transport",
        "no_internet",
        "works_flag",
        "benefit_flag",
        "food_insecurity_score",
        "intervention_count",
    ]

    assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
    model_input = assembler.transform(student_profile).select("student_id", "features", "dropout_label")
    train, test = model_input.randomSplit([0.8, 0.2], seed=2026)

    model = LogisticRegression(featuresCol="features", labelCol="dropout_label", maxIter=50)
    fitted = model.fit(train)
    predictions = fitted.transform(test)
    evaluator = BinaryClassificationEvaluator(labelCol="dropout_label", metricName="areaUnderROC")
    auc = evaluator.evaluate(predictions)

    scored = (
        fitted.transform(assembler.transform(student_profile))
        .withColumn("dropout_risk", vector_to_array(col("probability")).getItem(1))
        .withColumn(
            "risk_band",
            when(col("dropout_risk") >= 0.70, "Alto")
            .when(col("dropout_risk") >= 0.40, "Medio")
            .otherwise("Baixo"),
        )
        .select(
            "student_id",
            "name",
            "grade_level",
            "shift",
            "neighborhood",
            "status",
            "dropout_reason",
            round("dropout_risk", 4).alias("dropout_risk"),
            "risk_band",
            round("absence_rate", 4).alias("absence_rate"),
            "avg_grade",
            "recovery_exams",
            "platform_logins_total",
            "homework_submitted_total",
            "family_income_brl",
            "distance_km",
            "transport_access",
            "internet_access",
            "works_after_school",
            "food_insecurity_score",
            "intervention_count",
        )
        .orderBy(col("dropout_risk").desc())
    )

    dropout_by_neighborhood = (
        scored
        .groupBy("neighborhood")
        .agg(
            count("*").alias("students"),
            spark_sum(when(col("status") == "Evadido", 1).otherwise(0)).alias("dropouts"),
            round(avg("dropout_risk"), 4).alias("avg_risk"),
        )
        .withColumn("dropout_rate", round(col("dropouts") / col("students"), 4))
        .orderBy(col("dropout_rate").desc())
    )

    dropout_reasons = (
        scored
        .where(col("status") == "Evadido")
        .groupBy("dropout_reason")
        .agg(count("*").alias("students"))
        .orderBy(col("students").desc())
    )

    kpis = scored.agg(
        count("*").alias("total_students"),
        spark_sum(when(col("status") == "Evadido", 1).otherwise(0)).alias("dropouts"),
        round(avg("dropout_risk"), 4).alias("avg_dropout_risk"),
        round(avg("absence_rate"), 4).alias("avg_absence_rate"),
        round(avg("avg_grade"), 2).alias("school_avg_grade"),
    ).withColumn("model_auc", lit(builtins.round(float(auc), 4)))

    SILVER.mkdir(parents=True, exist_ok=True)
    GOLD.mkdir(parents=True, exist_ok=True)
    write_dataset(student_profile, SILVER / "student_profile")
    write_dataset(scored, GOLD / "student_risk_scores")
    write_dataset(dropout_by_neighborhood, GOLD / "dropout_by_neighborhood")
    write_dataset(subject_absences, GOLD / "subject_absences")
    write_dataset(dropout_reasons, GOLD / "dropout_reasons")
    write_dataset(kpis, GOLD / "kpis")

    print(f"Pipeline Spark concluido. AUC do modelo: {auc:.4f}")
    print(f"Resultados salvos em {GOLD}")
    spark.stop()


if __name__ == "__main__":
    main()
