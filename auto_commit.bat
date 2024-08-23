@echo off
echo Auto pull changes from remote repository.
git pull
echo Pull success, start to commit changes.

git add .
set /p var=Please enter commit message: 
git commit -m "%var%"
git pull
git push
echo Commit success!
pause
