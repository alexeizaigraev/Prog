import sqlite3

DB_PATH = r"D:\db\sqlite\az.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

try:
    cur.execute("PRAGMA foreign_keys = OFF")
    
    # Создаём новую таблицу без GENERATED полей
    cur.execute("""
    CREATE TABLE put_new (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        list        TEXT,
        gosnomer    TEXT,
        decada      INTEGER,
        year        INTEGER,
        fio         TEXT,
        t_start     INTEGER DEFAULT 0,
        t_add       INTEGER DEFAULT 0,
        t_end       INTEGER DEFAULT 0,
        t_marka     TEXT,
        odo_start   INTEGER DEFAULT 0,
        odo_end     INTEGER DEFAULT 0,
        h_start     INTEGER DEFAULT 0,
        h_end       INTEGER DEFAULT 0,
        oil_start   INTEGER DEFAULT 0,
        oil_add     INTEGER DEFAULT 0,
        oil_end     INTEGER DEFAULT 0,
        oil_marka   TEXT,
        FOREIGN KEY (gosnomer) REFERENCES units (gosnomer)
    )
    """)
    
    # Копируем данные
    cur.execute("""
    INSERT INTO put_new (id, list, gosnomer, decada, year, fio,
        t_start, t_add, t_end, t_marka,
        odo_start, odo_end,
        h_start, h_end,
        oil_start, oil_add, oil_end, oil_marka)
    SELECT id, list, gosnomer, decada, year, fio,
        t_start, t_add, t_end, t_marka,
        odo_start, odo_end,
        h_start, h_end,
        oil_start, oil_add, oil_end, oil_marka
    FROM put
    """)
    
    # Удаляем старую, переименовываем новую
    cur.execute("DROP TABLE put")
    cur.execute("ALTER TABLE put_new RENAME TO put")
    
    cur.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    print("✓ Миграция успешна!")
except Exception as e:
    print(f"✗ Ошибка: {e}")
    conn.rollback()
finally:
    conn.close()