@echo off
setlocal

REM Create a Windows test directory tree for the renamer tool.
REM Usage: scripts\create_testcase.bat [target_path]

set TARGET=%1
if "%TARGET%"=="" set TARGET=%CD%\win_testcase

echo Creating test tree at: %TARGET%
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  python "%~dp0\create_testcase.py" --target "%TARGET%"
) else (
  echo Python not found. Creating a minimal structure...
  mkdir "%TARGET%" 2>nul
  mkdir "%TARGET%\1" 2>nul
  mkdir "%TARGET%\2" 2>nul
  mkdir "%TARGET%\10" 2>nul
  echo sample> "%TARGET%\1\file.txt"
  echo sample> "%TARGET%\2\file.txt"
  echo sample> "%TARGET%\10\file.txt"
)

echo Done.
endlocal


