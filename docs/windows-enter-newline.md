# Windows側のClaudeでEnterを改行にする

MacからWindows App（RDP）やSynergyでWindowsを操作しているとき、Mac側のKarabinerは前面アプリがWindows Appであることしか分からないため、Windows上のClaudeに対するEnter変換はWindows側で行います。

`windows/autohotkey/enter-newline.ahk` はClaudeデスクトップアプリ（`Claude.exe`）が前面のとき、EnterをShift+Enter（改行）に、Ctrl+EnterをEnter（送信）に変換します。テンキーのEnterも同様です。

Mac側では物理Ctrl+Enterに加え、[Cmd→Ctrl変換](karabiner-windows-app.md#windows-appでcmdをctrlに変換)を有効にしていればCmd+Enterでも送信できます。

## 導入

1. [AutoHotkey v2](https://www.autohotkey.com/) をインストールします（`winget install AutoHotkey.AutoHotkey` でも可）。
2. `windows/autohotkey/enter-newline.ahk` をダブルクリックして起動します。タスクトレイにAutoHotkeyのアイコンが表示されます。
3. ログオン時に自動起動する場合は、`Win+R` → `shell:startup` で開いたフォルダに、`enter-newline.ahk` のショートカットを置きます。

スクリプトを編集した場合は、タスクトレイのアイコンを右クリック → Reload Scriptで反映します。

## IMEの変換中のEnter

IMEの変換中もEnterはShift+Enterとして送られます。Microsoft IMEはShift+Enterで確定せず、キー設定でも割り当てられないため、Google日本語入力を使います（`winget install Google.JapaneseIME`）。設定前でも、変換中のCtrl+EnterはEnterとしてIMEに届くため確定できます。

Google日本語入力のプロパティ → 一般 → キー設定の選択「編集...」を開き、左下の「編集」→「インポート」で `google-ime/keymap-windows.txt` を読み込みます。MS-IMEのキー設定をもとに、次のエントリを追加・置換したものです。RDP経由では変換・無変換キーを入力欄に取り込めないため、手で追加する代わりにインポートを使います。インポートすると現在のキー設定はすべて置き換わるため、独自に追加したエントリがある場合は先にエクスポートしておいてください。

インポート後、Win+Spaceで入力方式をGoogle日本語入力に切り替えます。常に使う場合は、設定 → 時刻と言語 → 言語と地域 → 日本語の言語のオプションで、Google日本語入力を既定にするか、Microsoft IMEを削除します。

| モード | 入力キー | コマンド |
| --- | --- | --- |
| 変換前入力中 | Shift Enter | 確定 |
| 変換中 | Shift Enter | 確定 |
| サジェスト表示中 | Shift Enter | 確定 |

サジェスト表示中のShift Enterは、既定の「最初の候補で確定」を削除しています。

[Windows AppのIME切替](karabiner-windows-app.md#windows-appで英数かなを切り替え)で使う変換・無変換キーも、Microsoft IMEのキー割り当ての代わりに次のように設定しています。IMEがオンのときに変換キーを押しても、再変換にならずオンのままになります。

| モード | 入力キー | コマンド |
| --- | --- | --- |
| 直接入力 | Henkan | IMEを有効化 |
| 入力文字なし | Henkan | IMEを有効化 |
| 入力文字なし | Muhenkan | IMEを無効化 |
| 変換前入力中 | Muhenkan | IMEを無効化 |
| 変換中 | Muhenkan | IMEを無効化 |

## 動作確認

Windows上のClaudeで次を確認します。

- 英字入力後のEnterで改行され、Ctrl+Enterで送信される。
- Google日本語入力でひらがなを入力した直後、スペースで変換した後のそれぞれでEnterを押して確定できる。確定後のEnterで改行される。
- Claude以外のアプリ（メモ帳など）ではEnterが通常どおり動く。
