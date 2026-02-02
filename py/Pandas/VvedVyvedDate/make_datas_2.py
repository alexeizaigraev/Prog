import pandas as pd
from datetime import datetime
from modules import * # Предполагаем, что здесь get_records_by_sheet, get_sheet_names, in_path

# --- БЛОК ЛОГИКИ (ЧИСТЫЕ ФУНКЦИИ) ---

def get_now_context():
    """Получаем текущую дату один раз для всей программы"""
    now = datetime.now()
    return {
        'year': str(now.year),
        'month': f"{now.month:02d}"
    }

def extract_digits_and_dots(text: str) -> str:
    """Оставляет в строке только цифры и точки"""
    return "".join(ch for ch in str(text) if ch.isdigit() or ch == ".")

def format_date_part(day, month, ctx):
    """Преобразует пару день/месяц в итоговую дату согласно правилам"""
    # Дополняем нулями для корректного сравнения и отображения
    day = str(day).strip().zfill(2)
    month = str(month).strip().zfill(2)
    
    if month == ctx['month']:
        return f"{day}.{ctx['month']}.{ctx['year']}"
    elif month < ctx['month'] or month == '12':
        return f"01.{ctx['month']}.{ctx['year']}"
    return '*'

def process_complex_date(date_str: str, ctx) -> str:
    """Разбирает строку с датами любой длины"""
    if not date_str or pd.isna(date_str):
        return f"01.{ctx['month']}.{ctx['year']}"
    
    clean_str = extract_digits_and_dots(date_str)
    parts = clean_str.strip().split(".")
    
    # Убираем пустые элементы, если они возникли при сплите
    parts = [p for p in parts if p]
    
    if not parts:
        return f"01.{ctx['month']}.{ctx['year']}"
    
    # Собираем даты парами (день + месяц)
    results = []
    for i in range(0, len(parts) - 1, 2):
        formatted = format_date_part(parts[i], parts[i+1], ctx)
        results.append(formatted)
        
    return " \n".join(results) if results else '*'

# --- БЛОК ПРОЦЕССИНГА ---

def run_processing(records, ctx):
    """Основной цикл обработки записей"""
    for record in records:
        original_date = record.get('Дата введення', '')
        record['Дата введення 1'] = process_complex_date(original_date, ctx)

def save_to_excel(records, file_path, sheet_name):
    """Сохранение результата"""
    df = pd.DataFrame(records)
    # Применяем перенос строк сразу при сохранении через стили (опционально)
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Настройка переноса строк в колонке с новой датой
        ws = writer.sheets[sheet_name]
        from openpyxl.styles import Alignment
        for row in ws.iter_rows(min_col=df.columns.get_loc('Дата введення 1') + 1):
            for cell in row:
                cell.alignment = Alignment(wrapText=True, vertical='top')

# --- ГЛАВНЫЙ ЗАПУСК ---

if __name__ == "__main__":
    # 1. Инициализация контекста
    ctx = get_now_context()
    
    # 2. Получение данных
    show_vkladki()
    activ_vkladka_num = 13
    all_sheets = get_sheet_names(in_path)
    
    if activ_vkladka_num < len(all_sheets):
        activ_vkladka_name = all_sheets[activ_vkladka_num]
        print(f"Обработка листа: {activ_vkladka_name}")
        
        records = get_records_by_sheet(activ_vkladka_name)
        
        # 3. Обработка
        run_processing(records, ctx)
        
        # 4. Вывод для проверки
        for record in records[:5]: # Показываем первые 5 для контроля
            print(f"{record.get('Дата введення')} -> {record.get('Дата введення 1')}")
            
        # 5. Сохранение
        out_path = f"D:/Data/OutData/Excel/out_{activ_vkladka_name}.xlsx"
        save_to_excel(records, out_path, activ_vkladka_name)
        
        print(f"\nГотово! Контекст: {ctx['month']}.{ctx['year']}")
        print(f"Файл сохранен: {out_path}")
    else:
        print("Ошибка: Индекс вкладки вне диапазона.")