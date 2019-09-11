REM PYTHON installer for PPM

REM    --add-data README.md;README.md ^
REM    --add-data LICENSE.txt;LICENSE.txt ^
REM    --add-data requirements.txt;requirements.txt ^
REM    --add-data setup.yaml;setup.yaml ^

DEL /Q/S exe
DEL /Q/S build
DEL /Q/S dist

REM sign.bat

pyinstaller ^
    --onefile ^
    --add-data pyinst;. ^
    __main__.py
rem    --uac-admin ^
rem    --add-data cacert.pem;pip\_vendor\certifi ^
rem    --add-data pythonw.exe;. ^
rem    --add-data pyvenv.cfg;. ^
rem    --add-data pip;pip ^
rem    --add-data venv.zip;. ^

if %ERRORLEVEL% == 0 goto :next2
    echo "Errors encountered during pyinstaller.  Exited with status: %errorlevel%"
    goto :endofscript
:next2

mkdir exe
move __pycache__ exe
move build exe
move dist exe
MOVE exe\dist\__main__.exe exe\dist\alabs-ppm.exe

sign\SignTool.exe sign ^
    /f sign\20190703-774162_CHAIN_argos-labs_com.pfx ^
    -p han!@35ssl ^
    /v -tr "http://sha256timestamp.ws.symantec.com/sha256/timestamp" ^
    exe\dist\alabs-ppm.exe

REM for test
REM COPY exe\dist\alabs-ppm.exe C:\work\ppm\ppm.exe

:endofscript
echo "Script complete"
