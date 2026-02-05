# Скрипт отправки обновлений в Git с проверкой статуса

Clear-Host
Write-Host "=== Проверка текущего статуса файлов ===" -ForegroundColor Yellow

# 1. Предварительно добавляем всё, чтобы увидеть новые файлы тоже
git add .

# 2. Показываем краткий статус
git status --short

Write-Host "`nВыше список файлов, которые будут отправлены." -ForegroundColor Gray
$confirmation = Read-Host "Всё верно? (Y/N)"

if ($confirmation -ne "y" -and $confirmation -ne "Y") {
    Write-Host "Отмена. Ничего не отправлено." -ForegroundColor Red
    Pause
    exit
}

# 3. Если всё ок, просим коммит
$commitMsg = Read-Host "Введи описание обновления"

if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $commitMsg = "Обновление инструментов (авто-коммит)"
}

# 4. Коммит и отправка
Write-Host "`n--- Коммит... ---" -ForegroundColor Cyan
git commit -m "$commitMsg"

Write-Host "--- Отправка в репозиторий... ---" -ForegroundColor Cyan
git push

Write-Host "`n--- Готово! Всё улетело. ---" -ForegroundColor Green
Pause