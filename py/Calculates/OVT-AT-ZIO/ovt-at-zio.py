import re

def count_items(filename="./in.txt"):
    total_OVT = 0
    total_AT = 0
    total_ZIO = 0
    
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            # Убираем лишние пробелы и скобки
            line = line.strip()
            if not line:
                continue  # пропускаем пустые строки
            
            # Ищем все пары "число + слово"
            matches = re.findall(r"(\d+)\s*([А-ЯІЇЄ]+)", line)
            for num_str, word in matches:
                num = int(num_str)
                word = word.upper()
                
                if "ОВТ" in word:
                    total_OVT += num
                elif "АТ" in word:
                    total_AT += num
                elif "ЗІО" in word:
                    total_ZIO += num
    
    return total_OVT, total_AT, total_ZIO

# Пример использования
ovt, at, zio = count_items("./in.txt")
# print("ОВТ =", ovt)
# print("АТ =", at)
# print("ЗІО =", zio)

print(f"\n{ovt} ОВТ \n({at} АТ\n{zio} ЗІО)")


