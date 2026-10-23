# ClaudeとCodexでEnterを改行にする

`macos/karabiner/enter-newline.json` はClaude（`com.anthropic.claudefordesktop`）とCodex（`com.openai.codex`）のデスクトップアプリが前面のとき、EnterをShift+Enter（改行）に、Ctrl+EnterをEnter（送信）に変換します。SynergyでWindowsを操作中（`customenter_synergy_windows = 1`）は適用しません。

ブラウザ版のChatGPT・Slack・Discordは[Chrome拡張](chrome-extension-customenter.md)で対応します。Windows AppやSynergyで操作するWindows上のClaudeは、Windows側の[AutoHotkey](windows-enter-newline.md)で対応します。

## 手動反映

1. `macos/karabiner/enter-newline.json` を `~/.config/karabiner/assets/complex_modifications/` にコピーします。
2. KarabinerのComplex Modifications → Add predefined ruleから、Codex用・Claude用のルールをそれぞれ追加します。

ファイルをコピーするだけでは登録済みの設定は変更されません。旧版のルールを登録済みの場合は、無効化または削除してから追加してください。以前の `CustomEnter: ChatGPT - ...` はCodex用ルールの旧名で、動作は同じです。

## Google日本語入力のキー設定

IMEの変換中もEnterはShift+Enterとして届くため、Google日本語入力のキー設定にShift+Enterの確定がないと、変換中のEnterで確定できません。入力候補が出ていないときやスペースで変換した後だけ確定できず、Ctrl+Enterが必要になります。

Google日本語入力の環境設定 → 一般 → キー設定の選択「編集...」で、次のエントリを追加してください。

| モード | 入力キー | コマンド |
| --- | --- | --- |
| 変換前入力中 | Shift Enter | 確定 |
| 変換中 | Shift Enter | 確定 |
| サジェスト表示中 | Shift Enter | 確定 |

## 動作確認

Claudeでひらがなを入力した直後、スペースで変換した後のそれぞれでEnterを押して確定できること、確定後のEnterで改行、Ctrl+Enterで送信されることを確認します。
