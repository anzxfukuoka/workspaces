@ECHO OFF

CD %~dp0%
SET python="venv\Scripts\python.exe"

%python% main.py %*