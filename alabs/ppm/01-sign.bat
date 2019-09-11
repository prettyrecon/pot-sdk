DEL /Q/S pyinst\Release
XCOPY argos-pbtail\argos-pbtail\bin\Release pyinst\Release /O /X /E /H /K
sign\sign-all.bat
