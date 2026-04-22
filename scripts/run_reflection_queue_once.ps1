param(
    [int]$Limit = 10,
    [switch]$AllowInProcess
)

$arguments = @(".\scripts\run_reflection_queue_once.py", "--limit", "$Limit")
if ($AllowInProcess) {
    $arguments += "--allow-in-process"
}

& ".\.venv\Scripts\python.exe" @arguments
