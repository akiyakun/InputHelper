# キー受信診断ページ

`windows/utility/keyboard-diagnostic.html` は、Synergy経由でMacから送ったキーがWindows側でどう受信されているかを確認するためのページです。[SynergyとKarabinerのIME連携](synergy-ime.md)で、Cmd単押しのIME切替やEnterがうまく動かないときの切り分けに使います。[Windows App](karabiner-windows-app.md)で接続したときも、接続先で開けば同じように確認できます。

## 使い方

1. Windows側でHTMLファイルをブラウザで開きます。
2. 入力欄をクリックし、右Cmd単押し→左Cmd単押しを、各1秒以上空けて2回ずつ試します。
3. 日本語の変換確定Enterも試します。
4. 必要に応じて「ログを保存」で `synergy-key-events.txt` としてダウンロードします。「ログ消去」で表示をクリアします。

## 記録される内容

修飾キー（Ctrl・Alt・Shift・Meta）、CapsLock、Enter、半角／全角（Backquote）、変換・無変換・かななどのIME関連キーの `keydown` / `keyup` と、変換開始／終了（`compositionstart` / `compositionend`）、フォーカスの変化だけを記録します。

各行には時刻（UTC）、イベント種類、`key` / `code`、各修飾キーの押下状態、CapsLock状態、変換中かどうか、キーリピートかどうかを表示します。CapsLock列はブラウザが報告する状態です。ログは直近400行まで保持します。

## プライバシー

通信や設定変更は行いません。入力した文字はログに残さず、文字キーは `[文字キー]` と表示します。
