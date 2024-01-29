@echo off
set "venvPath=D:\Dev\webscrap\venv"
set "pythonScriptPath=D:\Dev\webscrap\main.py"

rem Активация виртуального окружения
call "%venvPath%\Scripts\activate"

rem Запуск main.py
python "%pythonScriptPath%"

rem Деактивация виртуального окружения
deactivate