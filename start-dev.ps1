# Starts the WAMUGII backend and frontend together, each in its own window.
$root = $PSScriptRoot

Start-Process powershell -ArgumentList @(
  '-NoExit','-Command',
  "cd '$root\wamugii-backend'; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload"
)

Start-Process powershell -ArgumentList @(
  '-NoExit','-Command',
  "cd '$root\wamugii-frontend'; npm run dev"
)

Write-Host "Backend -> http://localhost:8000   Frontend -> http://localhost:5173"