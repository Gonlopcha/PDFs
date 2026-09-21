[Setup]
; --- Definimos la carpeta de origen (salida de Nuitka) ---
#define SourceDir "C:\Users\gonzalo.lopez\Documents\GitHub\PDFs\PDFTool.dist"
#define IconFile "C:\Users\gonzalo.lopez\Documents\GitHub\PDFs\icono.ico"

AppName=PDF Tool
AppVersion=1.0.0
AppPublisher=Gonzalo Lopez
DefaultDirName={pf}\PDFTool
DefaultGroupName=PDF Tool
OutputDir=C:\Users\gonzalo.lopez\Documents\GitHub\PDFs\instalador
OutputBaseFilename=PDFTool_v1.0.0
Compression=lzma
SolidCompression=yes
SetupIconFile={#IconFile}
UninstallDisplayIcon={app}\icono.ico

[Files]
; Copia TODO el contenido de la carpeta SourceDir a la carpeta de instalacion {app}
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Asegurar que el icono este disponible en la carpeta de instalacion
Source: "{#IconFile}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\PDF Tool";       Filename: "{app}\PDFTool.exe"; IconFilename: "{app}\icono.ico"
Name: "{commondesktop}\PDF Tool"; Filename: "{app}\PDFTool.exe"; IconFilename: "{app}\icono.ico"

[Run]
Filename: "{app}\PDFTool.exe"; Description: "Iniciar PDF Tool"; Flags: nowait postinstall skipifsilent
