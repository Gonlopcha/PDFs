[Setup]
; --- Definimos la carpeta de origen (salida de Nuitka) ---
#define SourceDir "C:\Users\gonzalo.lopez\Documents\GitHub\PDFs\PDFTool.dist"

AppName=PDF Tool
AppVersion=1.0.0
AppPublisher=Gonzalo Lopez
DefaultDirName={pf}\PDFTool
DefaultGroupName=PDF Tool
OutputDir=C:\Users\gonzalo.lopez\Documents\GitHub\PDFs\instalador
OutputBaseFilename=PDFTool_v1.0.0
Compression=lzma
SolidCompression=yes
; --- Si tienes un icono, descomenta la siguiente linea ---
; SetupIconFile={#SourceDir}\pdf_tool_icon.ico

[Files]
; Copia TODO el contenido de la carpeta SourceDir a la carpeta de instalacion {app}
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\PDF Tool";    Filename: "{app}\PDFTool.exe"
Name: "{commondesktop}\PDF Tool"; Filename: "{app}\PDFTool.exe"

[Run]
Filename: "{app}\PDFTool.exe"; Description: "Iniciar PDF Tool"; Flags: nowait postinstall skipifsilent
