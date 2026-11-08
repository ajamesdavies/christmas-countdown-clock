param([switch]$ConfigureWifi)

$ErrorActionPreference = 'Stop'
$boards = @(Get-Volume -FileSystemLabel CIRCUITPY | ForEach-Object {
    if ($_.DriveLetter) {
        $root = "$($_.DriveLetter):\"
        $boot = Join-Path $root 'boot_out.txt'
        if ((Test-Path -LiteralPath $boot) -and
            (Select-String -LiteralPath $boot -SimpleMatch 'Board ID:lilygo_tdisplay_s3' -Quiet)) {
            $root
        }
    }
})
if ($boards.Count -ne 1) {
    throw 'Connect exactly one LILYGO T-Display S3 running CircuitPython.'
}
if ($ConfigureWifi) {
    $ssid = Read-Host 'Enter your 2.4 GHz Wi-Fi network name'
    if ([string]::IsNullOrWhiteSpace($ssid) -or [Text.Encoding]::UTF8.GetByteCount($ssid) -gt 32) {
        throw 'Enter a Wi-Fi network name between 1 and 32 bytes.'
    }
    $secret = Read-Host 'Enter the Wi-Fi password (leave blank for an open network)' -AsSecureString
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
    try {
        $password = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
        $settingsPath = Join-Path $boards[0] 'settings.toml'
        $settings = if (Test-Path -LiteralPath $settingsPath) { [IO.File]::ReadAllText($settingsPath) } else { '' }
        $settings = ($settings -replace '(?m)^\s*CLOCK_WIFI_(SSID|PASSWORD)\s*=.*(?:\r?\n|$)', '').TrimEnd()
        $wifiSettings = @(
            'CLOCK_WIFI_SSID = ' + (ConvertTo-Json -InputObject $ssid -Compress)
            'CLOCK_WIFI_PASSWORD = ' + (ConvertTo-Json -InputObject $password -Compress)
        ) -join "`n"
        $contents = if ($settings) { "$wifiSettings`n`n$settings`n" } else { "$wifiSettings`n" }
        [IO.File]::WriteAllText($settingsPath, $contents, [Text.UTF8Encoding]::new($false))
    } finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
        Remove-Variable password, wifiSettings, contents, settings -ErrorAction SilentlyContinue
    }
    Write-Host 'Wi-Fi settings saved on the clock. It will try to sync at startup.'
}

$stamp = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
Set-Content -LiteralPath (Join-Path $boards[0] 'sync.txt') -Value $stamp -Encoding ascii
Write-Host 'Time sent. The countdown will update after CircuitPython reloads.'

