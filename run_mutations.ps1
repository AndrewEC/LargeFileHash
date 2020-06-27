Write-Host("`n----- Creating report directory -----")
if(Test-Path ./cosmic-ray-reports){
    Write-Host("Deleting old directory and contents")
    Remove-Item -Recurse -Force ./cosmic-ray-reports | Out-Null
}
if(Test-Path ./cosmic-ray-reports){
    Write-Host("Could not delete old cosmic-ray-reports directory")
    Exit
}
New-Item -ItemType directory -Path ./cosmic-ray-reports | Out-Null
if(-Not (Test-Path ./cosmic-ray-reports)){
    Write-Host("Could not create ./cosmic-ray-reports output directory")
    Exit
}

Write-Host("`n----- Initializing cosmic-ray session -----")
cosmic-ray init config.toml ./cosmic-ray-reports/session.sqlite
if($LastExitCode -ne 0){
    Write-Host("'cosmic-ray init config.toml ./cosmic-ray-reports/session.sqlite' with status: $LastExitCode")
    Exit
}

Write-Host("`n----- Executing mutation tests -----")
cosmic-ray exec ./cosmic-ray-reports/session.sqlite
if($LastExitCode -ne 0){
    Write-Host("'cosmic-ray exec ./cosmic-ray-reports/session.sqlite' failed with status: $LastExitCode")
    Exit
}

Write-Host("`n----- Generating HTML Report -----")
cr-html ./cosmic-ray-reports/session.sqlite > ./cosmic-ray-reports/report.html
if($LastExitCode -ne 0){
    Write-Host("'cr-html ./cosmic-ray-reports/session.sqlite > ./cosmic-ray-reports/report.html' failed with status: $LastExitCode")
    Exit
}

Write-Host("Opening Report")
./cosmic-ray-reports/report.html