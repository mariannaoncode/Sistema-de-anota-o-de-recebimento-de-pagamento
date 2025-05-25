@echo off
echo ============================
echo Gerando Executável .EXE
echo ============================

REM Verifica se o PyInstaller está instalado
python -m pyinstaller --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo PyInstaller não está instalado. Instalando agora...
    python -m pip install pyinstaller
)

REM Gera o executável
echo Criando executável...
python -m PyInstaller --noconfirm --onefile --windowed --icon=peixe.ico colaborador_cadastro.py

echo.
echo ============================
echo Finalizado!
echo O executável está na pasta "dist".
echo ============================
pause
