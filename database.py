import sqlite3


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
                ON DELETE CASCADE
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
                ON DELETE CASCADE
        )
    """)

    # Zapisujemy zmiany
    conn.commit()

    # Zamykamy połączenie
    conn.close()

    print("Baza danych została utworzona.")

# --------------------------
# URUCHOMIENIE PROGRAMU
# --------------------------

if __name__ == "__main__":
    create_database()