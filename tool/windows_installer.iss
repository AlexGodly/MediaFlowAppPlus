; Inno Setup script for the MediaFlow Windows installer.
; Built in CI: ISCC /DAppVersion=<version> /DSourceDir=<Release folder> /DOutputDir=<dist> /DIconFile=<app_icon.ico> tool\windows_installer.iss

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{5D3A9E47-2B8C-4F61-A0D3-7E1C9B4F8A26}
AppName=MediaFlow Plus
AppVersion={#AppVersion}
AppPublisher=Alex Godly
DefaultDirName={autopf}\MediaFlow Plus
DefaultGroupName=MediaFlow Plus
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir={#OutputDir}
OutputBaseFilename=MediaFlowPlus-{#AppVersion}-Windows-x64-Setup
SetupIconFile={#IconFile}
UninstallDisplayIcon={app}\MediaFlow.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\MediaFlow Plus"; Filename: "{app}\MediaFlow.exe"
Name: "{autodesktop}\MediaFlow Plus"; Filename: "{app}\MediaFlow.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\MediaFlow.exe"; Description: "Open MediaFlow Plus"; Flags: nowait postinstall skipifsilent
