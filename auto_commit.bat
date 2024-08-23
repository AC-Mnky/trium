@echo off
for /f "tokens=1-4 delims=:. " %%a in ("%time%") do (
    set hour=%%a
    set min=%%b
    set sec=%%c
)
echo Current Time is %hour%:%min%:%sec%. Hello from Trium!
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
