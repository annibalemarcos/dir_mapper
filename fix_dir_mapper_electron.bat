@echo off
mode con: cols=68 lines=14
setlocal EnableExtensions EnableDelayedExpansion

color 0B
title DIR MAP - Reparador Electron / Node

set "PROJECT_DIR=C:\my_projects\dir_mapper_v2"
set "TARGET_NODE_MAJOR=22"

echo ================================================================
echo  DIR MAP - Reparador de Electron / Node / npm
echo ================================================================
echo.
echo Este script tenta, em ordem:
echo  1. Reinstalar apenas o Electron.
echo  2. Se falhar, usar Node LTS 22 via nvm-windows, se existir.
echo  3. Se ainda falhar, limpar node_modules/cache e reinstalar tudo.
echo.
echo IMPORTANTE: este script NAO roda npm audit fix --force.
echo.

if not exist "%PROJECT_DIR%" (
    echo [ERRO] Pasta do projeto nao encontrada:
    echo        %PROJECT_DIR%
    echo.
    pause
    exit /b 1
)

cd /d "%PROJECT_DIR%" || (
    echo [ERRO] Nao consegui entrar na pasta do projeto.
    pause
    exit /b 1
)

echo [OK] Pasta atual:
echo      %CD%
echo.

call :SHOW_NODE

echo ================================================================
echo  ETAPA 1 - Reinstalar somente o Electron
echo ================================================================
echo.

if exist "node_modules\electron" (
    echo Removendo node_modules\electron...
    rmdir /s /q "node_modules\electron"
) else (
    echo node_modules\electron nao existe. Seguindo mesmo assim...
)

echo.
echo Instalando Electron novamente...
call npm install electron --save-dev
if errorlevel 1 (
    echo.
    echo [AVISO] Falhou ao reinstalar Electron.
    goto TRY_NVM
)

echo.
echo Testando npm start...
call npm start
if not errorlevel 1 (
    echo.
    echo [SUCESSO] App abriu/rodou com a reinstalacao do Electron.
    goto END_OK
)

echo.
echo [AVISO] npm start ainda falhou. Vamos para a proxima tentativa.
echo.

:TRY_NVM
echo ================================================================
echo  ETAPA 2 - Tentar Node LTS 22 via nvm-windows
echo ================================================================
echo.

where nvm >nul 2>nul
if errorlevel 1 (
    echo [INFO] nvm-windows nao encontrado neste sistema.
    echo        Pulando troca automatica de Node.
    goto FULL_CLEAN
)

echo [OK] nvm encontrado.
echo Instalando/usando Node %TARGET_NODE_MAJOR%...
call nvm install %TARGET_NODE_MAJOR%
call nvm use %TARGET_NODE_MAJOR%

echo.
call :SHOW_NODE

echo.
echo Reinstalando dependencias com Node LTS...
call npm install
if errorlevel 1 (
    echo.
    echo [AVISO] npm install falhou com Node LTS.
    goto FULL_CLEAN
)

echo.
echo Testando npm start com Node LTS...
call npm start
if not errorlevel 1 (
    echo.
    echo [SUCESSO] App abriu/rodou usando Node LTS via nvm.
    goto END_OK
)

echo.
echo [AVISO] Ainda falhou. Vamos para a limpeza bruta.
echo.

:FULL_CLEAN
echo ================================================================
echo  ETAPA 3 - Limpeza bruta e reinstalacao completa
echo ================================================================
echo.
echo Isto remove node_modules e package-lock.json, limpa cache npm,
echo reinstala tudo e tenta abrir novamente.
echo.

if exist "node_modules" (
    echo Removendo node_modules...
    rmdir /s /q "node_modules"
) else (
    echo node_modules nao existe. OK.
)

if exist "package-lock.json" (
    echo Removendo package-lock.json...
    del /f /q "package-lock.json"
) else (
    echo package-lock.json nao existe. OK.
)

echo.
echo Limpando cache npm...
call npm cache clean --force

echo.
echo Instalando tudo novamente...
call npm install
if errorlevel 1 (
    echo.
    echo [ERRO] npm install falhou mesmo apos limpeza completa.
    echo.
    echo Sugestao: instale manualmente o Node.js LTS 22 e rode este .bat de novo.
    echo Nao use npm audit fix --force por enquanto.
    goto END_FAIL
)

echo.
echo Testando npm start apos limpeza completa...
call npm start
if not errorlevel 1 (
    echo.
    echo [SUCESSO] App abriu/rodou apos limpeza completa.
    goto END_OK
)

echo.
echo [ERRO] O app ainda nao abriu.
echo.
echo Proximos passos recomendados:
echo  1. Instale Node.js LTS 22 manualmente.
echo  2. Feche e abra o CMD novamente.
echo  3. Rode este .bat outra vez.
echo.
echo Nao rode npm audit fix --force agora.
goto END_FAIL

:SHOW_NODE
echo Versoes atuais:
where node >nul 2>nul
if errorlevel 1 (
    echo   Node: nao encontrado
) else (
    for /f "delims=" %%v in ('node -v 2^>nul') do echo   Node: %%v
)
where npm >nul 2>nul
if errorlevel 1 (
    echo   npm: nao encontrado
) else (
    for /f "delims=" %%v in ('npm -v 2^>nul') do echo   npm: %%v
)
exit /b 0

:END_OK
echo.
echo ================================================================
echo  Finalizado com sucesso.
echo ================================================================
echo.
pause
exit /b 0

:END_FAIL
echo.
echo ================================================================
echo  Finalizado com erro.
echo ================================================================
echo.
pause
exit /b 1
