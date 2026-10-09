# Karabiner設定

## Windows AppでCmdをCtrlに変換

`remote-windows-keybind.json` はWindows App（`com.microsoft.rdc.macos`）が前面のとき、左Cmdを左Ctrl、右Cmdを右Ctrlへ変換します。Cmd+C/V/A/ZやCmd+Shiftとの組み合わせにも適用されます。Windows Appの接続一覧画面にも適用されます。

SynergyでWindowsを操作中（`customenter_synergy_windows = 1`）は適用しません。

### 手動反映

1. `remote-windows-keybind.json` を `~/.config/karabiner/assets/complex_modifications/` にコピーします。
2. KarabinerのComplex Modifications → Add predefined ruleから `Windows App: Cmd to Ctrl (disabled while using Synergy)` を追加します。
3. 既存のCmd単押しIME切替ルールより上に配置します。Synergyのルールを使う場合は、その直下に配置してください。

ファイルをコピーするだけでは登録済みの設定は変更されません。

### 動作確認

Windows Appで接続し、Cmd+C/V、Cmd+A、Cmd+Shift+矢印がWindowsのCtrl操作として動くことを確認します。Macの別アプリへ切り替え、Cmdが通常どおり動くことも確認してください。
