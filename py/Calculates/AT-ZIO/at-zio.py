import re

def count_items(filename="./in.txt"):
    total_AT = 0
    total_ZIO = 0
    
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Ищем все пары "число + слово"
            matches = re.findall(r"(\d+)\s*([А-ЯІЇЄ]+)", line)
            for num, word in matches:
                num = int(num)
                word = word.upper()
                if "АТ" in word:
                    total_AT += num
                elif "ЗІО" in word:
                    total_ZIO += num
    
    return total_AT, total_ZIO

# Пример использования
at, zio = count_items("./in.txt")
print(f"\n{at + zio} ОВТ \n({at} АТ\n{zio} ЗІО)")
