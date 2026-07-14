@echo off
echo Starting CyberProspect Dashboard...
call venv\Scripts\activate.bat
set PYTHONPATH=%cd%
streamlit run app\Overview.py
