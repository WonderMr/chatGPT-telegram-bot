set c_dir=%cd%
call %c_dir%/venv/Scripts/activate.bat
cd %c_dir%
pip install -r %c_dir%/requirements.txt
playwright install
playwright install-deps