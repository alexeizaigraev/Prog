import pandas as pd
import os
import subprocess
from datetime import datetime
import re

# --- 1. СЛОВАРЬ СОКРАЩЕНИЙ ДЛЯ ЗАПОЛНЕНИЯ ДНЕЙ ---
SHEET_MAPPING = {
    "Наявність (105)": "наявн_105",
    "Прирядженні (105)": "прир_105",
    "Виведені (105)": "вив_105",
    "Наявні ЧОРНОБИЛЬ": "наявн_чорн",
    "ДЛЯ ДОВІДОК та НОТАТОК 1 рота": "дов_1_рота",
    "ДЛЯ ДОВІДОК та НОТАТОК 2 рота": "дов_2_рота",
    "ДЛЯ ДОВІДОК та НОТАТОК РУБАК": "дов_рубак",
    "ДЛЯ ДОВІДОК та НОТАТОК зведена": "дов_звед",
    "ДЛЯ ДОВІДОК та НОТАТОК РЕБ": "дов_реб",
    "ДЛЯ ДОВІДОК та НОТАТОК інші час": "дов_інші",
    "Аркуш8": "аркуш_8",
    "ДЛЯ ДОВІДОК УОС ХАРКІВ 1 рота": "дов_харк_1_рота",
    "ДЛЯ ДОВІДОК УОС ХАРКІВ 2 рота": "дов_харк_2_рота",
    "Наявні УОС ХАРКІВ": "харк_наявн",
    "Приряджені УОС ХАРКІВ": "харк_прир",
    "Інші ВЧ УОС ХАРКІВ": "харк_інші",
    "Виведені УОС ХАРКІВ": "харк_вивед",
    "Приряджені Подпорядкування 36ош": "36_ош_прир",
    "Інші ВЧ 12 АК": "12_ак_інші",
    "Наявні 15 АК": "15_ак_наявн",
    "Приряджені 15 АК": "15_ак_прир",
    "Інші ВЧ 15 АК": "15_ак_інші",
    "Наявні 18 АК": "18_ак_наявн",
    "Приряджені 18 АК": "18_ак_прир",
    "Інші ВЧ 18 АК": "інші_18_ак",
    "Приряджені УВ(с) \"Захід\"": "захід_прир",
    "Виведені УВ(с) \"Захід\"": "захід_вив",
    "Орлівка": "орлівка",
    "Наявні УВ(с) Захід 101 ТРО": "захід_101_наявн",
    "Приряджені УВ(с) Захід 101 ТРО": "захід_101_прир",
    "Інші ВЧ УВ(с) Захід 101 ТРО": "захід_101_інші",
    "Виведені УВ(с) Захід 101 ТРО": "захід_101_вив",
    "Наявні УВ(с) Захід 104 ТРО": "захід_104_наявн",
    "Приряджені УВ(с) Захід 104 ТРО": "захід_104_прир",
    "Інші ВЧ УВ(с) Захід 104 ТРО": "захід_104_інші",
    "Виведені УВ(с) Захід 104 ТРО": "захід_104_вив"
}

# --- 2. ФУНКЦИИ ОЧИСТКИ И КАТЕГОРИЗАЦИИ ---
def clean_text(text):
    if pd.isna(text) or text == "": return ""
    text = str(text).replace("\n", " ").replace("\r", " ").replace("\t", " ")
    text = text.replace("'", "’").replace(";", "").replace('"', "")
    text = " ".join(text.split())
    return text.strip()

def get_category(rank):
    r = clean_text(rank).lower()
    if not r: return None
    
    # ВОТ ОНИ — ТВОИ СПИСКИ ДЛЯ КАТЕГОРИЙ:
    soldiers = ["солдат", "старший солдат"]
    sergeants = ["сержантський і старшинський склад", "молодший сержант", "сержант", "старший сержант", "головний сержант", "штаб-сержант", "майстер-сержант", "старший майстер-сержант", "головний майстер-сержант"]
    officers = ["офіцерський склад", "молодший лейтенант", "лейтенант", "старший лейтенант", "капітан", "майор", "підполковник", "полковник", "бригадний генерал", "генерал-майор", "генерал-лейтенант", "генерал"]
    
    if any(x in r for x in soldiers): return "солдати"
    if any(x in r for x in sergeants): return "сержанти"
    if any(x in r for x in officers): return "офіцери"
    return None

# --- 3. НАСТРОЙКИ ПУТЕЙ ---
in_path = r"D:\Data\InData\Excel\БІП розподіл по бригаді 105 та 117.xlsx"
out_path = r"D:\Data\OutData\Excel\ProstynyaOut.xlsx"
log_path = r"D:\Data\OutData\Excel\Report.txt"

report_text = []

# --- 4. ОСНОВНОЙ ЦИКЛ ОБРАБОТКИ ---
try:
    if not os.path.exists(in_path):
        raise FileNotFoundError(f"Файл не найден по пути: {in_path}")

    # Проверка актуальности файла
    file_mtime = datetime.fromtimestamp(os.path.getmtime(in_path)).date()
    if file_mtime != datetime.now().date():
        msg = f"ВНИМАНИЕ: Входной файл НЕ СЕГОДНЯШНИЙ! Дата изменения: {file_mtime}"
        report_text.append(msg + "\n")

    xl = pd.ExcelFile(in_path)
    all_dfs = []

    for sheet_name in xl.sheet_names:
        df = xl.parse(sheet_name)
        cols = df.columns.astype(str).tolist()

        def find_col(target):
            for c in cols:
                if target.lower() in c.lower(): return c
            return None

        col_zv = find_col("Звання")
        col_pib = find_col("ПІБ")
        col_pos = find_col("Посада")

        if col_zv and col_pib:
            # Сохраняем структуру от Звания и вправо
            start_idx = cols.index(col_zv)
            df = df.iloc[:, start_idx:].copy()
            
            # Очистка ключевых полей
            df[col_zv] = df[col_zv].apply(clean_text)
            df[col_pib] = df[col_pib].apply(clean_text)
            
            # Удаляем пустые строки
            df = df[~((df[col_zv] == "") & (df[col_pib] == ""))]
            if df.empty: continue

            # ПРИСВОЕНИЕ КАТЕГОРИИ (СОЛДАТИ/СЕРЖАНТИ/ОФІЦЕРИ)
            df['вид'] = df[col_zv].apply(get_category)
            
            # Лог неопределенных для Блокнота
            unknown = df[df['вид'].isnull() & (df[col_zv] != "")]
            if not unknown.empty:
                header = f"\n[КАТЕГОРИИ] Вкладка: {sheet_name}"
                report_text.append(header)
                for _, row in unknown.iterrows():
                    report_text.append(f"  - Не определено: {row[col_zv]} | {row[col_pib]}")
            
            # Очистка всех остальных данных
            for c in df.columns:
                if c not in ['вид', col_zv, col_pib]:
                    df[c] = df[c].apply(clean_text)

            current_sheet = sheet_name.strip()
            df['Вкладка-источник'] = current_sheet
            
            # Код для дней
            fill_name = SHEET_MAPPING.get(current_sheet, current_sheet)

            # --- ГАРАНТИРОВАННОЕ ЗАПОЛНЕНИЕ ДНЕЙ ---
            for day in range(1, 32):
                df[day] = fill_name
                    
            all_dfs.append(df)

    if all_dfs:
        # Сборка финала
        final_result = pd.concat(all_dfs, ignore_index=True, sort=False)
        report_text.append(f"\nОБРАБОТАНО ЗАПИСЕЙ: {len(final_result)}")

        # Поиск дублей
        c_zv = [c for c in final_result.columns if "звання" in str(c).lower()][0]
        c_pib = [c for c in final_result.columns if "піб" in str(c).lower()][0]
        
        duplicates = final_result[final_result.duplicated(subset=[c_zv, c_pib], keep=False)]
        if not duplicates.empty:
            report_text.append("\n" + "!"*20 + " ОБНАРУЖЕНЫ ДУБЛИКАТЫ " + "!"*20)
            grouped = duplicates.groupby([c_zv, c_pib])
            for name_tuple, group in grouped:
                report_text.append(f"ДУБЛЬ: {name_tuple[0]} | {name_tuple[1]}")
                for s in group['Вкладка-источник'].unique():
                    report_text.append(f"  - {s}")
            report_text.append("!"*61 + "\n")
        
        # Финальный порядок колонок
        day_cols = list(range(1, 32))
        fixed_end = ['Вкладка-источник'] + day_cols
        mid_cols = [c for c in final_result.columns if c not in fixed_end and c != 'вид']
        final_result = final_result[['вид'] + mid_cols + fixed_end]
        
        final_result.to_excel(out_path, index=False)
        
        # Сохранение лога и запуск блокнота
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_text))
        subprocess.Popen(['notepad.exe', log_path])

        print(f"ГОТОВО! Результат: {out_path}")

except Exception as e:
    print(f"ОШИБКА: {e}")