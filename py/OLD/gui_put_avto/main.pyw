import tkinter as tk
from tkinter import messagebox
import os

FONT = ("Arial", 14)
MONO = ("Courier New", 12)

# Значения по умолчанию
DEFAULT_KOEF_TRASSA = "0.85"
DEFAULT_KOEF_GOROD = "1.05"
DEFAULT_KOEF_BEZDOR = "1.3"
DEFAULT_PRESISSION = "0"

script_dir = os.path.dirname(os.path.abspath(__file__))
result_path = os.path.join(script_dir, "result.csv")

def calculate():
    try:
        speed_start = int(entry_speed_start.get())
        speed_end = int(entry_speed_end.get())
        fuel_rashod = float(entry_fuel_rashod.get())
        norma_rashod = float(entry_norma_rashod.get())
        presission = float(entry_presission.get())

        koef_trassa = float(entry_koef_trassa.get())
        koef_gorod = float(entry_koef_gorod.get())
        koef_bezdor = float(entry_koef_bezdor.get())

        probeg = speed_end - speed_start
        max_bezdor = int(probeg * 0.3)

        results = []

        for probeg_bezdor in range(0, max_bezdor + 1):
            for probeg_trassa in range(0, probeg - probeg_bezdor + 1):
                probeg_city = probeg - probeg_trassa - probeg_bezdor
                if probeg_city < 0:
                    continue

                rashod_trassa = probeg_trassa * koef_trassa * norma_rashod / 100
                rashod_city = probeg_city * koef_gorod * norma_rashod / 100
                rashod_bezdor = probeg_bezdor * koef_bezdor * norma_rashod / 100

                fuel_rashod_calculate = rashod_trassa + rashod_city + rashod_bezdor
                razn = abs(fuel_rashod - fuel_rashod_calculate)

                if razn <= presission:
                    results.append([
                        probeg_trassa, probeg_city, probeg_bezdor,
                        f"{rashod_trassa:.2f}", f"{rashod_city:.2f}", f"{rashod_bezdor:.2f}",
                        f"{razn:.2f}"
                    ])

        output_text.delete("1.0", tk.END)
        header = "probeg_trassa;probeg_city;probeg_bezdor;rashod_trassa;rashod_city;rashod_bezdor;razn\n"
        output_text.insert(tk.END, header)

        if results:
            results.sort(key=lambda x: float(x[-1]))
            with open(result_path, "w", newline='', encoding="utf-8") as f:
                f.write(header)
                for row in results:
                    line = ";".join(str(x) for x in row) + "\n"
                    f.write(line)
                    output_text.insert(tk.END, line)
        else:
            min_razn = float("inf")
            for probeg_bezdor in range(0, max_bezdor + 1):
                for probeg_trassa in range(0, probeg - probeg_bezdor + 1):
                    probeg_city = probeg - probeg_trassa - probeg_bezdor
                    if probeg_city < 0:
                        continue
                    fuel_rashod_calculate = (
                        probeg_trassa * koef_trassa +
                        probeg_city * koef_gorod +
                        probeg_bezdor * koef_bezdor
                    ) * norma_rashod / 100
                    razn = abs(fuel_rashod - fuel_rashod_calculate)
                    if razn < min_razn:
                        min_razn = razn
            output_text.insert(tk.END, f"{min_razn:.2f} # no result\n")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка ввода: {e}")

def clear_fields():
    for entry in [
        entry_speed_start, entry_speed_end,
        entry_fuel_rashod, entry_norma_rashod
    ]:
        entry.delete(0, tk.END)
    entry_koef_trassa.delete(0, tk.END)
    entry_koef_trassa.insert(0, DEFAULT_KOEF_TRASSA)
    entry_koef_gorod.delete(0, tk.END)
    entry_koef_gorod.insert(0, DEFAULT_KOEF_GOROD)
    entry_koef_bezdor.delete(0, tk.END)
    entry_koef_bezdor.insert(0, DEFAULT_KOEF_BEZDOR)
    entry_presission.delete(0, tk.END)
    entry_presission.insert(0, DEFAULT_PRESISSION)
    output_text.delete("1.0", tk.END)

def copy_to_clipboard():
    text = output_text.get("1.0", tk.END)
    root.clipboard_clear()
    root.clipboard_append(text)
    messagebox.showinfo("Скопировано", "Результат с заголовками скопирован в буфер обмена.")

def open_in_excel():
    try:
        if os.path.exists(result_path):
            os.startfile(result_path)
        else:
            messagebox.showerror("Ошибка", "Файл результата не найден")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть Excel: {e}")

# Интерфейс
root = tk.Tk()
root.title("Путевой лист")

def add_field(label_text, row, default_value=""):
    tk.Label(root, text=label_text + ":", font=FONT).grid(row=row, column=0, sticky="e")
    entry = tk.Entry(root, font=FONT)
    entry.grid(row=row, column=1)
    if default_value:
        entry.insert(0, default_value)
    return entry

entry_speed_start = add_field("speed_start", 0)
entry_speed_end = add_field("speed_end", 1)
entry_fuel_rashod = add_field("fuel_rashod", 2)
entry_norma_rashod = add_field("norma_rashod", 3)
entry_koef_trassa = add_field("koef_trassa", 4, DEFAULT_KOEF_TRASSA)
entry_koef_gorod = add_field("koef_gorod", 5, DEFAULT_KOEF_GOROD)
entry_koef_bezdor = add_field("koef_bezdor", 6, DEFAULT_KOEF_BEZDOR)
entry_presission = add_field("presission", 7, DEFAULT_PRESISSION)

tk.Button(root, text="Рассчитать", font=FONT, command=calculate).grid(row=8, column=0, pady=10)
tk.Button(root, text="Очистить поля", font=FONT, command=clear_fields).grid(row=8, column=1, pady=10)

output_text = tk.Text(root, font=MONO, width=90, height=20)
output_text.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

tk.Button(root, text="Копировать результат", font=FONT, command=copy_to_clipboard).grid(row=10, column=0, pady=5)
tk.Button(root, text="Открыть в Excel", font=FONT, command=open_in_excel).grid(row=10, column=1, pady=5)

root.mainloop()