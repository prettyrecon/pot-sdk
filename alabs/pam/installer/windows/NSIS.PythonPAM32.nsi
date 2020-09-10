OutFile "${PRODUCT_NAME}-${PRODUCT_VERSION}.exe"
InstallDir "$LOCALAPPDATA\PythonPAM"
; RequestExecutionLevel User

!include 'FileFunc.nsh'
!include 'MoveFileFolder.nsh'
!include 'LogicLib.nsh'
!include 'DotNetVer.nsh'
!include 'x64.nsh'
!include 'Registry.nsh'
!include 'WinVer.nsh'
!include 'RemoveFilesAndSubDirs.nsh'


BrandingText "ARGOS LABS - ARGOS PythonPAM for Windows Installer"

; Section SEC00
;     ${If} ${RunningX64}
;         SetRegView 64
;     ${EndIf}
;     !define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\Tesseract-OCR"
;     ReadRegStr $0 HKLM "${PRODUCT_UNINST_KEY}" UninstallString
;     DetailPrint "OCR is installed at: $0"
;     Sleep 10000

; SetRegView LastUsed
; SectionEnd


Section "${PRODUCT_NAME}-${PRODUCT_VERSION}" SEC01
  DetailPrint "Installing ${__SECTION__}"
  SetShellVarContext all
  SetOutPath "$INSTDIR"
  SetOverwrite on
  File /r "${BINARY_PATH}\"
  DetailPrint "Installing ${__SECTION__} ... Done"
SectionEnd


; Section "Tesseract 5.0" SEC02
;     ReadRegStr $R0 HKCU "${CHROME}" "UninstallString"
;     DetailPrint "Installing ${__SECTION__}"
;     File "/oname=$TEMP\tesseract-ocr-w64-setup-v5.0.0-alpha.20200223.exe" "setup\tesseract-ocr-w64-setup-v5.0.0-alpha.20200223.exe" 
;     ExecWait $TEMP\tesseract-ocr-w64-setup-v5.0.0-alpha.20200223.exe $0
;     DetailPrint "Installing ${__SECTION__} ... $0"
; SectionEnd


; Section "WindowsApplicationDriver" SEC03
;     DetailPrint "Installing ${__SECTION__}"
;     File "/oname=$TEMP\WindowsApplicationDriver.msi" "setup\WindowsApplicationDriver.msi"
;     ExecWait "msiexec.exe /i $TEMP\WindowsApplicationDriver.msi" $0
;     DetailPrint "Installing ${__SECTION__} ... $0"
; SectionEnd


Section "-Variable" SEC04
    ; AGENT_MODULE
    EnVar::Delete "AGENT_MODULE" 
    EnVar::AddValue "AGENT_MODULE" "PY"

    ; PYTHON_EXECUTABLE
    EnVar::Delete "PYTHON_EXECUTABLE" 
    EnVar::AddValue "PYTHON_EXECUTABLE" "$INSTDIR\python\Scripts\pythonw.exe"
SectionEnd

Section "-Configure File" SEC05
    ; FileOpen $9 $INSTDIR\pam.conf w ;Opens a Empty File and fills it
    FileOpen $9 $INSTDIR\pam.conf w ;Opens a Empty File and fills it
    FileWrite $9 "APP_DRIVER:$\r$\n"
    FileWrite $9 "  APP_DRIVER: $INSTDIR\programs\Windows Application Driver\WinAppDriver.exe$\r$\n"
    FileWrite $9 "EXTERNAL_PROG:$\r$\n"
    FileWrite $9 "  PPM: $INSTDIR\ext_program\alabs-ppm.exe$\r$\n"
    FileWrite $9 "  TESSERACT_EXECUTABLE: $INSTDIR\programs\Tesseract-OCR\tesseract.exe$\r$\n"
    FileWrite $9 "MANAGER:$\r$\n"
    FileWrite $9 "  IP: 127.0.0.1$\r$\n"
    FileWrite $9 "  LOG_LEVEL: info$\r$\n"
    FileWrite $9 "  PORT: 8012$\r$\n"
    FileWrite $9 "  VARIABLE_MANAGER_IP: 127.0.0.1$\r$\n"
    FileWrite $9 "  VARIABLE_MANAGER_PORT: 8012$\r$\n"
    FileWrite $9 "PATH:$\r$\n"
    FileWrite $9 "  CURRENT_PAM_LOG_DIR: $INSTDIR\logs$\r$\n"
    FileWrite $9 "  OPERATION_IN_FILE: $INSTDIR\logs\operation.in$\r$\n"
    FileWrite $9 "  OPERATION_LOG: $INSTDIR\logs\operation.log$\r$\n"
    FileWrite $9 "  OPERATION_STDERR_FILE: $INSTDIR\logs\operation.stderr$\r$\n"
    FileWrite $9 "  OPERATION_STDOUT_FILE: $INSTDIR\logs\operation.stdout$\r$\n"
    FileWrite $9 "  PAM_CONF: $INSTDIR\pam.conf$\r$\n"
    FileWrite $9 "  PAM_LOG: $INSTDIR\logs\pam.log$\r$\n"
    FileWrite $9 "  PLUGIN_LOG: $INSTDIR\logs\plugin.log$\r$\n"
    FileWrite $9 "  PLUGIN_STDERR_FILE: $INSTDIR\logs\plugin.stderr$\r$\n"
    FileWrite $9 "  PLUGIN_STDOUT_FILE: $INSTDIR\logs\plugin.stdout$\r$\n"
    FileWrite $9 "  RESULT_DIR: $INSTDIR\test_result$\r$\n"
    FileWrite $9 "  RESULT_FILE: $INSTDIR\test_result\TestRunResult.json$\r$\n"
    FileWrite $9 "  RESULT_SCREENSHOT_DIR: $INSTDIR\test_result\ScreenShot$\r$\n"
    FileWrite $9 "  USER_PARAM_VARIABLES: $INSTDIR\user_param_variables.json$\r$\n"
    FileWrite $9 "WEB_DRIVER:$\r$\n"
    FileWrite $9 "  CHROME_DRIVER_WINDOWS: $INSTDIR\programs\web_drivers\chromedriver.exe$\r$\n"
    FileWrite $9 "  WEB_DRIVER_EXECUTOR_URL: ''$\r$\n"
    FileClose $9 ;Closes the filled file
SectionEnd