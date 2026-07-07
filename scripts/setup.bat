@echo off
echo Setting up Reddit Crosspost Bot...

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo Creating directories...
mkdir data 2>nul
mkdir logs 2>nul

if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please edit .env file with your credentials
)

echo Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your Reddit credentials
echo 2. Run: python src/main.py
pause