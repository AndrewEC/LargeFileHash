Write-Host("----- Running Unit Tests -----")
coverage run --omit=./largefilehash/tests/* --branch --module largefilehash.tests._run_all
if($LastExitCode -ne 0){
    Write-Host("'coverage run --omit=./largefilehash/tests/* --branch --module largefilehash.tests._run_all' failed with status: $LastExitCode")
    Exit
}

Write-Host("`n----- Creating HTML Coverage Report -----")
coverage html
if($LastExitCode -ne 0){
    Write-Host("'coverage html' failed with status: $LastExitCode")
    Exit
}

Write-Host("`n----- Opening Report -----")
./htmlcov/index.html
