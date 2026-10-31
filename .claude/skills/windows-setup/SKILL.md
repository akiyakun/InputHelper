---
name: windows-setup
description: 新しいWindows PCにInputHelperのWindows側設定（AutoHotkey、Google日本語入力、PowerToys Keyboard Manager、Chrome拡張など）を導入する。「新しいPCのセットアップ」「Windowsの設定を入れて」「InputHelperをインストール」などと頼まれたときに使う。
---

# InputHelper Windowsセットアップ

新しいWindows PCで、このリポジトリのWindows側設定を導入し、ユーザーが手で行う作業を案内する。やり取りは日本語で行う。

## 1. 現状確認

1. `README.md` と `docs/windows-setup.md` を読み、ドキュメントの更新で手順が変わっていないか確認する。手順が変わっていれば、そちらを優先し、`windows/setup/setup-windows.ps1` とこのスキルも合わせて直す。
2. 次を確認してユーザーに一覧で伝える。
   - `winget list --id <ID> -e` で `AutoHotkey.AutoHotkey`、`Google.JapaneseIME`、`Microsoft.PowerToys`、Chrome の有無
   - スタートアップフォルダ（`[Environment]::GetFolderPath('Startup')`）の `enter-newline.lnk`
   - PowerToys Keyboard Managerの再マップ（下記「確認コマンド」）
3. Synergyを使うかどうか分からない場合は、ユーザーに聞く（Windows App（RDP）だけなら不要）。

## 2. 自動セットアップ

リポジトリのルートで実行する。Synergyも入れる場合は `-Synergy` を付ける。

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\setup\setup-windows.ps1
```

- インストール時にUACの確認が出る。**実行前に「UACのダイアログが出たら『はい』を押してください」とユーザーに伝える。** 確認待ちのままだとwingetが終わらないので、長時間止まったら `Get-Process consent` でUAC待ちかを確認してユーザーに声をかける。
- 時間がかかるので、バックグラウンド実行にする。
- 途中で失敗したら、原因を直してもう一度実行してよい（済んだ手順は飛ばす作りになっている）。

## 3. 結果の確認

```powershell
# AutoHotkeyスクリプトが動いているか
Get-CimInstance Win32_Process -Filter "Name like 'AutoHotkey%'" | Select-Object CommandLine
# PowerToysの自動起動タスクとKeyboard Managerエンジン
Get-ScheduledTask -TaskPath '\PowerToys\' | Select-Object TaskName, State
Get-Process PowerToys.KeyboardManagerEngine
# 既定の入力方式（Google日本語入力のTIPになっているか）
Get-WinDefaultInputMethodOverride
```

### 確認コマンド（Keyboard Manager）

PowerShell 5.1では引数中の `"` が落ちるため、DSCはBashから呼ぶ。

```bash
"$LOCALAPPDATA/PowerToys/PowerToys.DSC.exe" get --module KeyboardManager --resource profile --input '{}'
```

`shortcuts` に `Ctrl+Shift+9` → `VK29`（無変換）と `Ctrl+Shift+0` → `VK28`（変換）があれば設定済み（`+` は `\u002B` とエスケープされて表示される）。ほかの再マップがあると `test` は一致しないと判定するため、`test` ではなく `get` で確認する。PowerToysがマシン単位でインストールされている場合は `$PROGRAMFILES/PowerToys/` にある。

## 4. ユーザーに手作業を案内

GUIでしかできない作業は、`docs/windows-setup.md` の「手作業」をもとに、番号付きで具体的に案内する。終わったら教えてもらい、動作確認まで付き合う。

## 注意

- PowerToysの `PowerToys.DSC.exe set --module App --resource settings` に一部の項目だけを渡すと、渡さなかった各モジュールの有効/無効が既定値に戻ってしまう。必ず `get` した設定全体を変更して渡す（スクリプトはそうしている）。
- 動作中のPowerToysは `settings.json` の変更を読み直さず、インストール直後の初回起動では書き戻すこともある。自動起動タスクとKeyboard Managerのエンジンは、PowerToysの起動時に設定どおり反映される。そのため、`set` はPowerToysを止めてから行い、そのあと起動し直す（スクリプトはそうしている）。
- PowerShellからDSCに `--input` でJSONを渡すときは、スクリプトの `ConvertTo-NativeArg` のように、`"` の直前と末尾のバックスラッシュも二重にして引用する。`"` を `\"` に置き換えるだけでは、`\"` を含むJSONが壊れる。
- DSCの `KeyboardManager profile` の `set` はプロファイル全体を置き換え、指定しなかった再マップを消す。スクリプトは `get` した内容に2件をマージしてから `set` している。手で `set` するときも同じようにする。
- PowerToysのGUIで作った再マップは `LCtrl+LShift+9` のように左右付きで保存される。スクリプトは左右を外して比べ、同じショートカットなら置き換える（`Ctrl+Shift+9` と重複させない）。
- DSCのKeyboard Managerはキー名 `IME Non-Convert` / `IME Convert` を受け付けないため、仮想キーコード `0x1D` / `0x1C` で指定する。
- `setup-windows.ps1` はBOM付きUTF-8で保存する。BOMがないとWindows PowerShell 5.1が日本語をShift-JISとして読み、構文エラーになる。
- Google日本語入力のキー設定は設定DBに保存されていて、外から安全に書き換えられないため、インポートはユーザーに頼む。
- リポジトリに変更をコミットするときは、`CLAUDE.md` のプライバシーのルールに従い、ユーザー名を含むパスなどを入れない。
