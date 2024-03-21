@echo off
if "%1"=="h" goto begin
start mshta vbscript:createobject("wscript.shell").run("""%~nx0"" h",0)(window.close)&&exit
:begin
set PYTHON=.venv\Scripts\python.exe
%PYTHON% app.py
