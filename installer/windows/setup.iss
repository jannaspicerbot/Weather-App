; Weather App - Inno Setup Installer Script
;
; This script creates a professional Windows installer for the Weather App
; that includes:
; - Application files from PyInstaller build
; - Start Menu shortcuts
; - Desktop shortcut (optional)
; - Proper uninstaller
; - Custom icon

#define MyAppName "Weather App"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Weather App"
#define MyAppURL "https://github.com/jannaspicerbot/Weather-App"
#define MyAppExeName "WeatherApp.exe"
#define MyAppIconFile "..\..\weather_app\resources\icons\weather-app.ico"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={{8F3E9A2C-1B4D-4E5F-9C8A-7D6E5F4C3B2A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Uncomment the following line to run in non administrative install mode (install for current user only.)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=output
OutputBaseFilename=WeatherAppSetup
SetupIconFile={#MyAppIconFile}
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
; Uncomment if you add a LICENSE file
; LicenseFile=..\..\LICENSE
; Uncomment if you want to show README before installation
; InfoBeforeFile=..\..\README.md

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "Launch at Windows startup"; GroupDescription: "Startup Options:"; Flags: unchecked

[Files]
; Include all files from the PyInstaller build
Source: "dist\WeatherApp\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
; Start Menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop shortcut (optional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"

; Startup shortcut (optional)
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
; Launch the app after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up user data on uninstall (optional - commented out to preserve user data)
; Type: filesandordirs; Name: "{%APPDATA}\WeatherApp"

[Code]
// Custom code for installer

function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Any post-installation tasks can go here
  end;
end;

function InitializeUninstall(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;

  // Ask if user wants to keep their data
  if MsgBox('Do you want to keep your Weather App data (database and settings)?' + #13#10 + #13#10 +
            'Click Yes to keep your data (you can reinstall later).' + #13#10 +
            'Click No to delete all data.',
            mbConfirmation, MB_YESNO) = IDNO then
  begin
    // Delete user data folder
    DelTree(ExpandConstant('{%APPDATA}\WeatherApp'), True, True, True);
  end;
end;

[Messages]
; Custom messages
WelcomeLabel2=This will install [name/ver] on your computer.%n%nWeather App is a personal weather station dashboard that collects and displays data from Ambient Weather stations.%n%nYou will need API credentials from ambientweather.net to use this application.
