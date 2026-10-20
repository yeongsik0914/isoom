@echo off
chcp 65001 >nul
echo ==============================================================================
echo   🚀 아이숨 (Aisum) - Google Cloud Run 원클릭 프로덕션 배포 런처
echo ==============================================================================

cd /d "%~dp0\.."

python scripts\deploy_cloud_run.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 배포 중 오류가 발생했습니다. 위의 메시지를 확인해주세요.
    pause
)
