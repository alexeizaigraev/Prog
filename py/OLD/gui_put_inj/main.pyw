import tkinter as tk
from tkinter import messagebox
import os

FONT = ("Arial", 14)
MONO = ("Courier New", 12)

# Значения по умолчанию
DEFAULT_NORMA_POGR = "12"
DEFAULT_NORMA_EK = "5"
DEFAULT_NORMA_TRANS = "10"
DEFAULT_PRESISSION = "0"

def calculate():
    try:
        speed_start = int(entry_speed_start.get())
        speed_end = int(entry_speed_end.get())
        fuel_rashod = float(entry_fuel_rashod.get())
        presission = float(entry_presission.get())

        norma_pogr = float(entry_norma_pogr.get())
        norma_ek = float(entry_norma_ek.get())
        norma_trans = float(entry_norma_trans.get())

        probeg = speed_end - speed_start
        results = []

        for hour_pogr in range(0, probeg + 1):
            for hour_ek in range(0, probeg - hour_pogr + 1):
                hour_trans = probeg - hour_pogr - hour_ek
                hour_no_move = hour_pogr + hour_ek

                rashod_pogr = hour_pogr * norma_pogr
                rashod_ek = hour_ek * norma_ek
                rashod_trans = hour_trans * norma_trans

                fuel_rashod_calculate = rashod_pogr + rashod_ek + rashod_trans
                razn = abs(fuel_rashod - fuel_rashod_calculate)

                if razn <= presission:
                    results.append([
                        hour_pogr, hour_ek, hour_trans,
                        rashod_pogr, rashod_ek, rashod_trans,
                        hour_no_move, rashod_pogr + rashod_ek,
                        hour_trans, rashod_trans,
                        f"{razn:.2f}"
                    ])

        output_text.delete("1.0", tk.END)
        header = ("h_pogr;h_ek;h_trans;"
                  "r_pogr;r_ek;r_trans;"
                  "h_no_move;r_no_move;"
                  "h_move;r_move;razn\n")
        output_text.insert(tk.END, header)

        if results:
            results.sort(key=lambda x: float(x[-1]))
            with open("result.csv", "w", newline='', encoding="utf-8") as f:
                f.write(header)
                for row in results:
                    line = ";".join(str(x) for x in row) + "\n"
                    f.write(line)
                    output_text.insert(tk.END, line)
        else:
            output_text.insert(tk.END, "Нет подходящих вариантов\n")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка ввода: {e}")

def clear_fields():
    entry_speed_start.delete(0, tk.END)
    entry_speed_end.delete(0, tk.END)
    entry_fuel_rashod.delete(0, tk.END)
    entry_presission.delete(0, tk.END)
    entry_presission.insert(0, DEFAULT_PRESISSION)
    output_text.delete("1.0", tk.END)

def copy_to_clipboard():
    text = output_text.get("1.0", tk.END)
    root.clipboard_clear()
    root.clipboard_append(text)
    messagebox.showinfo("Скопировано", "Результат скопирован в буфер обмена.")

def open_in_excel():
    try:
        os.system('start excel.exe result.csv')
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть Excel: {e}")

# Интерфейс
root = tk.Tk()
root.title("Инженерная техника — расчёт моточасов")

def add_field(label_text, row, default_value="", readonly=False):
    tk.Label(root, text=label_text + ":", font=FONT).grid(row=row, column=0, sticky="e")
    entry = tk.Entry(root, font=FONT)
    entry.grid(row=row, column=1)
    if default_value:
        entry.insert(0, default_value)
    if readonly:
        entry.config(state="readonly")
    return entry

entry_speed_start = add_field("speed_start", 0)
entry_speed_end = add_field("speed_end", 1)
entry_fuel_rashod = add_field("fuel_rashod", 2)
entry_presission = add_field("presission", 3, DEFAULT_PRESISSION)
entry_norma_pogr = add_field("norma_pogr", 4, DEFAULT_NORMA_POGR)
entry_norma_ek = add_field("norma_ek", 5, DEFAULT_NORMA_EK)
entry_norma_trans = add_field("norma_trans", 6, DEFAULT_NORMA_TRANS)

tk.Button(root, text="Рассчитать", font=FONT, command=calculate).grid(row=7, column=0, pady=10)
tk.Button(root, text="Очистить поля", font=FONT, command=clear_fields).grid(row=7, column=1, pady=10)

output_text = tk.Text(root, font=MONO, width=100, height=20)
output_text.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

tk.Button(root, text="Копировать результат", font=FONT, command=copy_to_clipboard).grid(row=9, column=0, pady=5)
tk.Button(root, text="Открыть в Excel", font=FONT, command=open_in_excel).grid(row=9, column=1, pady=5)

root.mainloop()