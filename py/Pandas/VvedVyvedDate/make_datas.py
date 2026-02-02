from modules import *

# sheet_lists = get_sheet_names(in_path) 
# for i, sheet in enumerate(sheet_lists):
#     print(f"{i}. {sheet}")

def get_current_year():
    from datetime import datetime
    current_year = datetime.now().year
    return str(current_year)

def get_current_month():
    from datetime import datetime
    current_month = datetime.now().month
    return str(current_month)


# def add_year(record):
#     date_str = record['Дата введення']
#     year = pd.to_datetime(date_str).year    
#     record['Дата введення'] = year
#     return record

def extract_digits_and_dots(text: str) -> str:
    """
    Возвращает строку, содержащую только цифры и точки
    из исходного текста.
    """
    text = str(text)
    result = "".join(ch for ch in text if ch.isdigit() or ch == ".")
    return result

def good_date(day, month):
    day, month = str(day), str(month)
    print('day, month', day, month)
    print('month=', month, 'current_month=', current_month)
    print('month == current_month:', month == current_month)
    if month == current_month:
        print(f"{day}.{current_month}.{current_year}")
        return f"{day}.{current_month}.{current_year}"
    elif month < current_month or month == '12':
        print(f"01.{current_month}.{current_year}")
        return f"01.{current_month}.{current_year}"
    return '*'

def mk_feeld_date_vvedenia_1(date_str: str) -> str:
    date_str = extract_digits_and_dots(date_str)
    parts = date_str.strip().split(".")
    print(f'Parts: {parts}')
    if 1 < len(parts) < 4:
       return good_date(parts[0], parts[1])
    elif 3 < len(parts) < 6:
        return good_date(parts[0], parts[1]) + ' \n' + good_date(parts[2], parts[3])
    elif 5 < len(parts) < 8:
        return (good_date(parts[0], parts[1]) + 
                ' \n' + good_date(parts[2], parts[3]) +
                ' \n' + good_date(parts[4], parts[5]))
    if len(parts) == 0:
        return f"01.{current_month}.{current_year}"

def mk_data_vvedenia_1(record):    
    date_0 = record['Дата введення']
    mk_feeld_date_vvedenia_1(date_0)
    record['Дата введення 1'] = mk_feeld_date_vvedenia_1(date_0)
    

def process():
    for record in records:
        #print(record)
        date_vvedenia_0 = record['Дата введення']
        mk_data_vvedenia_1(record)

import pandas as pd

def save_records_to_excel(records: list[dict], file_path: str, sheet_name: str = "Sheet1"):
    """
    Сохраняет список словарей в Excel-файл.
    
    :param records: список словарей (каждый словарь = строка)
    :param file_path: путь для сохранения файла .xlsx
    :param sheet_name: название листа (по умолчанию "Sheet1")
    """
    df = pd.DataFrame(records)
    df.to_excel(file_path, sheet_name=sheet_name, index=False)


def main():
    process()


current_year = get_current_year()
current_month = get_current_month()
if len(current_month) == 1:
    current_month = '0' + current_month

show_vkladki()
activ_vkladka_num = 13
activ_vkladka_name = get_sheet_names(in_path)[activ_vkladka_num]
records = get_records_by_sheet(activ_vkladka_name)

main()

for record in records:
    print(f'{record['Дата введення']} --> {record["Дата введення 1"]}')


print(f'{current_month=} {current_year=}')

out_path = f"D:/Data/OutData/Excel/out_{activ_vkladka_name}.xlsx"
save_records_to_excel(records, out_path, activ_vkladka_name)


print('\nГотово!')
print(f'Файл сохранен по пути: \n{out_path}')