@echo off
set IDJOGO=%1
set GRUPO=%2
start cmd /k python playGameBot.py %IDJOGO% %GRUPO%
