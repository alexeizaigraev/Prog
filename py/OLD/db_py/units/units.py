import tkinter as tk
from tkinter import messagebox
import sqlite3

DB_PATH = r"D:\db\sqlite\az.db"
TABLE = "units"
FONT = ("Arial", 14)

def get_connection():
    return sqlite3.connect(DB_PATH)

def fetch_gosnomers():
    with get_connection() as conn:
        return [row[0] for row in conn.execute(f"SELECT gosnomer FROM {TABLE} ORDER BY gosnomer ASC")]

def fetch_gosnomers_by_prefix(prefix):
    with get_connection() as conn:
        return [row[0] for row in conn.execute(f"SELECT gosnomer FROM {TABLE} WHERE gosnomer LIKE ? ORDER BY gosnomer ASC", (prefix + "%",))]

def fetch_record_by_gosnomer(gosnomer):
    with get_connection() as conn:
        cur = conn.execute(f"SELECT * FROM {TABLE} WHERE gosnomer = ?", (gosnomer,))
        return cur.fetchone()

def show_record(record):
    if record:
        with get_connection() as conn:
            cur = conn.execute(f"PRAGMA table_info({TABLE})")
            columns = [row[1] for row in cur.fetchall()]
        for col, val in zip(columns, record):
            if col in field_entries:
                field_entries[col].delete(0, tk.END)
                field_entries[col].insert(0, str(val))
    else:
        messagebox.showinfo("Нет данных", "Запись не найдена")

def confirm_gosnomer_selection():
    selected = listbox_gosnomer.get(tk.ACTIVE)
    record = fetch_record_by_gosnomer(selected)
    show_record(record)

def reset_gosnomers():
    update_listbox(listbox_gosnomer, fetch_gosnomers())

def update_listbox(listbox, items):
    listbox.delete(0, tk.END)
    for item in items:
        listbox.insert(tk.END, item)

def search_by_prefix(event=None):
    prefix = entry_search.get().strip()
    if not prefix:
        reset_gosnomers()
        return
    gosnomers = fetch_gosnomers_by_prefix(prefix)
    update_listbox(listbox_gosnomer, gosnomers)

def clear_form():
    for entry in field_entries.values():
        entry.delete(0, tk.END)

def create_record():
    clear_form()

def save_record():
    values = {col: field_entries[col].get().strip() for col in columns}
    gosnomer = values["gosnomer"]
    if not gosnomer:
        messagebox.showwarning("Сохранение", "Поле 'gosnomer' обязательно.")
        return
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM {TABLE} WHERE gosnomer = ?", (gosnomer,))
        exists = cur.fetchone()[0]
        if exists:
            assignments = ", ".join(f"{col} = ?" for col in values)
            cur.execute(f"UPDATE {TABLE} SET {assignments} WHERE gosnomer = ?", (*values.values(), gosnomer))
            messagebox.showinfo("Обновлено", f"Запись с госномером {gosnomer} обновлена.")
        else:
            fields = ", ".join(values.keys())
            placeholders = ", ".join("?" for _ in values)
            cur.execute(f"INSERT INTO {TABLE} ({fields}) VALUES ({placeholders})", tuple(values.values()))
            messagebox.showinfo("Создано", f"Создана новая запись с госномером {gosnomer}.")
        conn.commit()
    reset_gosnomers()

def delete_record():
    gosnomer = field_entries["gosnomer"].get().strip()
    if not gosnomer:
        messagebox.showwarning("Удаление", "Нет госномера для удаления.")
        return
    with get_connection() as conn:
        conn.execute(f"DELETE FROM {TABLE} WHERE gosnomer = ?", (gosnomer,))
        conn.commit()
    clear_form()
    reset_gosnomers()
    messagebox.showinfo("Удалено", f"Запись с госномером {gosnomer} удалена.")

# Интерфейс
root = tk.Tk()
root.title("Интерфейс для таблицы units")

# Поиск
tk.Label(root, text="Поиск по госномеру:", font=FONT).grid(row=0, column=0, sticky="e")
entry_search = tk.Entry(root, font=FONT)
entry_search.grid(row=0, column=1, sticky="we")
entry_search.bind("<Return>", search_by_prefix)
tk.Button(root, text="Найти", font=FONT, command=search_by_prefix).grid(row=0, column=2, padx=5)
tk.Button(root, text="Создать", font=FONT, command=create_record).grid(row=0, column=3, padx=5)
tk.Button(root, text="Сохранить", font=FONT, command=save_record).grid(row=0, column=4, padx=5)
tk.Button(root, text="Удалить", font=FONT, command=delete_record).grid(row=0, column=5, padx=5)

# Поля записи
with get_connection() as conn:
    columns = [row[1] for row in conn.execute(f"PRAGMA table_info({TABLE})")]
    print(columns)
    #print(field_entries.keys())

field_entries = {}
for i, col in enumerate(columns):
    tk.Label(root, text=col + ":", font=FONT).grid(row=i+1, column=0, sticky="e")
    entry = tk.Entry(root, font=FONT, width=40)
    entry.grid(row=i+1, column=1, columnspan=5, sticky="we", padx=5, pady=1)
    field_entries[col] = entry

# Список госномеров
tk.Button(root, text="Выбрать госномер", font=FONT, command=confirm_gosnomer_selection).grid(row=1, column=6)
listbox_gosnomer = tk.Listbox(root, font=FONT, height=20)
listbox_gosnomer.grid(row=2, column=6, rowspan=15, padx=5)
tk.Button(root, text="Сбросить список", font=FONT, command=reset_gosnomers).grid(row=18, column=6, pady=10)

# Запуск
reset_gosnomers()
root.mainloop()