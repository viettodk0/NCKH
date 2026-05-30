@echo off
:: Tu dong chuyen terminal vao thu muc chua file bat nay
cd /d "%~dp0"

:: Khoi chay bang pythonw (pyw) de an cua so dong lenh den xil
start "" pyw photo_editor_app.py

:: Neu lenh tren loi (khong tim thay pyw), thu chay bang python thong thuong
if %errorlevel% neq 0 (
    start "" python photo_editor_app.py
)
