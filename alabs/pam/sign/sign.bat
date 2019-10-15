
: SignTool.exe sign ^
:   /f 20190703-774162_CHAIN_argos-labs_com.pfx ^
:   -p han!@35ssl /v ^
:   -t "http://timestamp.verisign.com/scripts/timstamp.dll" ^
:   %1

SignTool.exe sign ^
    /f 20190703-774162_CHAIN_argos-labs_com.pfx ^
    -p han!@35ssl /v ^
    -tr "http://sha256timestamp.ws.symantec.com/sha256/timestamp" ^
    %1
