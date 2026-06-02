rem builds console and gui executables stored in the ./dist directory  
rem run "python -m pip install pyinstaller" to get pyinstaller

pyinstaller --clean --onefile --noconfirm --paths=.\LGTV --noconsole --name lgtv_gui lgtv.py
pyinstaller --clean --onefile --noconfirm --paths=.\LGTV lgtv.py
