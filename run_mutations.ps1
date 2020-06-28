Write-Host("`n----- Cleaning up old files -----")
if(Test-Path ./html){
    Write-Host("Deleting old directory and contents")
    Remove-Item -Recurse -Force ./html | Out-Null
}
if(Test-Path ./html){
    Write-Host("Could not delete old html report directory directory")
    Exit
}
if(Test-Path ./.mutmut-cache) {
    Write-Host("Deleting old cache file")
    Remove-Item ./.mutmut-cache | Out-Null
}
if(Test-Path ./.mutmut-cache) {
    Write-Host("Could not delete .mutmut-cache")
    Exit
}

Write-Host("`n----- Executing mutation tests -----")
mutmut run

Write-Host("`n----- Generating HTML Report -----")
mutmut html
if($LastExitCode -ne 0){
    Write-Host("'mutmut html' failed with status: $LastExitCode")
    Exit
}

Write-Host("Opening Report")
./html/index.html