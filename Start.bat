@echo off
SET VENV_PATH=venv

IF NOT EXIST "%VENV_PATH%" (
    echo Creating virtual environment...
    python -m venv %VENV_PATH%
)

echo Activating virtual environment...
CALL %VENV_PATH%\Scripts\activate

echo Upgrading pip and installing requirements...
python -m pip install --upgrade pip & pip install -r requirements.txt

echo Starting the application...
python GUI.py

echo Done.