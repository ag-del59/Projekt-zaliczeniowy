import sqlite3
import pandas as pd
from scipy.stats import fisher_exact

DB_NAME = "brca_database_5000.db"


def create_database():
    # Połączenie z bazą danych.
    # Jeśli plik bazy nie istnieje, SQLite utworzy go automatycznie.
    conn = sqlite3.connect(DB_NAME)

    # Włączenie obsługi kluczy obcych
    conn.execute("PRAGMA foreign_keys = ON")

    cursor = conn.cursor()

    # --------------------------
    # TABELA PACJENTÓW
    # --------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_code TEXT NOT NULL UNIQUE,
            age INTEGER,
            has_cancer TEXT CHECK (
                has_cancer IN ('tak', 'nie')
            )
        )
    """)

    # --------------------------
    # TABELA BADAŃ
    # --------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tests (
            test_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            test_date TEXT,
            gene TEXT NOT NULL,
            test_type TEXT,
            panel TEXT,

            FOREIGN KEY (patient_id)
                REFERENCES patients(patient_id)
                ON DELETE CASCADE,

            UNIQUE(patient_id, test_date, gene, test_type, panel)
        )
    """)

    # --------------------------
    # TABELA WARIANTÓW
    # --------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS variants (
            variant_id INTEGER PRIMARY KEY AUTOINCREMENT,
            gene TEXT NOT NULL,
            rs_id TEXT,
            hgvs_c TEXT,
            hgvs_g TEXT,
            hgvs_p TEXT,

            UNIQUE(gene, hgvs_c)
        )
    """)

    # --------------------------
    # TABELA WYKRYTYCH WARIANTÓW
    # --------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS findings (
            finding_id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id INTEGER NOT NULL,
            variant_id INTEGER NOT NULL,
            zygosity TEXT NOT NULL,
            classification TEXT,
            notes TEXT,

            FOREIGN KEY (test_id)
                REFERENCES tests(test_id)
                ON DELETE CASCADE,

            FOREIGN KEY (variant_id)
                REFERENCES variants(variant_id)
                ON DELETE CASCADE,

            UNIQUE(test_id, variant_id, zygosity)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reference_frequencies (
            reference_id INTEGER PRIMARY KEY AUTOINCREMENT,
            variant_id INTEGER NOT NULL,
            population TEXT NOT NULL,
            allele_count INTEGER,
            allele_number INTEGER,
            allele_frequency REAL,
            homozygote_count INTEGER,
            source TEXT NOT NULL,
            release_version TEXT,
            dataset TEXT,
            genome_build TEXT,
            retrieval_date TEXT,
            source_url TEXT,
            notes TEXT,

            FOREIGN KEY (variant_id)
                REFERENCES variants(variant_id)
                ON DELETE CASCADE,

            UNIQUE(
                variant_id,
                population,
                source,
                release_version,
                dataset
            )
        )
    """)

    # Zapisujemy zmiany
    conn.commit()

    # Zamykamy połączenie
    conn.close()

    print("Baza danych została utworzona.")


def import_variants_from_excel(file_path):
    df = pd.read_excel(file_path, sheet_name="Warianty")

    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    for _, row in df.iterrows():

        patient_code = row["kod_pacjenta"]
        gene = row["gen"]
        rs_id = row["rs_id"]
        hgvs_c = row["hgvs_c"]
        hgvs_g = row["hgvs_g"]
        hgvs_p = row["hgvs_p"]
        zygosity = row["zygotycznosc"]
        classification = row["klasyfikacja"]
        notes = row["uwagi"]

        # --------------------------
        # 1. DODAJ WARIANT
        # --------------------------

        cursor.execute("""
            INSERT OR IGNORE INTO variants (
                gene,
                rs_id,
                hgvs_c,
                hgvs_g,
                hgvs_p
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            gene,
            rs_id,
            hgvs_c,
            hgvs_g,
            hgvs_p
        ))

        # --------------------------
        # 2. POBIERZ variant_id
        # --------------------------

        cursor.execute("""
            SELECT variant_id
            FROM variants
            WHERE gene = ?
            AND hgvs_c = ?
        """, (
            gene,
            hgvs_c
        ))

        variant_id = cursor.fetchone()[0]

        # --------------------------
        # 3. ZNAJDŹ test_id
        # --------------------------

        cursor.execute("""
            SELECT t.test_id
            FROM tests t
            JOIN patients p
                ON t.patient_id = p.patient_id
            WHERE p.patient_code = ?
            AND t.gene = ?
            LIMIT 1
        """, (
            patient_code,
            gene
        ))

        result = cursor.fetchone()

        if result is None:
            print(
                f"Brak badania dla pacjenta {patient_code}, gen {gene}"
            )
            continue

        test_id = result[0]

        # --------------------------
        # 4. DODAJ WYKRYCIE
        # --------------------------

        cursor.execute("""
            INSERT OR IGNORE INTO findings (
                test_id,
                variant_id,
                zygosity,
                classification,
                notes
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            test_id,
            variant_id,
            zygosity,
            classification,
            notes
        ))

    conn.commit()
    conn.close()

    print("Dane z arkusza Warianty zostały zaimportowane.")


# --------------------------
# URUCHOMIENIE PROGRAMU
# --------------------------

def import_tests_from_excel(file_path):
    # Wczytujemy arkusz "Badania" z Excela
    df = pd.read_excel(file_path, sheet_name="Badania")

    # Łączymy się z bazą
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")

    cursor = conn.cursor()

    for _, row in df.iterrows():

        patient_code = row["kod_pacjenta"]
        test_date = row["data_badania"]
        gene = row["gen"]
        test_type = row["rodzaj_testu"]
        panel = row["panel_testowy"]
        age = int(row["wiek"])
        has_cancer = str(row["czy_nowotwor"]).strip().lower()
        if has_cancer not in ("tak", "nie"):
            raise ValueError(f"Nieprawidłowa wartość czy_nowotwor: {has_cancer}")

        # 1. Dodaj pacjenta, jeśli jeszcze nie istnieje
        cursor.execute("""
            INSERT OR IGNORE INTO patients (patient_code, age, has_cancer)
            VALUES (?, ?, ?)
        """, (patient_code, age, has_cancer))

        # 2. Pobierz patient_id
        cursor.execute("""
            SELECT patient_id
            FROM patients
            WHERE patient_code = ?
        """, (patient_code,))

        patient_id = cursor.fetchone()[0]

        # 3. Dodaj badanie
        cursor.execute("""
            INSERT OR IGNORE INTO tests (
                patient_id,
                test_date,
                gene,
                test_type,
                panel
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            patient_id,
            str(test_date),
            gene,
            test_type,
            panel
        ))

    conn.commit()
    conn.close()

    print("Dane z arkusza Badania zostały zaimportowane.")

    # -------------------------------------------------------


def check_import():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM patients")
    patients_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tests")
    tests_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM variants")
    variants_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM findings")
    findings_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM reference_frequencies"
    )
    reference_count = cursor.fetchone()[0]

    conn.close()

    print("Liczba pacjentów:", patients_count)
    print("Liczba badań:", tests_count)
    print("Liczba unikalnych wariantów:", variants_count)
    print("Liczba wykryć wariantów:", findings_count)
    print(
        "Liczba danych referencyjnych:",
        reference_count
    )


# --------------------------------------------








def get_variant_list():
    conn = sqlite3.connect(DB_NAME)

    query = """
        SELECT
            variant_id,
            gene,
            rs_id,
            hgvs_c
        FROM variants
        ORDER BY gene, hgvs_c
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def get_variant_labels():
    df = get_variant_list()

    labels = []

    for _, row in df.iterrows():
        label = (
            f"{row['gene']} — "
            f"{row['rs_id']} — "
            f"{row['hgvs_c']}"
        )

        labels.append(label)

    return labels


def import_reference_from_excel(file_path):
    df = pd.read_excel(
        file_path,
        sheet_name="Dane_gnomAD"
    )

    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")

    cursor = conn.cursor()

    imported = 0
    skipped = 0

    for _, row in df.iterrows():

        rs_id = row["rs_id"]
        population = row["populacja"]

        # Pomijamy wiersze, w których nie uzupełniono jeszcze danych gnomAD
        if pd.isna(row["AC"]) or pd.isna(row["AN"]):
            skipped += 1
            continue

        # --------------------------
        # 1. ZNAJDŹ variant_id
        # --------------------------

        cursor.execute("""
            SELECT variant_id
            FROM variants
            WHERE rs_id = ?
        """, (rs_id,))

        result = cursor.fetchone()

        if result is None:
            print(
                f"Nie znaleziono wariantu {rs_id} "
                f"w tabeli variants."
            )
            skipped += 1
            continue

        variant_id = result[0]

        # --------------------------
        # 2. PRZYGOTUJ DANE
        # --------------------------

        allele_count = int(row["AC"])
        allele_number = int(row["AN"])

        allele_frequency = (
            float(row["AF"])
            if not pd.isna(row["AF"])
            else allele_count / allele_number
        )

        homozygote_count = (
            int(row["liczba_homozygot"])
            if not pd.isna(row["liczba_homozygot"])
            else None
        )

        release_version = (
            str(row["release_gnomAD"])
            if not pd.isna(row["release_gnomAD"])
            else None
        )

        dataset = (
            str(row["dataset"])
            if not pd.isna(row["dataset"])
            else None
        )

        genome_build = (
            str(row["genome_build"])
            if not pd.isna(row["genome_build"])
            else None
        )

        retrieval_date = (
            str(row["data_pobrania"])
            if not pd.isna(row["data_pobrania"])
            else None
        )

        source_url = (
            str(row["source_url"])
            if not pd.isna(row["source_url"])
            else None
        )

        notes = (
            str(row["uwagi"])
            if not pd.isna(row["uwagi"])
            else None
        )

        # --------------------------
        # 3. DODAJ DO BAZY
        # --------------------------
        cursor.execute("""
            SELECT reference_id
            FROM reference_frequencies
            WHERE variant_id = ?
              AND population = ?
              AND source = ?
              AND COALESCE(release_version, '') = COALESCE(?, '')
              AND COALESCE(dataset, '') = COALESCE(?, '')
        """, (
            variant_id,
            population,
            "gnomAD",
            release_version,
            dataset
        ))

        existing = cursor.fetchone()

        if existing is not None:
            skipped += 1
            continue

        cursor.execute("""
            INSERT OR IGNORE INTO reference_frequencies (
                variant_id,
                population,
                allele_count,
                allele_number,
                allele_frequency,
                homozygote_count,
                source,
                release_version,
                dataset,
                genome_build,
                retrieval_date,
                source_url,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            variant_id,
            population,
            allele_count,
            allele_number,
            allele_frequency,
            homozygote_count,
            "gnomAD",
            release_version,
            dataset,
            genome_build,
            retrieval_date,
            source_url,
            notes
        ))

        if cursor.rowcount == 1:
            imported += 1
        else:
            skipped += 1

    conn.commit()
    conn.close()

    print(
        f"Dane referencyjne: dodano {imported}, "
        f"pominięto {skipped}."
    )




def get_comparison_by_rs(rs_id, population, age_min=None, age_max=None, has_cancer=None):
    """Porównanie częstości wariantu w przefiltrowanej grupie z referencją."""
    conn = sqlite3.connect(DB_NAME)
    conditions = ["p.age >= ?" if age_min is not None else "1=1",
                  "p.age <= ?" if age_max is not None else "1=1",
                  "p.has_cancer = ?" if has_cancer is not None else "1=1"]
    patient_filter = " AND ".join(conditions)
    filter_params = []
    if age_min is not None:
        filter_params.append(age_min)
    if age_max is not None:
        filter_params.append(age_max)
    if has_cancer is not None:
        filter_params.append(has_cancer.lower())

    query = f"""
        SELECT v.gene, v.rs_id, v.hgvs_c,
               r.population,
               r.allele_count AS ref_ac,
               r.allele_number AS ref_an,
               r.allele_frequency AS ref_af,
               (SELECT COUNT(DISTINCT t.patient_id)
                  FROM tests t JOIN patients p ON p.patient_id=t.patient_id
                 WHERE t.gene=v.gene AND {patient_filter}) AS tested_n,
               (SELECT COUNT(DISTINCT t.patient_id)
                  FROM findings f
                  JOIN tests t ON t.test_id=f.test_id
                  JOIN patients p ON p.patient_id=t.patient_id
                 WHERE f.variant_id=v.variant_id
                   AND f.zygosity='heterozygota'
                   AND {patient_filter}) AS heterozygous_n,
               (SELECT COUNT(DISTINCT t.patient_id)
                  FROM findings f
                  JOIN tests t ON t.test_id=f.test_id
                  JOIN patients p ON p.patient_id=t.patient_id
                 WHERE f.variant_id=v.variant_id
                   AND f.zygosity='homozygota'
                   AND {patient_filter}) AS homozygous_n
        FROM variants v
        JOIN reference_frequencies r ON r.variant_id=v.variant_id
        WHERE v.rs_id=? AND r.population=?
    """
    params = tuple(filter_params * 3 + [rs_id, population])
    try:
        df = pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()

    if df.empty or int(df.iloc[0]["tested_n"]) == 0:
        return None

    df["lab_ac"] = df["heterozygous_n"] + 2 * df["homozygous_n"]
    df["lab_an"] = 2 * df["tested_n"]
    df["lab_af"] = df["lab_ac"] / df["lab_an"]
    df["lab_af_percent"] = df["lab_af"] * 100
    df["ref_af_percent"] = df["ref_af"] * 100
    df["frequency_ratio"] = df.apply(
        lambda row: row["lab_af"] / row["ref_af"]
        if pd.notna(row["ref_af"]) and row["ref_af"] > 0 else None,
        axis=1
    )

    for idx, row in df.iterrows():
        lab_ac, lab_an = int(row["lab_ac"]), int(row["lab_an"])
        ref_ac, ref_an = int(row["ref_ac"]), int(row["ref_an"])
        if ref_an <= 0 or ref_ac < 0 or ref_ac > ref_an:
            df.loc[idx, ["odds_ratio", "p_value", "significant"]] = [None, None, False]
            continue
        odds_ratio, p_value = fisher_exact(
            [[lab_ac, lab_an - lab_ac], [ref_ac, ref_an - ref_ac]],
            alternative="two-sided"
        )
        df.loc[idx, "odds_ratio"] = odds_ratio
        df.loc[idx, "p_value"] = p_value
        df.loc[idx, "significant"] = bool(p_value < 0.05)
    return df


def get_cancer_group_af(rs_id, age_min=None, age_max=None):
    """AF wariantu w dwóch grupach pacjentów; niezależnie od danych gnomAD."""
    conn = sqlite3.connect(DB_NAME)
    query = """
        SELECT p.has_cancer,
               COUNT(DISTINCT t.patient_id) AS tested_n,
               COUNT(DISTINCT CASE WHEN f.zygosity IN ('heterozygota', 'homozygota')
                     THEN t.patient_id END) AS carriers_n,
               COUNT(DISTINCT CASE WHEN f.zygosity = 'heterozygota'
                     THEN t.patient_id END) AS heterozygous_n,
               COUNT(DISTINCT CASE WHEN f.zygosity = 'homozygota'
                     THEN t.patient_id END) AS homozygous_n
        FROM variants v
        JOIN tests t ON t.gene = v.gene
        JOIN patients p ON p.patient_id = t.patient_id
        LEFT JOIN findings f ON f.test_id = t.test_id
                            AND f.variant_id = v.variant_id
        WHERE v.rs_id = ?
          AND p.has_cancer IN ('tak', 'nie')
          AND (? IS NULL OR p.age >= ?)
          AND (? IS NULL OR p.age <= ?)
        GROUP BY p.has_cancer
    """
    try:
        df = pd.read_sql_query(
            query, conn,
            params=(rs_id, age_min, age_min, age_max, age_max)
        )
    finally:
        conn.close()
    if df.empty:
        return df
    df["allele_count"] = df["heterozygous_n"] + 2 * df["homozygous_n"]
    df["allele_number"] = 2 * df["tested_n"]
    df["af_percent"] = 100 * df["allele_count"] / df["allele_number"]
    return df


def get_all_comparisons(population, gene="Wszystkie",
                        age_min=None, age_max=None, has_cancer=None):
    conn = sqlite3.connect(DB_NAME)

    # Pobieramy wszystkie warianty
    cursor = conn.cursor()

    cursor.execute("""
        SELECT rs_id
        FROM variants
        WHERE rs_id IS NOT NULL
        ORDER BY gene, rs_id
    """)

    rs_ids = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    results = []

    # Dla każdego wariantu korzystamy z funkcji,
    # która już działa dla pojedynczego wariantu
    for rs_id in rs_ids:

        df = get_comparison_by_rs(
            rs_id, population, age_min, age_max, has_cancer
        )

        if df is None:
            continue

        row = df.iloc[0]

        # Jeżeli wybrano konkretny gen,
        # pomijamy warianty drugiego genu
        if (
                gene != "Wszystkie"
                and row["gene"] != gene
        ):
            continue

        results.append({
            "gene": row["gene"],
            "rs_id": row["rs_id"],
            "hgvs_c": row["hgvs_c"],
            "lab_af_percent": row["lab_af_percent"],
            "ref_af_percent": row["ref_af_percent"],
            "frequency_ratio": row["frequency_ratio"],
            "p_value": row["p_value"]
        })

    return pd.DataFrame(results)


def get_variant_age_groups(rs_id):
    """
    Zwraca liczbę przebadanych pacjentów i nosicieli wariantu
    w grupach wiekowych, osobno według statusu nowotworowego.
    Każdy pacjent jest liczony maksymalnie raz w danej grupie.
    """

    query = """
        WITH age_groups AS (
            SELECT
                p.patient_id,
                p.has_cancer,
                CASE
                    WHEN p.age BETWEEN 18 AND 30 THEN '18–30'
                    WHEN p.age BETWEEN 31 AND 40 THEN '31–40'
                    WHEN p.age BETWEEN 41 AND 50 THEN '41–50'
                    WHEN p.age BETWEEN 51 AND 60 THEN '51–60'
                    WHEN p.age BETWEEN 61 AND 70 THEN '61–70'
                    WHEN p.age >= 71 THEN '71+'
                END AS age_group,
                CASE
                    WHEN p.age BETWEEN 18 AND 30 THEN 1
                    WHEN p.age BETWEEN 31 AND 40 THEN 2
                    WHEN p.age BETWEEN 41 AND 50 THEN 3
                    WHEN p.age BETWEEN 51 AND 60 THEN 4
                    WHEN p.age BETWEEN 61 AND 70 THEN 5
                    WHEN p.age >= 71 THEN 6
                END AS age_order,
                MAX(
                    CASE
                        WHEN f.finding_id IS NOT NULL
                         AND f.zygosity IN (
                             'heterozygota', 'homozygota'
                         )
                        THEN 1 ELSE 0
                    END
                ) AS is_carrier
            FROM variants v
            JOIN tests t
                ON t.gene = v.gene
            JOIN patients p
                ON p.patient_id = t.patient_id
            LEFT JOIN findings f
                ON f.test_id = t.test_id
               AND f.variant_id = v.variant_id
            WHERE v.rs_id = ?
              AND p.age >= 18
              AND p.has_cancer IN ('tak', 'nie')
            GROUP BY p.patient_id, p.has_cancer, age_group, age_order
        )
        SELECT
            age_group,
            age_order,
            has_cancer,
            COUNT(*) AS tested_n,
            SUM(is_carrier) AS carriers_n
        FROM age_groups
        WHERE age_group IS NOT NULL
        GROUP BY age_group, age_order, has_cancer
        ORDER BY age_order, has_cancer
    """

    with sqlite3.connect(DB_NAME) as conn:
        df = pd.read_sql_query(query, conn, params=(rs_id,))

    if not df.empty:
        df["carriers_percent"] = (
            100 * df["carriers_n"] / df["tested_n"]
        )

    return df

