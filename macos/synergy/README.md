# SynergyとKarabinerのIME連携

以下のコマンドは、リポジトリのルートディレクトリ（`InputHelper`）で実行してください。

## 登録・起動

1. `macos/karabiner/remote-ime.json` を `~/.config/karabiner/assets/complex_modifications/` にコピー。
2. Karabinerの「Add predefined rule」からSynergyルールを追加し、一番上へ移動。
3. MacのCapsLockをOFFにして、次を実行。

```sh
python3 "./macos/synergy/bridge_karabiner.py"
```

起動後にMacからWindowsへ移動すると専用ルールがONになります。
v7はv6と同じくPowerToysを利用し、左Cmd単押しでIME OFF、右Cmd単押しでIME ONを行います。
旧Synergyルールと検証用ルールを無効にし、v7を追加してください。ファイルの上書きだけでは追加済みルールは更新されません。
Windows単体およびMacからの実キーCommand+Shift操作で変換動作をユーザーが確認済み。v6のSynergy経由の左右Cmd単押しは2026-09-25にユーザーが成功確認済みです。最終チェック各項目の個別結果は未確認です。
Cmdを他のキーと組み合わせる操作は維持します。
手動起動はCtrl+Cで終了すると専用ルールがOFFになります。自動起動中は手動で重複起動しないでください。

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

起動時に `~/Library/Logs/Synergy/synergy.jsonl` があれば優先し、なければ旧 `synergy.log` を選びます。
JSONLの `msg` を読み出し、旧テキスト形式と同じ画面移動判定を行います。`--log` で監視ファイルを明示することもできます。
Synergyの更新でログファイル名・形式が変わった場合は、監視スクリプトの再起動が必要です（実行中の監視先は固定）。
ログをkqueueで監視し、Karabiner変数 `customenter_synergy_windows` を変更します。
画面移動、対象PCの切断、Macへの復帰、core停止、ログの消失・入れ替え・縮小で状態を更新します。
起動時は過去のログから現在位置を推測せずOFFで開始します。
ログ入れ替え後などにOFFのままなら、Macへ戻ってから再度Windowsへ移動してください。

Ctrl+C、SIGTERM、SIGHUPでは終了時にOFFへ戻します。
強制終了（SIGKILL）やKarabiner通信障害では解除が保証できないため、必要なら次を実行します。

```sh
python3 "./macos/synergy/bridge_karabiner.py" --reset
```

`--reset` は監視スクリプトを終了してから実行してください。
KarabinerでSynergyルールを無効にしても通常操作へ戻せます。

設定JSONの検証、ログの疑似イベントによるON/OFF、KarabinerへのOFF送信は確認済み。
Synergy経由の左右Cmd単押しでのIME切り替えはユーザー確認済みです。上記の最終チェックは引き続き必要です。


## 自動起動（macOS LaunchAgent）

2026-09-25にこのMacへ登録。Synergy本体の既存 `com.symless.synergy3` は稼働を確認済みです。
IME連携は `local.inputhelper.synergy-ime` として、ユーザーのGUIログイン時に起動します。
登録先は `~/Library/LaunchAgents/local.inputhelper.synergy-ime.plist` です。
ログイン直後にKarabinerやSynergyログの準備が間に合わない場合も、終了後にlaunchdが再起動します（最短15秒間隔）。
起動時はOFFなので、Macへ戻ってからWindowsへ移動してください。
スリープ中は処理が止まり、復帰後は監視を続行します。実機でのスリープ復帰・再ログイン確認は別途必要です。

監視ログは `~/Library/Logs/InputHelper/synergy-ime.log`。1 MiBごとにローテーションし、過去3本を保持します。
Synergy本体のログ保存設定は変更しません。

```sh
# 状態と直近ログ
launchctl print "gui/$(id -u)/local.inputhelper.synergy-ime"
tail -n 30 "$HOME/Library/Logs/InputHelper/synergy-ime.log"

# 停止（正常終了でIME連携をOFF。次回ログイン時には再開）
launchctl bootout "gui/$(id -u)/local.inputhelper.synergy-ime"

# 停止後に再開
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/local.inputhelper.synergy-ime.plist"

# 自動起動を削除する場合は、停止後に登録ファイルを削除
rm "$HOME/Library/LaunchAgents/local.inputhelper.synergy-ime.plist"
```

`KeepAlive` により、プロセスだけを終了すると自動再起動します。手動で `--reset` する前には `bootout` してください。
Karabiner設定JSONや有効ルールは自動起動の登録では変更しません。

### 移設・再登録

`launch_agent.py` は実行中のPythonとリポジトリの絶対パスを使ってplistを生成します。
このMacでは `/usr/bin/python3` から生成し、実体の `/Library/Developer/CommandLineTools/usr/bin/python3` を登録しています。
生成されるplistには、そのPCで必要な絶対パスが自動設定されます。生成済みplistはリポジトリへ追加せず、各PCで生成してください。
pyenvのシェル設定には依存しません。Pythonやリポジトリを移動する際は、停止後に再生成・再登録してください。
生成内容を確認するだけなら、以下の最初のコマンドのみ実行します。

```sh
/usr/bin/python3 "./macos/synergy/launch_agent.py" > /tmp/local.inputhelper.synergy-ime.plist
plutil -lint /tmp/local.inputhelper.synergy-ime.plist
mkdir -p "$HOME/Library/LaunchAgents"
cp /tmp/local.inputhelper.synergy-ime.plist "$HOME/Library/LaunchAgents/"
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/local.inputhelper.synergy-ime.plist"
```


## Macの前面アプリとSynergyの競合対策（v7）

SynergyでWindowsへ移動しても、Macの前面アプリはChromeリモートデスクトップ等のまま残ります。
アプリ別ルールには `customenter_synergy_windows != 1` の条件を追加し、Windows操作中は適用しません。
Macへ戻り変数が0になると、元のアプリ別操作が再び有効になります。

- `macos/karabiner/remote-ime.json` のSynergyルール: v7。単押しの送信内容は成功済みv6と同じ。追加の修飾キーを押した状態のCmdは、そのまま通して下位のMac用IMEルールへの適用を防ぎます。
- `macos/karabiner/remote-ime.json` のChromeリモートデスクトップルール: v3。Synergy操作中の除外条件を追加。Chromeリモートデスクトップ自体で使うCaps Lock方式は維持します。
- `macos/karabiner/enter-newline.json` のChatGPT／Claudeルール: v2。Synergy操作中はEnterとCtrl+Enterのアプリ別変換を適用しません。

### 手動反映

上記2ファイル（`remote-ime.json` と `enter-newline.json`）を `~/.config/karabiner/assets/complex_modifications/` にコピーします。
KarabinerのComplex Modificationsで旧版の該当ルールを無効化または削除し、Add predefined ruleから新しい版を追加してください。
Synergy v7は一番上へ配置します。ファイルの上書きだけでは登録済みルールは変わりません。
各JSONにはアプリ別のルールが2つずつ含まれます。必要なルールをそれぞれ追加してください。
以前の個別JSONをコピー済みの場合は、インポート候補の重複を避けるため、コピー先の旧ファイルも削除してください。旧ファイルの削除だけでは登録済みルールは削除されません。
監視スクリプトの再起動や、Windows側のPowerToysの設定変更は不要です。

### 実機確認と切り分け

1. MacでChromeリモートデスクトップを前面にし、左右CmdのIME操作を確認。
2. 前面アプリを変えずにSynergyでWindowsへ移動し、左右Cmd単押し、Cmd+C/V、Shiftを先に押したCmdとの組み合わせを確認。
3. Macへ戻り、Chromeリモートデスクトップ用のIME操作が復帰することを確認。
4. ChatGPT／ClaudeをMacの前面にした場合も、Synergy側のEnter・Ctrl+Enterがそのまま届くことを確認。

単押しのSynergyルールは以前から最上位でした。そのため、修飾キーなしの単押しでも失敗する場合は、ルール競合だけでは説明できません。
Karabiner-EventViewerのVariablesで、Windowsへ移動したときに `customenter_synergy_windows` が1、Macへ戻ると0になるか確認します。
変数が切り替わらなければ `~/Library/Logs/InputHelper/synergy-ime.log` の画面移動・エラーとSynergyの接続状態を確認してください。
この修正の条件・送信内容は静的に検証していますが、ChromeリモートデスクトップとSynergyを併用する実機確認は別途必要です。

条件判定はKarabiner公式の[ルール優先順位](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-evaluation-priority/)と[修飾キー条件](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/from/modifiers/)に基づきます。
