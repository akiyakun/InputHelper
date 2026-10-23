# SynergyとKarabinerのIME連携

SynergyでMacからWindowsへカーソルを移動している間だけ、Macの左右Cmd単押しでWindowsのIMEをオフ／オンにします。

Synergyのログを監視スクリプトが読み、Windowsへ移動したらKarabinerの変数 `customenter_synergy_windows` を1に、Macへ戻ったら0にします。Karabinerのルールはこの変数を見て、Windows操作中だけSynergy用の変換を行い、Mac用のアプリ別ルールを止めます。

以下のコマンドは、リポジトリのルートディレクトリ（`InputHelper`）で実行してください。

## 構成

| ファイル | 役割 |
| --- | --- |
| `macos/synergy/bridge_karabiner.py` | 監視スクリプト本体。Karabinerの変数を切り替える |
| `macos/synergy/watch_screens.py` | Synergyログの監視と画面移動の判定 |
| `macos/synergy/launch_agent.py` | 自動起動用のLaunchAgent plistを生成する |
| `macos/synergy/test_log_formats.py` | ログ形式の回帰テスト |
| `macos/karabiner/remote-ime.json` | Synergy用ルール（v7）、Chromeリモートデスクトップ用ルール（v3）、[Windows App用ルール](karabiner-windows-app.md) |
| `macos/karabiner/enter-newline.json` | [Codex／ClaudeのEnter変換](karabiner-enter-newline.md)（v2）。Synergy操作中は適用しない |

## キーの動作

Windows操作中（`customenter_synergy_windows = 1`）は次のように動きます。

| Macで押すキー | Macから送るキー | Windowsで受け取るキー | 結果 |
| --- | --- | --- | --- |
| 左Cmd単押し | 左Command+左Shift+9 | 左Ctrl+左Shift+9 | IMEオフ |
| 右Cmd単押し | 左Command+左Shift+0 | 左Ctrl+左Shift+0 | IMEオン |
| Cmd+ほかのキー | そのまま | Ctrl+ほかのキー | 通常のショートカット |
| Enter | そのまま | Enter | 変換確定・改行 |

- 追加の修飾キーを押した状態のCmdはそのまま通し、下位のMac用IMEルールが反応しないようにします。
- Windowsへ移動しても、Macの前面アプリ（Chromeリモートデスクトップ、Codex、Claudeなど）はそのまま残ります。アプリ別ルールには `customenter_synergy_windows != 1` の条件を付けているため、Windows操作中は適用されません。Macへ戻ると元の動作に戻ります。

## セットアップ

### 1. Windows側の設定

1. PowerToys Keyboard Managerの「ショートカットの再マップ」で、次を設定します。対象はすべてのアプリです。
   - Ctrl+Shift+9 → IME Non-Convert
   - Ctrl+Shift+0 → IME Convert
2. Microsoft IMEのキー割り当てで、無変換 → IME-オフ、変換 → IME-オンを設定します。

### 2. Synergyの設定

MacのSynergy設定で、Windows向けに `super = ctrl`、`ctrl = super` を設定します。

SynergyでのWindows側の画面名を控えておきます。監視スクリプトと自動起動の設定で `--target` に指定します。以下の例では `WINDOWS-PC` としています。

### 3. Karabinerのルールを登録

1. `macos/karabiner/remote-ime.json` と `macos/karabiner/enter-newline.json` を `~/.config/karabiner/assets/complex_modifications/` にコピーします。
2. KarabinerのComplex Modifications → Add predefined ruleから、使うルールを追加します。`remote-ime.json` には3つ、`enter-newline.json` には2つのルールがあります。
3. `Synergy: Cmd tap IME off/on (v7: ...)` を一番上へ移動します。ほかのルールの並べ方は[Windows App用のKarabiner設定](karabiner-windows-app.md#ルールの配置順)を参照してください。

ファイルをコピーするだけでは、登録済みのルールは変わりません。旧版のルールを登録している場合は、無効化または削除してから新しい版を追加してください。

### 4. 監視スクリプトを手動で起動

MacのCaps LockがOFFであることを確認してから、次を実行します。

```sh
python3 "./macos/synergy/bridge_karabiner.py" --target WINDOWS-PC
```

起動直後はOFFです。一度MacからWindowsへ移動すると、Synergy用ルールがONになります。Ctrl+Cで終了すると、ルールはOFFに戻ります。

手動で使う場合はここまでで完了です。常に使う場合は、次の自動起動を設定してください。

### 5. 自動起動（macOS LaunchAgent）

`launch_agent.py` は、実行したPythonとリポジトリの絶対パス、`--target` で指定した画面名を使ってplistを生成します。生成したplistは各PC固有のため、リポジトリへ追加しないでください。pyenvのシェル設定には依存しません。

```sh
/usr/bin/python3 "./macos/synergy/launch_agent.py" --target WINDOWS-PC > /tmp/local.inputhelper.synergy-ime.plist
plutil -lint /tmp/local.inputhelper.synergy-ime.plist
mkdir -p "$HOME/Library/LaunchAgents"
cp /tmp/local.inputhelper.synergy-ime.plist "$HOME/Library/LaunchAgents/"
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/local.inputhelper.synergy-ime.plist"
```

生成内容を確認するだけなら、最初のコマンドだけ実行します。

登録すると、`local.inputhelper.synergy-ime` としてGUIログイン時に起動します。

- 登録先: `~/Library/LaunchAgents/local.inputhelper.synergy-ime.plist`
- 監視ログ: `~/Library/Logs/InputHelper/synergy-ime.log`（1 MiBごとにローテーションし、過去3本を保持）
- ログイン直後にKarabinerやSynergyログの準備が間に合わず終了しても、launchdが再起動します（最短15秒間隔）。
- `KeepAlive` のため、プロセスだけを終了しても自動で再起動します。
- スリープ中は処理が止まり、復帰後に監視を続けます。
- Synergy本体のログ設定、Karabinerの設定JSONや有効なルールは変更しません。

自動起動中に手動で起動すると、「連携スクリプトはすでに動作中です」と表示されて終了します。手動で使う場合は、先に自動起動を停止してください。

Pythonやリポジトリの場所を変えた場合は、自動起動を停止してから、上記の手順でplistを生成し直して再登録してください。

## 運用

### 自動起動の操作

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

### Synergy用ルールを強制的にOFFにする

Ctrl+C、SIGTERM、SIGHUPで終了したときは、自動でOFFに戻ります。強制終了（SIGKILL）やKarabinerとの通信障害では戻らないことがあるため、次を実行します。

```sh
python3 "./macos/synergy/bridge_karabiner.py" --reset
```

`--reset` は監視スクリプトを終了してから実行してください。自動起動中は、先に `launchctl bootout` で停止します。KarabinerでSynergy用ルールを無効にしても、通常の操作に戻せます。

## 監視の仕組み

- 起動時に `~/Library/Logs/Synergy/synergy.jsonl` があればそれを、なければ旧形式の `synergy.log` を監視します。`--log` で監視するファイルを指定することもできます。
- JSONLは `msg` を取り出し、旧形式と同じ方法で画面移動を判定します。
- ログはkqueueで監視します（定期ポーリングはしません）。
- 画面移動、接続先の切断、Macへの復帰、Synergy coreの停止、ログの消失・入れ替え・縮小を検知して変数を更新します。
- 起動時は過去のログから現在の画面を推測せず、OFFで始めます。
- 監視するファイルは起動時に決まります。Synergyの更新でログのファイル名や形式が変わったときは、監視スクリプトを再起動してください。

## 動作確認

1. MacでChromeリモートデスクトップを前面にし、左右CmdのIME操作を確認します。
2. 前面アプリを変えずにSynergyでWindowsへ移動し、次を確認します。
   - 左右Cmdの単押しでIMEがオフ／オンになる。同じキーの連打でも状態が変わらない
   - 小文字で入力される。Caps Lockのランプが変わらない
   - Cmd+C/V、Shiftを先に押したCmdとの組み合わせが動く
   - 変換確定のEnterが動く
3. Codex／ClaudeをMacの前面にした状態でも、Windows側にEnter・Ctrl+Enterがそのまま届くことを確認します。
4. Macへ戻り、Chromeリモートデスクトップ用のIME操作や通常の操作が戻ることを確認します。

## トラブルシューティング

- **Windowsへ移動してもIMEが切り替わらない**: Karabiner-EventViewerのVariablesで、Windowsへ移動したときに `customenter_synergy_windows` が1、Macへ戻ると0になるか確認します。
- **変数が切り替わらない**: `~/Library/Logs/InputHelper/synergy-ime.log` の画面移動・エラーと、Synergyの接続状態を確認します。ログの入れ替え後などはOFFのままのことがあるので、Macへ戻ってからもう一度Windowsへ移動してください。
- **変数は1なのに修飾キーなしの単押しでも失敗する**: Synergy用ルールは最上位なので、ルールの競合ではなく送信内容や受信側の問題が考えられます。Windows側で[キー受信診断ページ](keyboard-diagnostic.md)を開き、どのキーが届いているか確認します。
- **大文字になる・Caps Lockがおかしい**: 以前のCaps Lock方式で検証したときにONのまま残っていることがあります。MacとWindowsのそれぞれでCaps LockをOFFにしてください。

ルールの判定は、Karabiner公式の[ルール優先順位](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-evaluation-priority/)と[修飾キー条件](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/from/modifiers/)に基づきます。

## テスト

旧形式とJSONL形式のログについて、画面移動の判定とログファイルの選択を確認します。Karabinerへの書き込みは行いません。macOSで実行してください。

```sh
python3 "./macos/synergy/test_log_formats.py"
```

## 確認状況

### 確認済み

- Windows単体、およびMacの実キーでのCommand+Shift操作による変換動作（ユーザー確認）。
- v6でのSynergy経由の左右Cmd単押しによるIME切替（2026-09-25、ユーザー確認）。v7の単押しの送信内容はv6と同じです。
- 設定JSONの検証、ログの疑似イベントによるON/OFF、KarabinerへのOFF送信。
- 2026-09-25にこのMacへLaunchAgentを登録。Synergy本体の `com.symless.synergy3` の稼働も確認。Pythonは `/usr/bin/python3` から生成し、実体の `/Library/Developer/CommandLineTools/usr/bin/python3` を登録しています。

### 未確認

- [動作確認](#動作確認)の各項目の個別結果。
- ChromeリモートデスクトップとSynergyを併用したときの実機確認（v7の条件と送信内容は静的に検証済み）。
- 自動起動でのスリープ復帰・再ログイン時の動作。

### 変更履歴

- **Caps Lock方式の廃止**: 以前はCaps Lockの送信と待ち時間でIMEを切り替えていましたが、PowerToysのショートカット（v6以降）に変更しました。Chromeリモートデスクトップ用ルールは、引き続きCaps Lock方式を使います。
- **v7（Synergy）／v3（Chromeリモートデスクトップ）／v2（Codex・Claude）**: Windows操作中にMacの前面アプリのルールが反応しないよう、アプリ別ルールにSynergy操作中の除外条件を追加しました。この変更で、監視スクリプトの再起動やPowerToysの設定変更は不要です。
- **ルールファイルの統合**: `synergy-ime.json`、`chrome-remote-desktop-ime.json` は `remote-ime.json` に、`chatgpt-enter.json`、`claude-enter.json` は `enter-newline.json` にまとめました。旧ファイルを `~/.config/karabiner/assets/complex_modifications/` にコピーしている場合は、インポート候補の重複を避けるため削除してください。旧ファイルを削除しても、登録済みのルールは消えません。
- **JSONLログへの対応**: Synergyの `synergy.jsonl` を優先して監視するようにしました。
- **画面名の指定を必須に変更**: 以前は監視スクリプトに画面名の既定値がありましたが、端末固有の情報をリポジトリに含めないよう削除し、`--target` での指定を必須にしました。既定値を使っていた自動起動は起動に失敗するため、`--target` を付けて[plistを生成し直し](#5-自動起動macos-launchagent)、再登録してください。
- **Codex用ルールの改名**: `enter-newline.json` の `CustomEnter: ChatGPT - ...` は対象がCodexアプリ（`com.openai.codex`）のため、`CustomEnter: Codex - ...` に改名しました。動作は変わりません。
