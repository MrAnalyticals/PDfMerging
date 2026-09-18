# Smoke test script: copy latest exe, start it, wait for server, POST PDFs, save merged output, stop server
Write-Output "COPYING..."
$src='C:\Users\user\OneDrive\Computing\Microsoft\Visual Studio Code VSC\Projects\PDfMerging\dist\PDFMerger.exe'
$dest='C:\Users\user\OneDrive\Computing\Microsoft\Visual Studio Code VSC\Projects\Ref PDf Merge\PDFMerger.exe'
Copy-Item -Path $src -Destination $dest -Force
Get-Item $dest | Format-List FullName,LastWriteTime,Length

Write-Output "STARTING..."
$p = Start-Process -FilePath $dest -PassThru
$pid = $p.Id
Write-Output "PID=$pid"

Write-Output "POLLING..."
$ready=$false
for($i=0;$i -lt 30;$i++){
    try{
        $r = Invoke-WebRequest -Uri 'http://127.0.0.1:5000' -UseBasicParsing -TimeoutSec 2
        Write-Output ("HTTP_STATUS=$($r.StatusCode)")
        if($r.StatusCode -eq 200){ $ready=$true; break }
    } catch { Write-Output ("attempt " + $i + ": not ready") }
    Start-Sleep -Seconds 1
}
if(-not $ready){ Write-Output "SERVER_NOT_READY"; Stop-Process -Id $pid -Force; exit 2 }
Write-Output "SERVER_READY"

$folder='C:\Users\user\Downloads\HopeStreetLease'
$files = Get-ChildItem -Path $folder -Filter '*.pdf' -File -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
if(-not $files){ Write-Output 'NO_PDFS_FOUND'; Stop-Process -Id $pid -Force; exit 3 }
Write-Output ("FILES_FOUND=" + $files.Count)
foreach($f in $files){ Write-Output $f }

$out=Join-Path $env:TEMP 'merged_output_from_test.pdf'
$argsList=@()
foreach($f in $files){ $argsList += '-F'; $argsList += "pdf_files=@$f" }
$argsList += 'http://127.0.0.1:5000/merge'
$argsList += '-o'
$argsList += $out
Write-Output ('CURL ARGS: ' + ($argsList -join ' | '))
$proc = Start-Process -FilePath 'curl.exe' -ArgumentList $argsList -Wait -NoNewWindow -PassThru
Write-Output ('CURL_EXIT=' + $proc.ExitCode)

if(Test-Path $out){ $t=Get-Item $out; Write-Output ('MERGED_OK: ' + $t.FullName + ' | ' + $t.LastWriteTime + ' | ' + [math]::Round($t.Length/1024,2) + 'KB') } else { Write-Output 'MERGED_MISSING' }

Write-Output ('STOPPING PID=' + $pid)
Stop-Process -Id $pid -Force

Write-Output 'DONE'
