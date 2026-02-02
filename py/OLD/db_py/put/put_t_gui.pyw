import tkinter as tk
from tkinter import messagebox
import sqlite3
import re

DB_PATH = r"D:\db\sqlite\az.db"
TABLE = "put"
FONT = ("Arial", 14)

from datetime import datetime


def search_by_list(event=None):
    target_list = entry_search_list.get().strip()
    if not target_list:
        messagebox.showwarning("Поиск", "Введите номер путёвки.")
        return
    record = fetch_record_by_list(target_list)
    if record:
        show_record(record)
    else:
        messagebox.showerror("Ошибка", f"Путёвка '{target_list}' не найдена. Проверь номер.")

def get_connection():
    return sqlite3.connect(DB_PATH)

def log_change(action, record_id, changes):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user = "admin"
    try:
        with get_connection() as conn:
            conn.execute("INSERT INTO put_log (timestamp, action, user, record_id, field_changes) VALUES (?, ?, ?, ?, ?)",
                         (timestamp, action, user, record_id, changes))
            conn.commit()
    except Exception:
        # не фейлим UI при отсутствии таблицы логов
        pass

def fetch_all_lists():
    with get_connection() as conn:
        return [row[0] for row in conn.execute(f"SELECT DISTINCT list FROM {TABLE} ORDER BY list DESC").fetchall()]

def fetch_all_gosnomers():
    with get_connection() as conn:
        return [row[0] for row in conn.execute(f"SELECT DISTINCT gosnomer FROM {TABLE} ORDER BY gosnomer ASC").fetchall()]

def fetch_record_by_list(selected_list):
    with get_connection() as conn:
        cur = conn.execute(f"SELECT * FROM {TABLE} WHERE list = ?", (selected_list,))
        return cur.fetchone()

def fetch_lists_by_gosnomer(selected_gosnomer):
    with get_connection() as conn:
        return [row[0] for row in conn.execute(f"SELECT list FROM {TABLE} WHERE gosnomer = ? ORDER BY list DESC", (selected_gosnomer,)).fetchall()]

def fetch_gosnomers_by_prefix(prefix):
    with get_connection() as conn:
        return [row[0] for row in conn.execute(f"SELECT DISTINCT gosnomer FROM {TABLE} WHERE gosnomer LIKE ? ORDER BY gosnomer ASC", (prefix + "%",)).fetchall()]

def fetch_lists_by_gosnomers(gosnomers):
    if not gosnomers:
        return []
    placeholders = ",".join("?" for _ in gosnomers)
    with get_connection() as conn:
        return [row[0] for row in conn.execute(f"SELECT DISTINCT list FROM {TABLE} WHERE gosnomer IN ({placeholders}) ORDER BY list DESC", gosnomers).fetchall()]

def get_table_columns_info():
    """
    Возвращает (columns_list, set_of_generated_column_names, column_types).
    После удаления GENERATED-полей генерируем пустое множество generated.
    """
    with get_connection() as conn:
        cur = conn.execute(f"PRAGMA table_info({TABLE})")
        info = cur.fetchall()
        names = [row[1] for row in info]
        types = {row[1]: (row[2] or "").upper() for row in info}
    generated = set()  # больше нет вычисляемых полей
    return names, generated, types

def show_record(record):
    if record:
        for col, val in zip(columns, record):
            if col in field_entries:
                # Для числовых колонок показываем "0" если в БД NULL/None,
                # чтобы отличать пустую строку от нуля.
                if val is None:
                    ctype = column_types.get(col, "")
                    if "INT" in ctype or "REAL" in ctype or "NUM" in ctype or "DEC" in ctype:
                        text = "0"
                    else:
                        text = ""
                else:
                    text = str(val)
                set_entry_value(field_entries[col], text, readonly=(col in generated_columns))
    else:
        messagebox.showinfo("Нет данных", "Запись не найдена")

def confirm_list_selection():
    selected = listbox_list.get(tk.ACTIVE)
    record = fetch_record_by_list(selected)
    show_record(record)

def confirm_gosnomer_selection():
    selected = listbox_gosnomer.get(tk.ACTIVE)
    lists = fetch_lists_by_gosnomer(selected)
    update_listbox(listbox_list, lists)

def reset_lists():
    update_listbox(listbox_list, fetch_all_lists())
    update_listbox(listbox_gosnomer, fetch_all_gosnomers())

def update_listbox(listbox, items):
    listbox.delete(0, tk.END)
    for item in items:
        listbox.insert(tk.END, item)

def search_by_prefix(event=None):
    prefix = entry_search.get().strip()
    if not prefix:
        reset_lists()
        return
    gosnomers = fetch_gosnomers_by_prefix(prefix)
    update_listbox(listbox_gosnomer, gosnomers)
    lists = fetch_lists_by_gosnomers(gosnomers)
    update_listbox(listbox_list, lists)

def set_entry_value(entry, text, readonly=False):
    entry.config(state="normal")
    entry.delete(0, tk.END)
    entry.insert(0, text)
    if readonly:
        entry.config(state="readonly")

def clear_form():
    for col, entry in field_entries.items():
        if col in generated_columns:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.config(state="readonly")
        else:
            entry.delete(0, tk.END)

def create_new():
    clear_form()

def save_record():
    # исключаем id и вычисляемые поля из списка для INSERT/UPDATE
    values = {col: field_entries[col].get().strip() for col in columns if col != "id" and col not in generated_columns}
    id_value = field_entries["id"].get().strip()

    with get_connection() as conn:
        cur = conn.cursor()
        if id_value:
            # UPDATE
            if values:
                assignments = ", ".join(f"{col} = ?" for col in values.keys())
                params = tuple(values[k] for k in values.keys()) + (id_value,)
                cur.execute(f"UPDATE {TABLE} SET {assignments} WHERE id = ?", params)
                conn.commit()
                log_change("update", id_value, str(values))
                messagebox.showinfo("Обновлено", f"Запись с id={id_value} обновлена.")
            else:
                messagebox.showinfo("Обновлено", "Нет полей для обновления (возможно все поля вычисляемые).")
        else:
            # INSERT
            if values:
                fields = ", ".join(values.keys())
                placeholders = ", ".join("?" for _ in values)
                cur.execute(f"INSERT INTO {TABLE} ({fields}) VALUES ({placeholders})", tuple(values.values()))
                conn.commit()
                new_id = cur.lastrowid
                field_entries["id"].delete(0, tk.END)
                field_entries["id"].insert(0, str(new_id))
                log_change("insert", new_id, str(values))
                messagebox.showinfo("Создано", f"Создана новая запись с id={new_id}.")
            else:
                messagebox.showwarning("Создание", "Нет полей для вставки (все поля вычисляемые?).")

    reset_lists()
    

def delete_record():
    id_value = field_entries["id"].get().strip()
    if not id_value:
        messagebox.showwarning("Удаление", "Нет id для удаления.")
        return
    with get_connection() as conn:
        conn.execute(f"DELETE FROM {TABLE} WHERE id = ?", (id_value,))
        conn.commit()
    clear_form()
    log_change("delete", id_value, "")
    messagebox.showinfo("Удалено", f"Запись с id={id_value} удалена.")

# Интерфейс
root = tk.Tk()
root.title("Путевые листы — интерфейс")

# Верхняя панель поиска
tk.Label(root, text="Поиск по госномеру:", font=FONT).grid(row=0, column=0, sticky="e")
entry_search = tk.Entry(root, font=FONT)
entry_search.grid(row=0, column=1, sticky="we")
entry_search.bind("<Return>", search_by_prefix)
tk.Button(root, text="Найти", font=FONT, command=search_by_prefix).grid(row=0, column=2, padx=5)

tk.Label(root, text="Поиск по номеру путёвки:", font=FONT).grid(row=0, column=3, sticky="e")
entry_search_list = tk.Entry(root, font=FONT)
entry_search_list.grid(row=0, column=4, sticky="we")
entry_search_list.bind("<Return>", search_by_list)
tk.Button(root, text="Найти путёвку", font=FONT, command=search_by_list).grid(row=0, column=5, padx=5)


# Поля записи
columns, generated_columns, column_types = get_table_columns_info()
print("columns (PRAGMA order):", columns)
print("generated columns:", generated_columns)
print("column types:", column_types)

# гарантируем, что используем ровно тот же порядок, в котором вернул PRAGMA
display_columns = list(columns)

field_entries = {}
# debug - печать порядка полей
for i, col in enumerate(display_columns):
    print(f"FIELD ORDER {i}: {col}")
    tk.Label(root, text=col + ":", font=FONT).grid(row=i+1, column=0, sticky="e")
    entry = tk.Entry(root, font=FONT, width=40)
    entry.grid(row=i+1, column=1, columnspan=2, sticky="we", padx=5, pady=1)
    # вычисляемые поля показываем, но делаем readonly
    if col in generated_columns:
        entry.config(state="readonly")
    field_entries[col] = entry

# Кнопки CRUD
tk.Button(root, text="Создать", font=FONT, command=create_new).grid(row=len(columns)+1, column=0, pady=10)
tk.Button(root, text="Сохранить", font=FONT, command=save_record).grid(row=len(columns)+1, column=1)
tk.Button(root, text="Удалить", font=FONT, command=delete_record).grid(row=len(columns)+1, column=2)
tk.Button(root, text="Очистить форму", font=FONT, command=clear_form).grid(row=len(columns)+2, column=0, columnspan=3, pady=5)

# Списки справа
#tk.Label(root, text="list", font=FONT).grid(row=0, column=3)
tk.Button(root, text="Выбрать list", font=FONT, command=confirm_list_selection).grid(row=1, column=3)
listbox_list = tk.Listbox(root, font=FONT, height=15)
listbox_list.grid(row=2, column=3, rowspan=10, padx=5)

tk.Label(root, text="gosnomer", font=FONT).grid(row=12, column=3)
tk.Button(root, text="Выбрать gosnomer", font=FONT, command=confirm_gosnomer_selection).grid(row=13, column=3)
listbox_gosnomer = tk.Listbox(root, font=FONT, height=10)
listbox_gosnomer.grid(row=14, column=3, rowspan=5, padx=5)

tk.Button(root, text="Сбросить списки", font=FONT, command=reset_lists).grid(row=20, column=3, pady=10)

# Запуск
reset_lists()
root.mainloop()