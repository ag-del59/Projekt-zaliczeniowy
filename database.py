import sqlite3
import pandas as pd

DB_NAME = "brca_database.db"


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
            patient_code TEXT NOT NULL UNIQUE
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

        # 1. Dodaj pacjenta, jeśli jeszcze nie istnieje
        cursor.execute("""
            INSERT OR IGNORE INTO patients (patient_code)
            VALUES (?)
        """, (patient_code,))

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


    #-------------------------------------------------------
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
#--------------------------------------------

def get_variant_statistics():

    conn = sqlite3.connect(DB_NAME)

    query = """
        SELECT
            v.gene,
            v.rs_id,
            v.hgvs_c,

            COUNT(
                DISTINCT t_all.patient_id
            ) AS tested_n,

            COUNT(
                DISTINCT CASE
                    WHEN f.zygosity = 'heterozygota'
                    THEN t_positive.patient_id
                END
            ) AS heterozygous_n,

            COUNT(
                DISTINCT CASE
                    WHEN f.zygosity = 'homozygota'
                    THEN t_positive.patient_id
                END
            ) AS homozygous_n

        FROM variants v

        -- wszystkie osoby przebadane dla danego genu
        JOIN tests t_all
            ON t_all.gene = v.gene

        -- wykrycia konkretnego wariantu
        LEFT JOIN findings f
            ON f.variant_id = v.variant_id

        -- badanie osoby, u której znaleziono wariant
        LEFT JOIN tests t_positive
            ON f.test_id = t_positive.test_id

        GROUP BY
            v.variant_id,
            v.gene,
            v.rs_id,
            v.hgvs_c

        ORDER BY
            v.gene,
            v.hgvs_c
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    # Liczba alleli zawierających wariant
    df["allele_count"] = (
            df["heterozygous_n"]
            + 2 * df["homozygous_n"]
    )

    # Łączna liczba przebadanych alleli
    df["allele_number"] = (
            2 * df["tested_n"]
    )

    # Częstość allelu w danych laboratoryjnych
    df["lab_af"] = (
            df["allele_count"]
            / df["allele_number"]
    )

    # Częstość w procentach
    df["lab_af_percent"] = (
            df["lab_af"] * 100
    )

    return df

def get_variant_by_rs(rs_id):

    conn = sqlite3.connect(DB_NAME)

    query = """
        SELECT
            v.gene,
            v.rs_id,
            v.hgvs_c,

            COUNT(
                DISTINCT t_all.patient_id
            ) AS tested_n,

            COUNT(
                DISTINCT CASE
                    WHEN f.zygosity = 'heterozygota'
                    THEN t_positive.patient_id
                END
            ) AS heterozygous_n,

            COUNT(
                DISTINCT CASE
                    WHEN f.zygosity = 'homozygota'
                    THEN t_positive.patient_id
                END
            ) AS homozygous_n

        FROM variants v

        JOIN tests t_all
            ON t_all.gene = v.gene

        LEFT JOIN findings f
            ON f.variant_id = v.variant_id

        LEFT JOIN tests t_positive
            ON f.test_id = t_positive.test_id

        WHERE v.rs_id = ?

        GROUP BY
            v.variant_id,
            v.gene,
            v.rs_id,
            v.hgvs_c
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(rs_id,)
    )

    conn.close()

    if df.empty:
        return None

    df["allele_count"] = (
        df["heterozygous_n"]
        + 2 * df["homozygous_n"]
    )

    df["allele_number"] = (
        2 * df["tested_n"]
    )

    df["lab_af"] = (
        df["allele_count"]
        / df["allele_number"]
    )

    df["lab_af_percent"] = (
        df["lab_af"] * 100
    )

    return df

def get_all_rs_ids():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT rs_id
        FROM variants
        WHERE rs_id IS NOT NULL
        ORDER BY rs_id
    """)

    results = cursor.fetchall()

    conn.close()

    rs_ids = [row[0] for row in results]

    return rs_ids

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

def clear_reference_data():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM reference_frequencies
    """)

    conn.commit()
    conn.close()

    print("Dane referencyjne zostały wyczyszczone.")

if __name__ == "__main__":

    create_database()

    import_tests_from_excel(
        "BRCA1_BRCA2_dane_syntetyczne_1000_pacjentow.xlsx"
    )

    import_variants_from_excel(
        "BRCA1_BRCA2_dane_syntetyczne_1000_pacjentow.xlsx"
    )

    import_reference_from_excel(
        "gnomAD_dane_referencyjne_BRCA1_BRCA2.xlsx"
    )

    check_import()