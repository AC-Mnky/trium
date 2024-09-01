@REM Global settings for Trium Intro Script.
chcp 65001
@echo off
title Trium Auto Commit Script
type %cd%\assets\trium.txt
echo.


@REM Get current time
for /f "tokens=1-4 delims=:. " %%a in ("%time%") do (
    set hour=%%a
    set min=%%b
    set sec=%%c
)
echo Current Time is %hour%:%min%:%sec%. Hello from Trium!
echo.
echo Here is a simple tutorial to help you quickly get started with this repository.

@REM Main Menu
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


@REM Submenu 1 - browse README.md
:browse_readme
echo.
echo [Current Action] Auto open README.md in command line.
echo.
echo.
type %cd%\README.md
echo.
echo.
pause
goto choose_exit


@REM Submenu 2 - browse SoftwareDesign.md
:software_design
echo.
echo [Current Action] Auto open SoftwareDesign.md in command line.
echo.
echo.
type %cd%\doc\SoftwareDesign.md
echo.
echo.
pause
goto choose_exit


@REM Submenu 3 - choose git operations
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

@REM Git Operation 1 - pull only
:pull
echo.
echo [Current Action] Auto pull changes from remote repository.
git pull
echo Pull success (?)
goto choose_exit

@REM Git Operation 2 - commit only
:commit
echo.
echo [Current Action] Auto commit changes to remote repository.
git add .
set /p commit_message="Please enter commit message: "
git commit -m "%commit_message%"
git pull
git push
echo Commit success (?)
goto choose_exit

@REM Git Operation 3 - pull and commit
:pull_commit
echo.
echo [Current Action] Auto pull from remote repository and commit changes.
git pull
echo Pull success (?), start to commit changes.
git add .
set /p commit_message="Please enter commit message: "
git commit -m "%commit_message%"
git pull
git push
echo Commit success (?)
goto choose_exit


@REM Submenu 4 - format codes
:format_codes
echo.
echo [Current Action] Auto format all codes in the repository.
echo.
echo Checking whether black is installed...

setlocal
set "PYTHON_EXE=python"
set "PACKAGE_NAME=black"
%PYTHON_EXE% -c "import %PACKAGE_NAME%; print(%PACKAGE_NAME%)" >nul 2>nul
if errorlevel 1 (
    goto install_package
) else (
    echo %PACKAGE_NAME% is installed. Start formatting.
    goto format
)
endlocal

@REM exception handling - install package
:install_package
echo %PACKAGE_NAME% is not installed. Install %PACKAGE_NAME% to format [y/n]?
set /p var_install=
if %var_install%==Y (
    echo Installing %PACKAGE_NAME%...
    %PYTHON_EXE% -m pip install %PACKAGE_NAME%
    echo %PACKAGE_NAME% is installed. Start formatting.
) else if %var_install%==y (
    echo Installing %PACKAGE_NAME%...
    %PYTHON_EXE% -m pip install %PACKAGE_NAME%
    echo %PACKAGE_NAME% is installed. Start formatting.
) else if %var_install%==N (
    echo Quit formatting.
    goto choose_intro
) else if %var_install%==n (
    echo Quit formatting.
    goto choose_intro
) else ( 
    echo Invalid input, please try again.
    goto format_codes
)

@REM format codes
:format
echo Current formatting settings: [max-line-length=110][skip magic trailing comma].
@REM TODO: Add code formatter settings into a configuration file.
black . --line-length=110 --skip-magic-trailing-comma
pause
goto choose_exit


@REM Submenu 5 - exit
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


@REM Submenu 6 - test (beta)
:test
echo.
echo [Current Action] Play Music!
echo.
echo Please choose your music (enter letter in square brackets):
echo [A] 10th Symphony TYPE/MOON  [B] Scar Red
set /p music=
if %music%==A goto play_10th_symphony
if %music%==B goto play_scar_red
else echo Invalid input, please try again.
goto test

@REM Music Player 1 - 10th Symphony TYPE/MOON
:play_10th_symphony
start %cd%\assets\music\10th_symphony_type-MOON.mp3
echo Current Playing: 10th Symphony TYPE/MOON
echo.
pause
goto choose_intro

@REM Music Player 2 - Scar Red
:play_scar_red
start %cd%\assets\music\Scar_Red.mp3
echo Current Playing: Scar Red
echo.
pause
goto choose_intro
