@echo off
git add .
set /p var=please enter commit message: 
git commit -m var
git pull
git push
echo commit success!
pause
