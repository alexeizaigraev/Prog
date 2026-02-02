import pandas as pd
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import pyperclip
import os
from datetime import datetime

# Настройки путей
IN_PATH = r"D:\Data\InData\Excel\Простыня-Сводная.xlsx"

# Строгие крупные шрифты
FONT_BIG = ("Arial", 22, "bold")
FONT_MEDIUM = ("Arial", 18)
FONT_RESULT = ("Consolas", 18)

class AnalyticsApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Аналитика: Сводка по дням")
        self.geometry("1150x900")
        ctk.set_appearance_mode("dark")

        if not os.path.exists(IN_PATH):
            messagebox.showerror("Ошибка", f"Файл не найден:\n{IN_PATH}")
            self.destroy()
            return

        try:
            self.df = pd.read_excel(IN_PATH)
            self.df.columns = [str(c).strip() for c in self.df.columns]
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать Excel:\n{e}")
            self.destroy()
            return

        self.create_widgets()

    def create_widgets(self):
        # 1. Выбор дня
        ctk.CTkLabel(self, text="1. Выбери день месяца:", font=FONT_BIG).pack(pady=(20, 5))
        
        self.days = [str(i) for i in range(1, 32)]
        self.current_day_str = str(datetime.now().day)
        self.day_var = ctk.StringVar(value=self.current_day_str)
        
        self.day_combo = ctk.CTkComboBox(self, values=self.days, variable=self.day_var, font=FONT_MEDIUM, height=45)
        self.day_combo.pack(pady=10)

        # 2. Выбор вкладок
        ctk.CTkLabel(self, text="2. Выбор вкладок (Ctrl+клик):", font=FONT_BIG).pack(pady=(10, 5))
        unique_sheets = sorted([str(s) for s in self.df['Вкладка-источник'].dropna().unique()])

        self.sheet_listbox = tk.Listbox(self, selectmode="multiple", font=FONT_MEDIUM, 
                                        bg="#2b2b2b", fg="white", height=6, 
                                        selectbackground="#1f538d", borderwidth=0)
        for s in unique_sheets:
            self.sheet_listbox.insert(tk.END, s)
        self.sheet_listbox.pack(pady=5, padx=20, fill="x")

        # Кнопки управления
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)

        self.btn_calc = ctk.CTkButton(button_frame, text="СДЕЛАТЬ СВОДКУ", font=FONT_BIG, 
                                      height=60, width=250, command=self.calculate)
        self.btn_calc.pack(side="left", padx=10)

        self.btn_copy = ctk.CTkButton(button_frame, text="КОПИРОВАТЬ", font=FONT_BIG, 
                                      fg_color="#228B22", height=60, width=250, command=self.copy_to_clipboard)
        self.btn_copy.pack(side="left", padx=10)

        self.btn_clear = ctk.CTkButton(button_frame, text="ОЧИСТИТЬ", font=FONT_BIG, 
                                       fg_color="#B22222", hover_color="#8B0000",
                                       height=60, width=250, command=self.clear_all)
        self.btn_clear.pack(side="left", padx=10)

        # Поле вывода
        self.result_text = ctk.CTkTextbox(self, font=FONT_RESULT, width=1100, height=450)
        self.result_text.pack(pady=10, padx=20, fill="both", expand=True)

    def format_line(self, label, data):
        """Строго по твоему примеру: Название – Сумма (О-С-С)"""
        counts = data['вид'].value_counts()
        off = counts.get('офіцери', 0)
        ser = counts.get('сержанти', 0)
        sol = counts.get('солдати', 0)
        total = off + ser + sol
        return f"{label} – {total} ({off}-{ser}-{sol})"

    def calculate(self):
        day_val = self.day_var.get().strip()
        
        if day_val not in self.df.columns:
            messagebox.showerror("Ошибка", f"Колонка дня '{day_val}' не найдена!")
            return

        selected_indices = self.sheet_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Внимание", "Выбери хотя бы одну вкладку!")
            return

        self.result_text.delete("1.0", tk.END)
        output = []
        output.append(f"ОТЧЕТ НА {day_val}-е ЧИСЛО:")
        output.append("=" * 50 + "\n")

        for i in selected_indices:
            sheet_name = self.sheet_listbox.get(i)
            sheet_data = self.df[self.df['Вкладка-источник'] == sheet_name]
            
            if sheet_data.empty:
                continue

            output.append(self.format_line(sheet_name, sheet_data))
            
            day_content = sheet_data.dropna(subset=[day_val])
            if not day_content.empty:
                unique_codes = sorted(day_content[day_val].astype(str).unique())
                main_codes = [c for c in unique_codes if "ДПУ" not in c]
                for code in main_codes:
                    code_data = day_content[day_content[day_val].astype(str) == code]
                    line = self.format_line(code, code_data)
                    
                    dpu_variant = f"{code} ДПУ"
                    if dpu_variant in unique_codes:
                        dpu_data = day_content[day_content[day_val].astype(str) == dpu_variant]
                        dpu_stats = self.format_line("", dpu_data).replace(" – ", "").strip()
                        line += f", з них ДПУ – {dpu_stats}"
                    
                    output.append(line)
            
            output.append("") 

        self.result_text.insert("1.0", "\n".join(output))

    def clear_all(self):
        """Сброс всех полей и результатов"""
        # Очистка текста
        self.result_text.delete("1.0", tk.END)
        # Сброс выделения в списке вкладок
        self.sheet_listbox.selection_clear(0, tk.END)
        # Сброс дня на текущий
        self.day_var.set(self.current_day_str)
        self.day_combo.set(self.current_day_str)

    def copy_to_clipboard(self):
        content = self.result_text.get("1.0", tk.END).strip()
        if content:
            pyperclip.copy(content)
            self.btn_copy.configure(text="СКОПИРОВАНО!")
            self.after(1000, lambda: self.btn_copy.configure(text="КОПИРОВАТЬ"))

if __name__ == "__main__":
    app = AnalyticsApp()
    app.mainloop()