chcp 65001
@echo off
title Trium Auto Commit Script
type %cd%\assets\trium.txt
echo.


for /f "tokens=1-4 delims=:. " %%a in ("%time%") do (
    set hour=%%a
    set min=%%b
    set sec=%%c
)
echo Current Time is %hour%:%min%:%sec%. Hello from Trium!
echo.
echo Here is a simple tutorial to help you quickly get started with this repository.


:choose_intro
echo.
echo Please choose your operation (enter letter (case SENSITIVE) in square brackets):
echo [A] Browse the global README.md  [B] Review SoftwareDesign.md  [C] Start Git Operations  [D] Format Codes
echo [N] Exit  [T] Beta Test XD
set /p var=
if %var%==A goto browse_readme
if %var%==B goto software_design
if %var%==C goto choose_git
if %var%==D goto format_codes
if %var%==N exit
if %var%==T goto test
else echo Invalid input, please try again.
goto choose_intro


:browse_readme
echo.
echo Auto open README.md in command line.
echo.
echo.
type %cd%\README.md
echo.
echo.
pause
goto choose_exit


:software_design
echo.
echo Auto open SoftwareDesign.md in command line.
echo.
echo.
type %cd%\doc\SoftwareDesign.md
echo.
echo.
pause
goto choose_exit


:choose_git
echo.
echo Please choose your Git operation (enter letter in square brackets):
echo [A] Pull only  [B] Commit only  [C] Pull and Commit
set /p var=
if %var%==A goto pull
if %var%==B goto commit
if %var%==C goto pull_commit
else (
    echo.
    echo Invalid input, please try again.
)
goto choose_git


:pull
echo.
echo Auto pull changes from remote repository.
git pull
echo Pull success (?)
goto choose_exit


:commit
echo.
git add .
set /p commit_message="Please enter commit message: "
git commit -m "%commit_message%"
git pull
git push
echo Commit success (?)
goto choose_exit


:pull_commit
echo.
echo Auto pull changes from remote repository.
git pull
echo Pull success (?), start to commit changes.
git add .
set /p commit_message="Please enter commit message: "
git commit -m "%commit_message%"
git pull
git push
echo Commit success (?)
goto choose_exit


:format_codes
echo.
echo Auto format all codes in the repository.
echo.
echo Checking whether black is installed...

setlocal
set "PYTHON_EXE=python"
set "PACKAGE_NAME=black"
%PYTHON_EXE% -c "import %PACKAGE_NAME%; print(%PACKAGE_NAME%)" >nul 2>nul
if errorlevel 1 (
    echo %PACKAGE_NAME% is not installed. Install %PACKAGE_NAME% to format?
    set /p var_install= [y/n]
    if %var_install%==Y (
        echo Installing %PACKAGE_NAME%...
        %PYTHON_EXE% -m pip install %PACKAGE_NAME%
        echo %PACKAGE_NAME% is installed. Start formatting.
    ) else if %var_install%==y (
        echo Installing %PACKAGE_NAME%...
        %PYTHON_EXE% -m pip install %PACKAGE_NAME%
        echo %PACKAGE_NAME% is installed. Start formatting.
    ) else (
        echo Quit formatting.
        goto choose_intro
) else (
    echo %PACKAGE_NAME% is installed. Start formatting.
)
endlocal

echo Current formatting settings: [max-line-length=110][skip magic trailing comma].
@REM TODO: Add code formatter settings into a configuration file.
black . --line-length=110 --skip-magic-trailing-comma
pause
goto choose_exit


:choose_exit
echo.
echo Wander around for a while longer [y/n]?
set /p var_exit=
if %var_exit%==Y (
    echo Return to main menu.
    goto choose_intro
)
if %var_exit%==y (
    echo Return to main menu.
    goto choose_intro
)
if %var_exit%==N (
    echo Goodbye!
    exit
)
if %var_exit%==n (
    echo Goodbye!
    exit
)
else echo Invalid input, please try again.
pause
goto choose_exit


:test
echo.
echo Play Music!
start %cd%\assets\music\10th_symphony_type-MOON.mp3
echo Current Playing: 10th Symphony TYPE/MOON
echo.
pause
goto choose_intro
