[Setup]
AppName=Revisa_Tracks
AppVersion=1.0
DefaultDirName={pf}\Revisa_Tracks
DefaultGroupName=Revisa Tracks GPS
OutputDir=.
OutputBaseFilename=setup
Compression=lzma
SolidCompression=yes
SetupIconFile=C:\1\t.ico

[Files]
Source: "C:\1\dist\RT2.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\1\t.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Revisa Tracks GPS"; Filename: "{app}\RT2.exe"; WorkingDir: "{app}"
Name: "{group}\Uninstall Revisa Tracks GPS"; Filename: "{uninstallexe}"; IconFilename: "{app}\t.ico"

[CustomMessages]
AboutMsg=Este software fue creado por Ecooempresas. Para más información, visite https://www.facebook.com/ecooempresas/.

[Run]
Filename: "{app}\RT2.exe"; Description: "{cm:LaunchProgram,Revisa Tracks GPS}"; Flags: nowait postinstall skipifsilent

[Code]
procedure AboutButtonClick(Sender: TObject);
begin
  MsgBox(CustomMessage('AboutMsg'), mbInformation, MB_OK);
end;

procedure InitializeWizard;
var
  AboutButton: TButton;
begin
  AboutButton := TButton.Create(WizardForm);
  AboutButton.Parent := WizardForm;
  AboutButton.Caption := '&Acerca de...';
  AboutButton.Left := WizardForm.CancelButton.Left;
  AboutButton.Top := WizardForm.CancelButton.Top + WizardForm.CancelButton.Height + 6;
  AboutButton.Width := WizardForm.CancelButton.Width;
  AboutButton.OnClick := @AboutButtonClick;
end;
