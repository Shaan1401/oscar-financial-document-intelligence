@echo off
title OSCAR Frontend (Vite :5173)
cd /d "%~dp0..\frontend"
set TEMP=%~dp0..\.runtime\tmp
set TMP=%~dp0..\.runtime\tmp
set npm_config_cache=%~dp0..\.runtime\npm-cache
npm run dev -- --host 127.0.0.1 --port 5173
