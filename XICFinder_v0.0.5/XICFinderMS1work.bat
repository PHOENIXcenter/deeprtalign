@echo off
if not exist raw (
mkdir raw
)
for /f  %%a in ('dir /b %cd%\*.raw') do (
echo dealing with %%~na !
XICFinder.exe 1 %%a %%~naout.txt 3 10
echo %%~na finish!
move %%a raw
)
echo 工作完成\(^^o^^)/~
pause