# 新しいWindows PCのセットアップ

新しいWindows PCに、このリポジトリのWindows側設定をまとめて導入する手順です。自動でできる部分は `windows/setup/setup-windows.ps1` で行い、GUIでしかできない部分は手作業で行います。

## AIを使ったセットアップ（おすすめ）

1. GitとClaudeをインストールします。デスクトップアプリ（`Anthropic.Claude`）とCLI（`Anthropic.ClaudeCode`）のどちらか一方で構いません。インストール後、新しいPowerShellを開き、Claudeを起動してサインインします。

   ```powershell
   winget install --id Git.Git -e
   winget install --id Anthropic.Claude -e
   ```

   CLIを使う場合は、2行目の代わりに `winget install --id Anthropic.ClaudeCode -e` を実行します。

2. このリポジトリをcloneします。

   ```powershell
   git clone <このリポジトリのURL>
   ```

3. Claude Code（デスクトップアプリのCodeタブ、またはリポジトリのフォルダで `claude` コマンド）でリポジトリのフォルダを開き、次のように頼みます。

   ```text
   新しいWindows PCなので、InputHelperのセットアップをお願いします
   ```

   リポジトリ内のスキル `.claude/skills/windows-setup` が使われ、現状確認 → スクリプト実行 → 確認 → 手作業の案内の順に進みます。`/windows-setup` と入力して直接呼び出すこともできます。

4. インストール中にUAC（管理者権限）の確認が出たら「はい」を押します。
5. 最後に案内される[手作業](#手作業)を行い、[動作確認](#動作確認)をします。

## スクリプトで直接セットアップする

リポジトリのルートで実行します。Synergyも使う場合は `-Synergy` を付けます。何度実行しても問題ありません。

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\setup\setup-windows.ps1
```

スクリプトが行うこと:

| 内容 | 詳細 |
| --- | --- |
| アプリのインストール | wingetでAutoHotkey v2、Google日本語入力、PowerToys、Chrome（未導入の場合）、Synergy（`-Synergy` のとき） |
| AutoHotkey | `enter-newline.ahk` のショートカットをスタートアップに置いて起動（[詳細](windows-enter-newline.md)） |
| PowerToys Keyboard Manager | Ctrl+Shift+9 → IME Non-Convert、Ctrl+Shift+0 → IME Convert（[詳細](synergy-ime.md#1-windows側の設定)）。ほかの再マップは残す |
| PowerToys | ログオン時の自動起動とKeyboard ManagerをON（未設定ならPowerToysを再起動して反映）。ほかのモジュールの有効/無効は変更しない |
| 入力方式 | Google日本語入力を既定の入力方式にする |

## 手作業

1. **Google日本語入力のキー設定をインポート**: タスクバーのIMEアイコンを右クリック → プロパティ → 一般 → キー設定の選択「編集...」→ 左下の「編集」→「インポート」で `google-ime\keymap-windows.txt` を選び、OKで閉じます（[詳細](windows-enter-newline.md#imeの変換中のenter)）。
2. **Chrome拡張 CustomEnter**: Chromeで `chrome://extensions` を開き、デベロッパーモードをON → 「パッケージ化されていない拡張機能を読み込む」で `chrome-extensions` フォルダを選びます（[詳細](chrome-extension-customenter.md)）。
3. **Slack**: 環境設定 → 詳細設定で「Enterで改行」を選びます（Ctrl+Enterで送信）。
4. **Synergy**（使う場合）: Synergyを起動してMacに接続します。Mac側の設定は[SynergyとKarabinerのIME連携](synergy-ime.md)を参照してください。
5. **Microsoft IMEを削除**（任意）: Win+Spaceで誤ってMicrosoft IMEに切り替わるのを防ぐ場合は、設定 → 時刻と言語 → 言語と地域 → 日本語の「…」→ 言語のオプション → キーボードからMicrosoft IMEを削除します。

## 動作確認

- Windows上のClaudeで、Enterで改行、Ctrl+Enterで送信される。日本語の変換中のEnterで確定できる。
- 変換キーでIMEオン、無変換キーでIMEオフになる。MacのWindows App・Synergyからは左右Cmd単押しで切り替わる。
- ブラウザ版ChatGPTでEnterで改行、Ctrl+Enterで送信される。

キーがうまく届かないときは[キー受信診断ページ](keyboard-diagnostic.md)で確認します。
