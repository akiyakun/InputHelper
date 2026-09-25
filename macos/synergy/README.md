# SynergyとKarabinerのIME連携

## 登録・起動

1. `../karabiner/synergy-ime.json` を `~/.config/karabiner/assets/complex_modifications/` にコピー。
2. Karabinerの「Add predefined rule」からSynergyルールを追加し、一番上へ移動。
3. MacのCapsLockをOFFにして、次を実行。

```sh
python3 "/Users/akiya/local/GDrive/Data/Chrome/Extensions/CustomEnter/synergy/bridge_karabiner.py"
```

起動後にMacからWindowsへ移動すると専用ルールがONになります。
v6はPowerToysを利用し、左Cmd単押しでIME OFF、右Cmd単押しでIME ONを行います。
旧Synergyルールと検証用ルールを無効にし、v6を追加してください。ファイルの上書きだけでは追加済みルールは更新されません。
Windows単体およびMacからの実キーCommand+Shift操作で変換動作をユーザーが確認済み。v6のSynergy経由の左右Cmd単押しは2026-09-25にユーザーが成功確認済みです。最終チェック各項目の個別結果は未確認です。
Cmdを他のキーと組み合わせる操作は維持します。
Ctrl+Cで終了すると専用ルールはOFFになります。自動起動は登録していません。

## このMacの設定に合わせた内容

- 接続先名: `s500plus-27441e4d`（変更時は `--target 名前`）
- MacのSynergy設定でWindows向けに `super = ctrl`、`ctrl = super` と設定済み。
- 左Cmd単押しはMacの左Command+左Shift+9を送信し、Windowsで左Ctrl+左Shift+9として受信する想定。
- 右Cmd単押しは同じ修飾キーと0を送信する。
- WindowsのPowerToys Keyboard Manager「ショートカットの再マップ」で、Ctrl+Shift+9 → IME Non-Convert、Ctrl+Shift+0 → IME Convertを設定する。対象はすべてのアプリ。
- Microsoft IMEのキー割り当てで、無変換 → IME-オフ、変換 → IME-オンを設定する。
- Caps Lock送信と待ち時間は廃止。以前の検証でCaps LockがONなら、初回検証前にMacとWindowsそれぞれでOFFに戻す。
- Windows操作中の通常Enterはそのまま通し、Macで前面に残るChatGPT／ClaudeのEnter変換を回避する。
- 実機確認: 左右の単押しと連打によるIME状態維持、小文字入力、Caps Lockランプ不変、Cmd+C/V、変換確定Enter、Macに戻ったときの通常操作。

## 検知と終了

ログをkqueueで監視し、Karabiner変数 `customenter_synergy_windows` を変更します。
画面移動、対象PCの切断、Macへの復帰、core停止、ログの消失・入れ替え・縮小で状態を更新します。
起動時は過去のログから現在位置を推測せずOFFで開始します。
ログ入れ替え後などにOFFのままなら、Macへ戻ってから再度Windowsへ移動してください。

Ctrl+C、SIGTERM、SIGHUPでは終了時にOFFへ戻します。
強制終了（SIGKILL）やKarabiner通信障害では解除が保証できないため、必要なら次を実行します。

```sh
python3 "/Users/akiya/local/GDrive/Data/Chrome/Extensions/CustomEnter/synergy/bridge_karabiner.py" --reset
```

`--reset` は監視スクリプトを終了してから実行してください。
KarabinerでSynergyルールを無効にしても通常操作へ戻せます。

設定JSONの検証、ログの疑似イベントによるON/OFF、KarabinerへのOFF送信は確認済み。
Synergy経由の左右Cmd単押しでのIME切り替えはユーザー確認済みです。上記の最終チェックは引き続き必要です。
