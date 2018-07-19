@echo off


for /l %%i in (1 1 256) do (

FOR /F %%a IN ('TIME /T') DO set a=%%a
echo %date% %a% %time%

git status
cd img
git add .
git commit -m "daily update"
git push
cd ..
git add .
git commit -m "daily update"
git push

FOR /F %%a IN ('TIME /T') DO set a=%%a
echo %date% %a% %time%

timeout /t 86400
)
pause