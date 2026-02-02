import pandas as pd
import re
import calendar
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

# Твои модули
from modules import * # --- БЛОК 1: КОНТЕКСТ И ЛОГИКА ДАТ ---

def get_now_context():
    now = datetime.now()
    return {
        'year': str(now.year),
        'month': f"{now.month:02d}", 
        'month_int': now.month,
        'year_int': now.year
    }

def get_last_day_of_month(ctx):
    last_day = calendar.monthrange(ctx['year_int'], ctx['month_int'])[1]
    return datetime(ctx['year_int'], ctx['month_int'], last_day)

def to_date_obj(date_str, ctx):
    if not date_str: 
        return None
    clean = date_str.strip().rstrip('.')
    try:
        day, month = map(int, clean.split('.'))
        return datetime(ctx['year_int'], month, day)
    except ValueError:
        return None

def date_to_str(date_obj):
    return date_obj.strftime("%d.%m.%Y")

def parse_existing_dates(text_col):
    if not text_col or pd.isna(text_col) or str(text_col).strip() == '*':
        return []
    dates = []
    parts = str(text_col).split('\n')
    for p in parts:
        p = p.strip()
        if not p: 
            continue
        try:
            dates.append(datetime.strptime(p, "%d.%m.%Y"))
        except ValueError:
            pass
    return dates

# --- БЛОК 2: ОБРАБОТКА СТРОК ---

def extract_digits_and_dots(text: str) -> str:
    return "".join(ch for ch in str(text) if ch.isdigit() or ch == ".")

def make_vvedenia_1(date_str: str, ctx) -> str:
    if not date_str or pd.isna(date_str):
        return f"01.{ctx['month']}.{ctx['year']}"
    
    clean_str = extract_digits_and_dots(date_str)
    parts = [p for p in clean_str.strip().split(".") if p]
    
    if not parts:
        return f"01.{ctx['month']}.{ctx['year']}"
    
    results = []
    for i in range(0, len(parts) - 1, 2):
        day, month = parts[i].zfill(2), parts[i+1].zfill(2)
        if month == ctx['month']:
            results.append(f"{day}.{ctx['month']}.{ctx['year']}")
        elif month < ctx['month'] or month == '12':
            results.append(f"01.{ctx['month']}.{ctx['year']}")
        else:
            results.append('*')
    return " \n".join(results) if results else '*'

def analyze_vyvedenia_text(text, ctx, row_idx):
    if not text or pd.isna(text):
        return [], [get_last_day_of_month(ctx)]
    
    text = str(text)
    all_dates_matches = re.findall(r'(\d{1,2})\.(\d{1,2})', text)
    
    for d_str, m_str in all_dates_matches:
        if int(m_str) != ctx['month_int']:
            print(f"(!) Внимание: Строка {row_idx + 2}. Неверный месяц ({m_str}) в тексте: '{text}'")
            return None, None
            
    entry_additions, exit_list = [], []
    
    # 1. Сначала диапазоны " з ... по ... "
    range_pattern = re.compile(r'(?:^|\s)з\s+(\d{1,2}\.\d{1,2}\.?)\s+по\s+(\d{1,2}\.\d{1,2}\.?)', re.IGNORECASE)
    ranges = range_pattern.findall(text)
    
    for d1_str, d2_str in ranges:
        dt1, dt2 = to_date_obj(d1_str, ctx), to_date_obj(d2_str, ctx)
        if dt1 and dt2:
            exit_list.append(dt1 - timedelta(days=1))
            entry_additions.append(dt2 + timedelta(days=1))
            
    # 2. Убираем диапазоны и ищем одиночные даты
    text_clean = range_pattern.sub(' ', text)
    singles = re.findall(r'(\d{1,2}\.\d{1,2}\.?)', text_clean)
    
    for d_str in singles:
        dt = to_date_obj(d_str, ctx)
        if dt:
            exit_list.append(dt - timedelta(days=1))
            entry_additions.append(dt + timedelta(days=1))
            
    return entry_additions, exit_list

# --- БЛОК 3: СОХРАНЕНИЕ И ИНТЕРФЕЙС ---

def save_to_excel(records, out_path, sheet_name):
    df = pd.DataFrame(records)
    with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        ws = writer.sheets[sheet_name]
        from openpyxl.styles import Alignment
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                if cell.value and isinstance(cell.value, str) and '\n' in cell.value:
                    cell.alignment = Alignment(wrapText=True, vertical='top')

def start_processing(sheet_name):
    ctx = get_now_context()
    try:
        records = get_records_by_sheet(sheet_name)
        for idx, record in enumerate(records):
            # Шаг 1: Введення 1
            val_vved_1 = make_vvedenia_1(record.get('Дата введення', ''), ctx)
            record['Дата введення 1'] = val_vved_1
            
            # Шаг 2: Анализ вывода и Введення 2
            entry_adds, exit_res = analyze_vyvedenia_text(record.get('Дата виведення'), ctx, idx)
            if entry_adds is None:
                record['Дата введення 2'], record['Дата виведення 2'] = '*', '*'
                continue
                
            f_entry = parse_existing_dates(val_vved_1) + entry_adds
            f_entry.sort()
            record['Дата введення 2'] = "\n".join([date_to_str(d) for d in f_entry])
            
            exit_res.sort()
            record['Дата виведення 2'] = "\n".join([date_to_str(d) for d in exit_res])

        out_path = f"D:/Data/OutData/Excel/out_{sheet_name}.xlsx"
        save_to_excel(records, out_path, sheet_name)
        messagebox.showinfo("Готово", f"Файл успешно сохранен:\n{out_path}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при обработке:\n{str(e)}")

# --- ИНТЕРФЕЙС TKINTER ---

def run_gui():
    root = tk.Tk()
    root.title("Az-Phenomenology: Excel Processor")
    root.geometry("450x350")

    label = tk.Label(root, text="Выберите вкладку для обработки:", pady=15, font=("Arial", 10, "bold"))
    label.pack()

    try:
        sheet_names = get_sheet_names(in_path)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{str(e)}")
        return

    combo = ttk.Combobox(root, values=sheet_names, state="readonly", width=50)
    combo.pack(pady=10)
    if sheet_names: 
        combo.current(0)

    def on_submit():
        selected_sheet = combo.get()
        if selected_sheet:
            # Небольшое уведомление в консоль перед стартом
            print(f"Запуск обработки листа: {selected_sheet}...")
            root.destroy() 
            start_processing(selected_sheet)

    btn = tk.Button(
        root, 
        text="Запустить обработку", 
        command=on_submit, 
        bg="#2E7D32", 
        fg="white", 
        font=("Arial", 10, "bold"),
        padx=20, 
        pady=10
    )
    btn.pack(pady=30)

    root.mainloop()

if __name__ == "__main__":
    run_gui()