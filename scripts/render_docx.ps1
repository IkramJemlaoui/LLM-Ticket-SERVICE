param(
    [Parameter(Mandatory = $true)][string]$InputPath,
    [Parameter(Mandatory = $true)][string]$OutputPath
)

$ErrorActionPreference = "Stop"
$wordApp = $null
$document = $null

try {
    $resolvedInput = (Resolve-Path -LiteralPath $InputPath).Path
    $resolvedOutput = [System.IO.Path]::GetFullPath($OutputPath)
    $wordApp = New-Object -ComObject Word.Application
    $wordApp.Visible = $false
    $wordApp.DisplayAlerts = 0
    $wordApp.ScreenUpdating = $false
    $document = $wordApp.Documents.Open($resolvedInput, $false, $true, $false)
    $document.Repaginate()
    $pageCount = $document.ComputeStatistics(2)
    $document.ExportAsFixedFormat($resolvedOutput, 17)
    Write-Output "PDF=$resolvedOutput"
    Write-Output "PAGES=$pageCount"
}
finally {
    if ($null -ne $document) {
        $document.Close($false)
    }
    if ($null -ne $wordApp) {
        $wordApp.Quit()
    }
}
