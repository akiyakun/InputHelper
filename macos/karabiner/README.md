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

## Windows Appで英数／かなを切り替え

`remote-ime.json` の `Windows App: Cmd tap and Eisu/Kana IME off/on (v1: PowerToys Ctrl+Shift+9/0)` を追加すると、左Cmd単押しと英数キーでIMEをオフ、右Cmd単押しとかなキーでIMEをオンにします。Cmd+C/Vなどの組み合わせはCtrlとして送ります。ほかの修飾キーを押した状態のCmdは `remote-windows-keybind.json` が変換するため、両方のルールを有効にしてください。

Windows側はSynergy用と同じ設定を利用します。

- PowerToys Keyboard Managerの「ショートカットの再マップ」で、Ctrl+Shift+9 → IME Non-Convert、Ctrl+Shift+0 → IME Convertを設定（すべてのアプリ）。
- Microsoft IMEのキー割り当てで、無変換 → IME-オフ、変換 → IME-オンを設定。

`remote-ime.json` を `~/.config/karabiner/assets/complex_modifications/` にコピーし、Add predefined ruleから上記のWindows Appルールを追加します。配置順はSynergy → Windows AppのIME切替 → Windows AppのCmd→Ctrl → その他のCmd単押しIMEルールとしてください。

Windows Appが前面のときだけ適用し、SynergyでWindowsを操作中は適用しません。接続一覧画面でもキーは変換されます。

RDP接続先で、左右Cmd単押しと英数／かなキーによる切替、同じキーを連打した場合のIME状態維持、Cmd+C/V、Shiftを先に押したCmdとの組み合わせを確認してください。

## Windows App使用中にCmd+SpaceでAlfredを開く

`remote-windows-keybind.json` は、Windows Appが前面でも左右Cmd+SpaceでMac側のAlfred 5の検索欄を開きます。AppleScriptの `search` コマンドで直接呼び出します。

Cmd→Ctrl変換時に左右Cmdの押下状態を変数へ記録し、キーを離したら解除します。`remote-ime.json` のWindows Appルールにも同じ記録処理が必要なので、両ファイルの登録済みルールを更新してください。IME切替 → Cmd→Ctrlの順序は維持します。

物理Ctrl+Space、Cmd+Shift+Spaceはこの起動処理の対象外です。Synergy操作中も適用しません。Alfredが開いたらCmdを離して入力してください。

動作確認: RDP中の左右Cmd+Spaceによる検索欄の表示、Cmd単押しのIME切替、Cmd+C/V、物理Ctrl+SpaceのWindows側への送信を確認します。初回にmacOSからAlfredの操作許可を求められた場合は許可してください。

## ClaudeとChatGPTでEnterを改行にする

`enter-newline.json` はClaude（`com.anthropic.claudefordesktop`）とChatGPT（`com.openai.codex`）が前面のとき、EnterをShift+Enter（改行）に、Ctrl+EnterをEnter（送信）に変換します。SynergyでWindowsを操作中は適用しません。

### Google日本語入力のキー設定

IMEの変換中もEnterはShift+Enterとして届くため、Google日本語入力のキー設定にShift+Enterの確定がないと、変換中のEnterで確定できません。入力候補が出ていないときやスペースで変換した後だけ確定できず、Ctrl+Enterが必要になります。

Google日本語入力の環境設定 → 一般 → キー設定の選択「編集...」で、次のエントリを追加してください。

| モード | 入力キー | コマンド |
| --- | --- | --- |
| 変換前入力中 | Shift Enter | 確定 |
| 変換中 | Shift Enter | 確定 |
| サジェスト表示中 | Shift Enter | 確定 |

動作確認: Claudeでひらがなを入力した直後、スペースで変換した後のそれぞれでEnterを押して確定できること、確定後のEnterで改行、Ctrl+Enterで送信されることを確認します。
