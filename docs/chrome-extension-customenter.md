# Chrome拡張 CustomEnter

ブラウザ版のチャットサービスで、Enterで誤送信しないようにするChrome拡張です。ソースは `chrome-extensions/` にあります。

| サイト | スクリプト | 動作 |
| --- | --- | --- |
| ChatGPT（`https://chatgpt.com/*`） | `chatgpt.js` | Enterで改行、Ctrl+Enterで送信 |
| Slack（`https://app.slack.com/*`） | `slack.js` | Ctrl+Enterで送信（Enterはサイト側の設定に従う） |
| Discord（`https://discord.com/*`） | `discord.js` | Enterによる送信を止める（Shift+Enterの改行はそのまま） |

デスクトップ版のClaude・Codexは[Karabinerの設定](karabiner-enter-newline.md)で対応します。

## インストール

1. Chromeで `chrome://extensions` を開き、右上の「デベロッパー モード」をONにします。
2. 「パッケージ化されていない拡張機能を読み込む」から `chrome-extensions` フォルダを選択します。
3. スクリプトを変更した場合は、拡張機能の更新ボタンを押してから対象サイトを再読み込みしてください。

## 各サイトの動作

### ChatGPT

- 入力欄（`#prompt-textarea` またはcomposer内のcontenteditable）でのEnterを横取りし、Shift+Enterとして入力欄へ送り直して改行します。エディタが処理しなかった場合は直接改行を挿入します。
- Ctrl+Enterで送信ボタンをクリックします。回答生成中の停止ボタンは押しません。送信ボタンが無効なときは何もしません。
- IMEの変換確定Enterはそのまま確定に使われ、送信されません。
- Shift・Alt・Cmd（Meta）を押したEnterは変更しません。
- ページの読み込み時、コンソールに `[CustomEnter] ChatGPT handler loaded (1.3.1)` と表示されます。

### Slack

- メッセージ入力欄（`data-qa="texty_input"`）でCtrl+Enterを押すと、送信ボタンをクリックします。
- Enterの動作は変更しないため、Enterで改行したい場合はSlackの環境設定で「Enterで改行」を選んでください。

### Discord

- メッセージ入力欄で修飾キーなしのEnterを押したとき、Discordの送信処理へイベントを渡しません。
- Shift+Enterの改行は変更しません。

## 動作確認

各サイトで、日本語の変換確定Enterで送信されないこと、Enterで改行されること（Discordでは送信されないこと）、Ctrl+Enterで送信されること（ChatGPT・Slack）を確認します。サイトのDOM変更で動かなくなることがあるため、その場合はセレクタを見直してください。
