import pandas as pd
import re
import calendar
from datetime import datetime, timedelta

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def get_last_day_of_month(ctx):
    """Возвращает последний день текущего месяца в формате dd.mm.yyyy"""
    year = int(ctx['year'])
    month = int(ctx['month'])
    last_day = calendar.monthrange(year, month)[1]
    return f"{last_day:02d}.{ctx['month']}.{ctx['year']}"

def to_date_obj(date_str, ctx):
    """Превращает строку 'dd.mm' или 'dd.mm.' в объект datetime с текущим годом"""
    clean_str = date_str.strip().rstrip('.') # Убираем точку в конце, если есть
    try:
        day, month = map(int, clean_str.split('.'))
        return datetime(int(ctx['year']), month, day)
    except ValueError:
        return None

def date_to_str(date_obj):
    """Возвращает дату в формате dd.mm.yyyy"""
    return date_obj.strftime("%d.%m.%Y")

def parse_dates_from_col1(text_col1):
    """Парсит уже существующие даты из 'Дата введення 1' (там могут быть переносы строк)"""
    if not text_col1 or pd.isna(text_col1):
        return []
    
    dates = []
    # Разбиваем по переносу строки, чистим от мусора
    parts = str(text_col1).split('\n')
    for p in parts:
        p = p.strip()
        if not p or p == '*': continue
        
        # Ожидаем формат dd.mm.yyyy
        try:
            dt = datetime.strptime(p, "%d.%m.%Y")
            dates.append(dt)
        except ValueError:
            pass 
    return dates

# --- ОСНОВНАЯ ЛОГИКА АНАЛИЗА ---

def analyze_text_dates(text, ctx):
    """
    Анализирует текст 'Дата виведення', находит периоды и одиночные даты.
    Возвращает кортеж (список_для_введення, список_для_виведення) или (None, None) при ошибке месяца.
    """
    # 1. Проверка на пустой текст
    if not text or pd.isna(text):
        # Если пусто -> Дата виведення = конец месяца. 
        # В "введение" ничего не добавляем (согласно твоему описанию для пустого поля)
        last_day = datetime.strptime(get_last_day_of_month(ctx), "%d.%m.%Y")
        return [], [last_day]

    text = str(text)
    
    # 2. Предварительная проверка: все ли даты относятся к текущему месяцу?
    # Ищем все вхождения dd.mm
    all_dates_matches = re.findall(r'(\d{1,2})\.(\d{1,2})', text)
    current_month_int = int(ctx['month'])
    
    for _, m_str in all_dates_matches:
        if int(m_str) != current_month_int:
            return None, None # Ошибка месяца -> вернем признак ошибки

    # Списки для накопления дат (храним объекты datetime)
    entry_additions = [] # Добавка к дате введення
    exit_additions = []  # Добавка к дате виведення

    # 3. ПОИСК ДИАПАЗОНОВ: " з 26.01. по 31.01."
    # Регулярка ищет: " з ", пробелы, дату1, " по ", пробелы, дату2
    # Используем ignorecase, чтобы ловить и " з " и " З "
    range_pattern = re.compile(r'(?:^|\s)з\s+(\d{1,2}\.\d{1,2}\.?)\s+по\s+(\d{1,2}\.\d{1,2}\.?)', re.IGNORECASE)
    
    # Находим все диапазоны
    ranges = range_pattern.findall(text)
    
    for d1_str, d2_str in ranges:
        dt1 = to_date_obj(d1_str, ctx)
        dt2 = to_date_obj(d2_str, ctx)
        
        if dt1 and dt2:
            # В массив выведения: дата, на 1 день РАНЬШЕ первой
            exit_additions.append(dt1 - timedelta(days=1))
            # В массив введения: дата, на 1 день ПОЗЖЕ второй
            entry_additions.append(dt2 + timedelta(days=1))

    # Удаляем найденные диапазоны из текста, чтобы не спутать даты внутри них с "одиночными"
    # Заменяем их на пробелы, чтобы не склеить слова
    text_without_ranges = range_pattern.sub(' ', text)

    # 4. ПОИСК ОДИНОЧНЫХ ДАТ (тех, что остались)
    # Ищем просто dd.mm., но исключаем случаи, если вдруг перед ними "по" или "з" остались (хотя мы их вычистили)
    single_pattern = re.compile(r'(?<!з\s)(?<!по\s)(\d{1,2}\.\d{1,2}\.?)', re.IGNORECASE)
    # Нюанс regex: (?<!...) это lookbehind - "перед которым нет". 
    # Но так как мы удалили диапазоны "з ... по ...", простой поиск дат в остатке текста сработает корректно для "одиночек".
    
    singles = re.findall(r'(\d{1,2}\.\d{1,2}\.?)', text_without_ranges)
    
    for d_str in singles:
        dt = to_date_obj(d_str, ctx)
        if dt:
            # Для одиночной даты:
            # Выведение: на 1 день раньше найденной
            exit_additions.append(dt - timedelta(days=1))
            # Введение: на 1 день позже найденной
            entry_additions.append(dt + timedelta(days=1))

    return entry_additions, exit_additions


def process_record_v2(record, ctx):
    """Функция обработки одной записи для создания полей версии 2"""
    
    raw_text_out = record.get('Дата виведення')
    
    # Получаем списки дат для добавления
    entry_adds, exit_adds = analyze_text_dates(raw_text_out, ctx)
    
    # --- ОБРАБОТКА ОШИБКИ МЕСЯЦА ---
    if entry_adds is None: # Признак ошибки "*"
        record['Дата введення 2'] = '*' # Или оставить как было? По логике, если ошибка, то выходим
        record['Дата виведення 2'] = '*' # Или "Дата виведення 1" = "*"
        # В твоем задании: "ставим в поле 'Дата виведення 1' символ '*' и выходим".
        # Здесь я ставлю '*' в итоговые поля.
        return

    # --- СБОРКА "Дата введення 2" ---
    # 1. Берем даты из "Дата введення 1"
    existing_entry_dates = parse_dates_from_col1(record.get('Дата введення 1'))
    
    # 2. Объединяем с новыми вычисленными датами
    all_entry_dates = existing_entry_dates + entry_adds
    
    # 3. Сортируем
    all_entry_dates.sort()
    
    # 4. Собираем в строку
    record['Дата введення 2'] = "\n".join([date_to_str(d) for d in all_entry_dates])

    # --- СБОРКА "Дата виведення 2" ---
    # Тут у нас только вычисленные даты (из массивов выведения)
    # (Если исходное поле было пустым, тут лежит [LastDay])
    
    exit_adds.sort()
    record['Дата виведення 2'] = "\n".join([date_to_str(d) for d in exit_adds])