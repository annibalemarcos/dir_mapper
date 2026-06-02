@echo off
mode con: cols=68 lines=14
REM ================================================================
REM  DIR MAP v0.2 - Build completo do .exe (Windows)
REM  Gera dist\DIR MAP Setup 0.2.0.exe SEM exigir Python no usuário final.
REM
REM  Pré-requisitos NA SUA MAQUINA (não no PC do usuário final):
REM    1. Node.js >= 16  (https://nodejs.org)
REM    2. Python  >= 3.8 (https://python.org)  -- so para BUILDAR
REM ================================================================

echo.
echo === [1/4] Instalando dependencias Node ===
call npm install
if errorlevel 1 goto :fail

echo.
echo === [2/4] Instalando PyInstaller ===
python -m pip install --upgrade pip
python -m pip install pyinstaller
if errorlevel 1 goto :fail

echo.
echo === [3/4] Empacotando Python em dir_mapper.exe ===
if exist bin rmdir /s /q bin
call npm run build-python
if errorlevel 1 goto :fail

if not exist bin\dir_mapper.exe (
    echo ERRO: bin\dir_mapper.exe nao foi gerado.
    goto :fail
)

echo.
echo === [4/4] Empacotando o instalador Electron ===
call npm run build-win
if errorlevel 1 goto :fail

echo.
echo ================================================================
echo  BUILD CONCLUIDO!
echo  Instalador disponivel em:  dist\DIR MAP Setup 0.2.0.exe
echo  Versao portavel em:        dist\win-unpacked\DIR MAP.exe
echo ================================================================
exit /b 0

:fail
echo.
echo *** Build falhou. Verifique os erros acima. ***
exit /b 1
