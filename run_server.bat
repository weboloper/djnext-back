@echo off
setlocal
cd /d %~dp0
call env\Scripts\activate
py manage.py runserver