; Inno Setup script for My Phone ERP — produces a one-click Setup.exe
; Build: iscc installer\myphone_setup.iss  (after PyInstaller has produced dist\MyPhoneERP)

#define AppName "My Phone ERP"
#define AppVersion "1.0.0"
#define AppPublisher "DevNest System"
#define AppExe "MyPhoneERP.exe"

[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\MyPhoneERP
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=..\dist_installer
OutputBaseFilename=MyPhoneERP-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
; Program Files needs admin; data is written to %LOCALAPPDATA% at runtime.
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
; The whole PyInstaller output folder produced by: pyinstaller myphone.spec
Source: "..\backend\dist\MyPhoneERP\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
