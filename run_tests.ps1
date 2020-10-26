# Individual tests can be run with the following command: python -m unittest largefilehahs.tests.<test_file>
# Make sure to not include the .py extension when specifying a value for the <test_file>

Write-Host("----- Running Unit Tests -----")
coverage run --omit=./largefilehash/tests/* --source=largefilehash.src --branch --module largefilehash.tests._run_all
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
