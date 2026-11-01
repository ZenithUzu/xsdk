param(
    [string]$Destination = 'C:\xsdk-windows',
    [string]$Compiler = 'C:\xsdk-tools\compiler',
    [string]$Msys = 'C:\msys64',
    [string]$Bundle = ''
)
$ErrorActionPreference = 'Stop'
if ($Destination -match '\s' -or $Compiler -match '\s') { throw 'Usa rutas sin espacios.' }
if (Test-Path $Destination) { throw 'Elige una carpeta nueva; no se reemplazan archivos existentes.' }
$git = Join-Path $Msys 'usr\bin\git.exe'
if (-not (Test-Path $git)) { throw 'Instala y actualiza MSYS2 primero. Esta instalación requiere Git de MSYS2.' }
& $git clone --branch main https://github.com/ZenithUzu/xsdk.git $Destination
if ($LASTEXITCODE -ne 0) { throw 'No se pudo clonar xSDK.' }
if ($Bundle) {
    if (Test-Path $Compiler) { throw 'Elige una carpeta nueva para el compilador del paquete.' }
    $expected = (Get-Content "$Bundle.sha256" -Raw).Trim().Split(' ')[0]
    if ($expected -notmatch '^[a-fA-F0-9]{64}$') { throw 'Checksum inválido.' }
    if ((Get-FileHash $Bundle -Algorithm SHA256).Hash -ne $expected) { throw 'Checksum del paquete incorrecto.' }
    $stage = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())
    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $zip = [IO.Compression.ZipFile]::OpenRead((Resolve-Path $Bundle))
        try {
            foreach ($entry in $zip.Entries) {
                $name = $entry.FullName.Replace('\', '/')
                if ($name.StartsWith('/') -or $name.Contains(':') -or ($name.Split('/') -contains '..')) {
                    throw 'El paquete contiene una ruta insegura.'
                }
            }
        } finally { $zip.Dispose() }
        Expand-Archive -LiteralPath $Bundle -DestinationPath $stage
        if (-not (Test-Path "$stage\compiler\bin\powerpc-xsdk-elf-g++.exe")) { throw 'Paquete incompleto.' }
        New-Item -ItemType Directory -Force (Split-Path $Compiler) | Out-Null
        Move-Item "$stage\compiler" $Compiler
        Write-Host 'Compilador instalado. Configura su ruta en la interfaz y pulsa Verificar herramientas.'
    } finally {
        if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }
    }
}
Write-Host "Listo: $Destination\Iniciar-Windows.cmd"
Write-Host 'Sin paquete: construye Dependencias, Compilador y Shaders desde la interfaz.'
