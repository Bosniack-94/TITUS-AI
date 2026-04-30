@echo off
echo [TITUS] Iniciando Ecosistema Centralizado...

echo [*] Lanzando NUCLEO (Backend)...
start "TITUS_BACKEND" cmd /c "cd /d %~dp0backend && python main.py"

echo [*] Lanzando DASHBOARD (Frontend)...
start "TITUS_DASHBOARD" cmd /c "cd /d %~dp0frontend && npm run dev"

echo [!] TITUS: Todos los sistemas iniciados.
pause
