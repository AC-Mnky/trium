@echo off
echo Auto synchronize changes from remote repository.
git add .
set /p var=Please enter commit message: 
git commit -m "%var%"
git pull
git push
echo Commit success!
pause
