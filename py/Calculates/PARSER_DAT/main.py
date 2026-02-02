import csv
from datetime import datetime, timedelta

# входной файл
INPUT_FILE = "in.csv"
OUTPUT_FILE = "out.csv"

def parse_date(date_str):
    """Преобразует строку даты в объект datetime."""
    try:
        return datetime.strptime(date_str.strip(), "%d.%m.%Y")
    except:
        return None

def process_row(row):
    """
    Обработка одной строки по правилам:
    - если заведён раньше месяца → первая дата ввода = 01.01.2026
    - события болезни/отпуска → вывод на день раньше, ввод на день позже
    - если ввод попадает в новый месяц → ставим 31.01.2026
    - если дата ввода пустая → вывод = 31.01.2026
    """
    month_start = datetime(2026, 1, 1)
    month_end = datetime(2026, 1, 31)

    dates_in = []
    dates_out = []

    # пример: row[0] = "30.12.2026", row[1] = "хворіє 28.01.2026 по 31.01.2026"
    date_in = parse_date(row[0]) if row[0] else None
    note = row[1].lower() if len(row) > 1 else ""

    # если заведён раньше месяца
    if date_in and date_in < month_start:
        dates_in.append(month_start.strftime("%d.%m.%Y"))
    elif date_in and month_start <= date_in <= month_end:
        dates_in.append(date_in.strftime("%d.%m.%Y"))
    elif not date_in:
        # пустая дата ввода → вывод конец месяца
        dates_out.append(month_end.strftime("%d.%m.%Y"))

    # обработка событий
    if "хворіє" in note or "лікарня" in note or "відпустка" in note:
        # ищем диапазон дат
        import re
        match = re.findall(r"(\d{2}\.\d{2}\.\d{4})", note)
        if len(match) >= 2:
            start = parse_date(match[0])
            end = parse_date(match[1])
            if start and end:
                # вывод на день раньше
                out_date = start - timedelta(days=1)
                if month_start <= out_date <= month_end:
                    dates_out.append(out_date.strftime("%d.%m.%Y"))
                # ввод на день позже
                in_date = end + timedelta(days=1)
                if in_date.month == 1:
                    dates_in.append(in_date.strftime("%d.%m.%Y"))
                else:
                    dates_in.append(month_end.strftime("%d.%m.%Y"))
                # конец месяца — всегда вывод
                dates_out.append(month_end.strftime("%d.%m.%Y"))

    return "\n".join(dates_in), "\n".join(dates_out)

def main():
    with open(INPUT_FILE, newline='', encoding="utf-8") as f_in, \
         open(OUTPUT_FILE, "w", newline='', encoding="utf-8") as f_out:
        reader = csv.reader(f_in, delimiter=";")
        writer = csv.writer(f_out, delimiter=";")

        # заголовки
        writer.writerow(["Даты ввода", "Даты вывода"])

        for row in reader:
            dates_in, dates_out = process_row(row)
            writer.writerow([dates_in, dates_out])

if __name__ == "__main__":
    main()