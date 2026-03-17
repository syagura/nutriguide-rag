@echo off
cd /d D:\Development\fullstack_ml\nutriguide-rag\backend
set PYTHONPATH=src
uvicorn main:app --reload --host 0.0.0.0 --port 8000