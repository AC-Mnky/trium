@REM This script will auto format the code using black and isort
@echo off
REM Set git user name and email
@REM git config --global user.name "Veritas"
@REM git config --global user.email "145042207+VeriTas-arch@users.noreply.github.com"

REM 运行 black 和 isort
cd ..
cd ..
cd ..
echo Running Black for code formatting...
echo Current formatting settings: [max-line-length=110][skip magic trailing comma]
black . --line-length=110 --skip-magic-trailing-comma

echo Running isort for import sorting...
isort .

REM 检查是否有更改
FOR /F "tokens=*" %%G IN ('git status --porcelain') DO (
    SET changes=%%G
    GOTO :HAS_CHANGES
)
GOTO :NO_CHANGES

:HAS_CHANGES
REM 添加所有更改
git add .

REM 提交更改
git commit -m "chore: auto format code"

REM 推送更改到当前分支
git push
echo Code formatted and pushed successfully!
EXIT /B 0

:NO_CHANGES
echo No formatting changes required.
EXIT /B 0

