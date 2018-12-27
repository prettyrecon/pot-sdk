REM @echo off

REM 1) pip install
pip install PyYAML


REM 2) move shell folder
PUSHD %~dp0
set WDIR=%CD%
echo "working directory for build_all is \"%WDIR%\""

REM 3) bf has each build.bat and do
for /f "tokens=*" %%a in ('dir /s/b build.bat') do call :processline %%a

goto :eof

REM %bf% has the build.sh path
:processline
	set bf=%*
	echo %bf%
	for %%F in (%bf%) do set dirname=%%~dpF
	echo "building %dirname% ..."
	python.exe %WDIR%\change_version.py -n %dirname%\setup.yaml
	pushd %dirname%
		CALL build.bat
	popd
	goto :eof

:eof
POPD
echo "Build All is done!"
