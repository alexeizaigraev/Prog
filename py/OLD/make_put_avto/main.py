import csv
import os

# Исходные данные
presission = 0

speed_start = 0
speed_end = 400
probeg = speed_end - speed_start

fuel_rashod = 40
norma_rashod = 10

koef_trassa = 0.85
koef_gorod = 1.05
koef_bezdor = 1.3

max_bezdor = int(probeg * 0.3)

results = []

for probeg_bezdor in range(0, max_bezdor + 1):
    for probeg_trassa in range(0, probeg - probeg_bezdor + 1):
        probeg_city = probeg - probeg_trassa - probeg_bezdor
        if probeg_city < 0:
            continue

        rashod_trassa = probeg_trassa * koef_trassa * norma_rashod / 100
        rashod_city = probeg_city * koef_gorod * norma_rashod / 100
        rashod_bezdor = probeg_bezdor * koef_bezdor * norma_rashod / 100

        fuel_rashod_calculate = rashod_trassa + rashod_city + rashod_bezdor
        razn = abs(fuel_rashod - fuel_rashod_calculate)

        if razn <= presission:
            results.append([
                probeg_trassa, probeg_city, probeg_bezdor,
                f"{rashod_trassa:.2f}", f"{rashod_city:.2f}", f"{rashod_bezdor:.2f}",
                f"{razn:.2f}"
            ])

if results:
    results.sort(key=lambda x: float(x[-1]))
    with open("result.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow([
            "probeg_trassa", "probeg_city", "probeg_bezdor",
            "rashod_trassa", "rashod_city", "rashod_bezdor", "razn"
        ])
        writer.writerows(results)
    os.system("notepad.exe result.csv")
else:
    min_razn = float("inf")
    for probeg_bezdor in range(0, max_bezdor + 1):
        for probeg_trassa in range(0, probeg - probeg_bezdor + 1):
            probeg_city = probeg - probeg_trassa - probeg_bezdor
            if probeg_city < 0:
                continue
            fuel_rashod_calculate = (
                probeg_trassa * koef_trassa +
                probeg_city * koef_gorod +
                probeg_bezdor * koef_bezdor
            ) * norma_rashod / 100
            razn = abs(fuel_rashod - fuel_rashod_calculate)
            if razn < min_razn:
                min_razn = razn
    print(f"{min_razn:.2f} # no result")