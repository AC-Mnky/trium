@echo off
git pull
echo pull success, start to commit changes.
pause

git add .
set /p var=please enter commit message: 
git commit -m "%var%"
git pull
git push
echo commit success!
pause
