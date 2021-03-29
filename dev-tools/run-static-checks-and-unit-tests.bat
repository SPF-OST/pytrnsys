rem Run from top-level directory

@echo on

if exist test-results (
    rmdir /s /q test-results
)

pylint pytrnsys pytrnsys_examples tests
pytest ^
    --cov=pytrnsys --cov-report html:test-results/coverage --cov-report term^
    --html=test-results/report/report.html ^
    -m "not manual"
