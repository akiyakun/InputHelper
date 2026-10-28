<#
.SYNOPSIS
  新しいWindows PCにInputHelperのWindows側設定を導入する。

.DESCRIPTION
  何度実行しても同じ状態になるように作っています。済んでいる手順は飛ばします。
  - wingetでAutoHotkey v2、Google日本語入力、PowerToysをインストール（Chromeは未導入の場合のみ）
  - enter-newline.ahk をスタートアップに登録して起動
  - PowerToys Keyboard Managerに Ctrl+Shift+9 → 無変換、Ctrl+Shift+0 → 変換 を設定
  - PowerToysのログオン時自動起動とKeyboard ManagerをON
  - Google日本語入力を既定の入力方式にする
  GUIでしかできない手順（キー設定のインポート、Chrome拡張の読み込みなど）は最後に一覧表示します。

.PARAMETER Synergy
  Synergy（Windows側クライアント）もインストールする。

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\windows\setup\setup-windows.ps1
#>
# Get-Helpで上のヘルプを表示するため、#Requiresはヘルプより後に置く
#Requires -Version 5.1
param(
    [switch]$Synergy
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

function Write-Step($Message) { Write-Host "==> $Message" -ForegroundColor Cyan }
function Write-Done($Message) { Write-Host "    $Message" -ForegroundColor Green }
function Write-Note($Message) { Write-Host "    $Message" -ForegroundColor Yellow }

function Install-WingetPackage($Id) {
    $null = winget list --id $Id -e --accept-source-agreements 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Done "$Id はインストール済み"
        return
    }
    Write-Note "$Id をインストールします（UACの確認が出たら「はい」を押してください）"
    winget install --id $Id -e --accept-source-agreements --accept-package-agreements
    # wingetの終了コード: https://github.com/microsoft/winget-cli/blob/master/doc/windows/package-manager/winget/returnCodes.md
    switch ('{0:X8}' -f $LASTEXITCODE) {
        '00000000' { Write-Done "$Id をインストールしました" }
        { $_ -in '8A150109', '8A15010B' } { Write-Note "$Id をインストールしました。完了にはPCの再起動が必要です" }
        { $_ -in '8A150061', '8A15010D' } { Write-Done "$Id はインストール済み" }
        default { throw "$Id のインストールに失敗しました（exit=0x$_）" }
    }
}

# PowerShell 5.1と7で引数中の " の扱いが異なるため、引数文字列を自前で組み立てて渡す。
function Invoke-Native($FilePath, $Arguments) {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $psi.Arguments = $Arguments
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $p = [System.Diagnostics.Process]::Start($psi)
    $stdout = $p.StandardOutput.ReadToEnd()
    $stderr = $p.StandardError.ReadToEnd()
    $p.WaitForExit()
    [pscustomobject]@{ ExitCode = $p.ExitCode; StdOut = $stdout; Output = $stdout + $stderr }
}

# Windowsのコマンドライン引数の規則（CommandLineToArgvW）に従って1つの引数として引用する。
# " の直前と末尾のバックスラッシュは二重にする必要がある。
function ConvertTo-NativeArg($Value) {
    $escaped = [regex]::Replace($Value, '(\\*)"', { param($m) ($m.Groups[1].Value * 2) + '\"' })
    $escaped = [regex]::Replace($escaped, '(\\+)$', { param($m) $m.Groups[1].Value * 2 })
    '"' + $escaped + '"'
}

function Invoke-Dsc($Verb, $Module, $Resource, $InputJson) {
    $r = Invoke-Native $dsc "$Verb --module $Module --resource $Resource --input $(ConvertTo-NativeArg $InputJson)"
    if ($r.ExitCode -ne 0) { throw "PowerToys.DSC $Verb $Module/$Resource に失敗しました: $($r.Output)" }
    # 1行目が結果のJSON（setの2行目は変更されたプロパティの一覧）
    $r.StdOut -split "`r?`n" | Where-Object { $_.Trim() } | Select-Object -First 1 | ConvertFrom-Json
}

function Get-PowerToysDir {
    foreach ($dir in @("$env:LOCALAPPDATA\PowerToys", "$env:ProgramFiles\PowerToys")) {
        if (Test-Path (Join-Path $dir 'PowerToys.exe')) { return $dir }
    }
    throw 'PowerToysが見つかりません'
}

# 1. アプリのインストール
Write-Step 'アプリのインストール'
Install-WingetPackage 'AutoHotkey.AutoHotkey'
Install-WingetPackage 'Google.JapaneseIME'
Install-WingetPackage 'Microsoft.PowerToys'
# ChromeはGoogleのインストーラで入れるとwingetのIDと結び付かないため、実行ファイルの有無で判定する
$chromeInstalled = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe"
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($chromeInstalled) { Write-Done 'Google Chrome はインストール済み' } else { Install-WingetPackage 'Google.Chrome' }
if ($Synergy) { Install-WingetPackage 'Symless.Synergy' }

# 2. AutoHotkey（ClaudeのEnterを改行にする）
Write-Step 'AutoHotkeyスクリプトをスタートアップに登録'
$ahkScript = Join-Path $RepoRoot 'windows\autohotkey\enter-newline.ahk'
$lnkPath = Join-Path ([Environment]::GetFolderPath('Startup')) 'enter-newline.lnk'
$shell = New-Object -ComObject WScript.Shell
$lnk = $shell.CreateShortcut($lnkPath)
$lnk.TargetPath = $ahkScript
$lnk.WorkingDirectory = Split-Path $ahkScript
$lnk.Save()
Write-Done "スタートアップに登録: $lnkPath"
# #SingleInstance Force のため、起動済みでも再読み込みになる
Start-Process $ahkScript
Write-Done 'enter-newline.ahk を起動しました'

# 3. PowerToys Keyboard Manager（Ctrl+Shift+9/0 → 無変換/変換）
Write-Step 'PowerToys Keyboard Managerの再マップ'
$ptDir = Get-PowerToysDir
$dsc = Join-Path $ptDir 'PowerToys.DSC.exe'
# DSCのsetはプロファイル全体を置き換えるため、現在の設定を読み、ほかの再マップを残したまま2件だけ入れ替える。
$kbm = (Invoke-Dsc get KeyboardManager profile '{}').profile
# DSCはキー名「IME Non-Convert」を受け付けないため、仮想キーコードで指定する（0x1D=無変換、0x1C=変換）
$ours = @(
    [pscustomobject]@{ from = 'Ctrl+Shift+9'; to = '0x1D' }
    [pscustomobject]@{ from = 'Ctrl+Shift+0'; to = '0x1C' }
)
# GUIで作ると LCtrl+LShift+9 のように左右付きで保存されるため、左右を外して比べ、同じショートカットは置き換える
$others = @($kbm.shortcuts | Where-Object { $_ -and -not (($_.from -replace '\b[LR](Ctrl|Shift|Alt|Win)\b', '$1') -in $ours.from -and -not $_.targetApp) })
$merged = [pscustomobject]@{ profile = [pscustomobject]@{ keys = @($kbm.keys | Where-Object { $_ }); shortcuts = $others + $ours } }
$null = Invoke-Dsc set KeyboardManager profile ($merged | ConvertTo-Json -Depth 10 -Compress)
Write-Done "Ctrl+Shift+9 → 無変換、Ctrl+Shift+0 → 変換 を設定しました（ほかの再マップ $($others.Count) 件はそのまま）"

# 4. PowerToysの自動起動とKeyboard Manager有効化
# DSCの App settings は、渡さなかった項目（各モジュールの有効/無効など）を既定値に戻す。
# 現在の設定をgetで読み、2項目だけ変えて全体を渡す。
Write-Step 'PowerToysの自動起動とKeyboard Managerを有効化'
$app = Invoke-Dsc get App settings '{}'
$app.settings.startup = $true
$app.settings.enabled | Add-Member -NotePropertyName 'Keyboard Manager' -NotePropertyValue $true -Force
$null = Invoke-Dsc set App settings ($app | ConvertTo-Json -Depth 20 -Compress)
Write-Done 'startup と Keyboard Manager をONにしました'
if (-not (Get-Process 'PowerToys' -ErrorAction SilentlyContinue)) {
    Start-Process (Join-Path $ptDir 'PowerToys.exe')
}
$engine = $null
for ($i = 0; $i -lt 30 -and -not $engine; $i++) {
    Start-Sleep -Seconds 1
    $engine = Get-Process 'PowerToys.KeyboardManagerEngine' -ErrorAction SilentlyContinue
}
if ($engine) {
    Write-Done 'Keyboard Managerのエンジンが動作中'
} else {
    Write-Note 'Keyboard Managerのエンジンが起動していません。PowerToysの設定画面で確認してください'
}

# 5. Google日本語入力を既定の入力方式に
Write-Step 'Google日本語入力を既定の入力方式に設定'
$googleTip = Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\CTF\TIP' -ErrorAction SilentlyContinue |
    Where-Object { (Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue).'(default)' -like '*Google*' -or
                   (Get-ItemProperty "$($_.PSPath)\LanguageProfile\0x00000411\*" -ErrorAction SilentlyContinue).Description -like '*Google*' } |
    Select-Object -First 1
$profileKey = if ($googleTip) { Get-ChildItem "$($googleTip.PSPath)\LanguageProfile\0x00000411" -ErrorAction SilentlyContinue | Select-Object -First 1 }
if ($profileKey) {
    $tip = "0411:$($googleTip.PSChildName)$($profileKey.PSChildName)"
    $langs = Get-WinUserLanguageList
    $ja = $langs | Where-Object { $_.LanguageTag -eq 'ja' } | Select-Object -First 1
    if (-not $ja) {
        Write-Note '言語の一覧に日本語がありません。設定 → 時刻と言語 → 言語と地域で日本語を追加してから、もう一度実行してください'
    } else {
        if (-not ($ja.InputMethodTips -contains $tip)) {
            $ja.InputMethodTips.Add($tip)
            Set-WinUserLanguageList $langs -Force
        }
        Set-WinDefaultInputMethodOverride -InputTip $tip
        Write-Done "既定の入力方式: $tip"
    }
} else {
    Write-Note 'Google日本語入力の入力方式が見つかりません。再起動後にもう一度実行してください'
}

Write-Host ''
Write-Host '自動でできる設定は完了しました。残りは手作業です（docs/windows-setup.md の「手作業」を参照）:' -ForegroundColor Cyan
Write-Host '  1. Google日本語入力のプロパティ → キー設定「編集...」→ 編集 → インポートで google-ime\keymap-windows.txt を読み込む'
Write-Host '  2. Chromeの chrome://extensions でデベロッパーモードをONにし、chrome-extensions フォルダを読み込む'
Write-Host '  3. Slackの環境設定で「Enterで改行」を選ぶ（Ctrl+Enterで送信）'
Write-Host '  4. Windows上のClaudeでEnter＝改行、Ctrl+Enter＝送信になることを確認する'
