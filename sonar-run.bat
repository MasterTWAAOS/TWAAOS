@echo off
echo Starting SonarQube analysis for FIESC exam scheduling application...
echo.

echo Checking if SonarQube is running...
curl -s http://localhost:9000/api/system/status > nul 2>&1
if %errorlevel% neq 0 (
    echo SonarQube is not yet running or still initializing.
    echo Please make sure SonarQube is running at http://localhost:9000
    echo and then run this script again.
    exit /b 1
)

echo SonarQube is running! Proceeding with analysis...
echo.

echo Running SonarQube analysis...
docker run --rm ^
  -e SONAR_HOST_URL="http://host.docker.internal:9000" ^
  -e SONAR_LOGIN="admin" ^
  -e SONAR_PASSWORD="admin" ^
  -v "%cd%:/usr/src" ^
  -w /usr/src ^
  sonarsource/sonar-scanner-cli:4.8 ^
  -D"sonar.projectKey=FIESC" ^
  -D"sonar.projectName=FIESC Exam Scheduling App" ^
  -D"sonar.projectVersion=1.0" ^
  -D"sonar.sources=backend,frontend/src" ^
  -D"sonar.exclusions=**/node_modules/**,**/*.spec.js,**/tests/**,**/__pycache__/**,**/*.pyc" ^
  -D"sonar.sourceEncoding=UTF-8"

echo.
echo Analysis complete!
echo Open http://localhost:9000 in your browser to see the results.
echo Default credentials: admin/admin (please change on first login)
