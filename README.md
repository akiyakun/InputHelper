# InputHelper

MacとWindowsをまたいだキー入力（IME切替・Enterの改行／送信）を調整する設定とスクリプト集です。

## 新しいWindows PCのセットアップ（AI利用）

このリポジトリをcloneしてClaude Codeで開き、次のように頼むだけでセットアップできます。

```text
新しいWindows PCなので、InputHelperのセットアップをお願いします
```

スキル `.claude/skills/windows-setup` により、アプリのインストール（AutoHotkey・Google日本語入力・PowerToys）と設定を自動で行い、残りの手作業（Google日本語入力のキー設定のインポート、Chrome拡張の読み込みなど）を案内します。インストール中にUACの確認が出たら「はい」を押してください。

AIを使わない場合や詳しい内容は[新しいWindows PCのセットアップ](docs/windows-setup.md)を参照してください。

## ドキュメント

| ドキュメント | 内容 |
| --- | --- |
| [新しいWindows PCのセットアップ](docs/windows-setup.md) | Windows側の設定をまとめて導入する（スクリプト・AI利用） |
| [Windows App用のKarabiner設定](docs/karabiner-windows-app.md) | Windows AppでのCmd→Ctrl変換、IME切替、Alfred起動 |
| [ClaudeとCodexでEnterを改行にする](docs/karabiner-enter-newline.md) | デスクトップアプリのEnter変換とGoogle日本語入力の設定 |
| [Windows側のClaudeでEnterを改行にする](docs/windows-enter-newline.md) | Windows App・Synergy経由で操作するWindows版ClaudeのEnter変換（AutoHotkey） |
| [SynergyとKarabinerのIME連携](docs/synergy-ime.md) | Synergyでの画面移動を検知してIME切替ルールを切り替える |
| [Chrome拡張 CustomEnter](docs/chrome-extension-customenter.md) | ブラウザ版ChatGPT・Slack・DiscordのEnter動作 |
| [キー受信診断ページ](docs/keyboard-diagnostic.md) | Windows側で受信したキーを確認するツール |
