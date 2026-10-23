#Requires AutoHotkey v2.0
#SingleInstance Force

; Claudeデスクトップアプリが前面のとき、EnterをShift+Enter（改行）、Ctrl+EnterをEnter（送信）に変換する。
; Windows App（RDP）やSynergyでMacから操作する場合も、Windows側で変換する。
GroupAdd "CustomEnter", "ahk_exe Claude.exe"

#HotIf WinActive("ahk_group CustomEnter")
Enter::Send "+{Enter}"
NumpadEnter::Send "+{Enter}"
^Enter::Send "{Enter}"
^NumpadEnter::Send "{Enter}"
#HotIf
