@echo off
for /f "tokens=1-4 delims=:. " %%a in ("%time%") do (
    set hour=%%a
    set min=%%b
    set sec=%%c
)
echo Current Time is %hour%:%min%:%sec%. Hello from Trium!
echo.

:choose
echo Please choose your operation (enter A, B or C):
echo [A] Pull only  [B] Commit only  [C] Pull and Commit
set /p var=
if %var%==A goto pull
if %var%==B goto commit
if %var%==C goto pull_commit
else echo Invalid input, please try again.
goto choose

:pull
echo Auto pull changes from remote repository.
git pull
echo Pull success (?)
pause
exit

:commit
git add .
set /p commit_message="Please enter commit message: "
git commit -m "%commit_message%"
git pull
git push
echo Commit success (?)
pause
exit

:pull_commit
echo Auto pull changes from remote repository.
git pull
echo Pull success (?), start to commit changes.
git add .
set /p commit_message="Please enter commit message: "
git commit -m "%commit_message%"
git pull
git push
echo Commit success (?)
pause
exit
