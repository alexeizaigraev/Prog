import pandas as pd

in_path = "D:/Data/InData/Excel/in1.xlsx"

def get_sheet_names(file_path: str) -> list[str]:
    """
    Возвращает список названий всех листов Excel-файла.

    :param file_path: путь к Excel-файлу (.xlsx, .xls)
    :return: список строк с названиями листов
    """
    xls = pd.ExcelFile(file_path)
    return xls.sheet_names

def read_sheet_as_dicts(file_path: str, sheet_name: str) -> list[dict]:
    """
    Читает указанный лист Excel-файла и возвращает список словарей.
    Ключи словаря = названия колонок, значения = данные строк.

    :param file_path: путь к Excel-файлу (.xlsx, .xls)
    :param sheet_name: название листа
    :return: список словарей
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return df.to_dict(orient="records")

def show_vkladki():
    sheet_lists = get_sheet_names(in_path) 
    for i, sheet in enumerate(sheet_lists):
        print(f"{i}. {sheet}")

def get_records_by_sheet(sheet_name: str) -> list[dict]:
# sheet = _listsheets[13]   
    return read_sheet_as_dicts(in_path, sheet_name)

# records = read_sheet_as_dicts(in_path, _listsheets[13])  # пример чтения 14-го листа
# print(records)
# print('\n' + sheet)

