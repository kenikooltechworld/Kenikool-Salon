@echo off
echo Installing React + Vite dependencies...
echo.

REM Core dependencies
call npm install react-router-dom
call npm install axios
call npm install @tanstack/react-query

REM Utility libraries
call npm install class-variance-authority
call npm install clsx
call npm install tailwind-merge
call npm install date-fns

REM PDF and Excel
call npm install jspdf
call npm install jspdf-autotable
call npm install papaparse
call npm install xlsx

REM Charts and QR
call npm install chart.js react-chartjs-2
call npm install qrcode

REM UI and Icons
call npm install lucide-react
call npm install sonner

REM Dev dependencies (types)
call npm install -D @types/papaparse
call npm install -D @types/qrcode

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo NEXT STEPS:
echo 1. Install Tailwind CSS v4 yourself (I'm not familiar with v4 setup)
echo 2. Run: npm run dev
echo.
pause
