REM sign.bat ..\pyinst\Release\argos-pbtail.exe
sign\SignTool.exe sign ^
    /f sign\20190703-774162_CHAIN_argos-labs_com.pfx ^
    -p han!@35ssl ^
    /v -tr "http://sha256timestamp.ws.symantec.com/sha256/timestamp" ^
    pyinst\Release\argos-pbtail.exe
