AceJump
=======

Plugin for Sublime Text 2

It's inspired by AceJump for JetBrains WebStorm (inspired by emacs AceJump, which is inspired by EasyMotion for Vim)

Possibilities
------------

With just one keyboard shortcut and two typed letters you can set your cursor to the begining or end of any word (or text chunk) on the screen. You can also select this word (like `ctrl+d`).

Description
---------------------------

After you type a keyboard shortcut (default is `ctrl+;`) an input field is opened. First character you type launches function which searches for all text chunks containing this character. Then it labels all found occurences. Next letter(s) you type are interpeted as label you want jump to. If you then press enter the cursor will be before your label. If you want to select target word just type plus sign (`+`) before hiting the enter. You can also jump to the end of the word by appending dollar sign (`$`).

Notice that current plugin status is indicated in status bar.

How to use it
-------------

Input: `<first_character_in_word><searching_word_label>[<modifier>]`

- Press keyboard shortcut to activate plugin.
- Type character to search for.
- Type letter corresponding to your word and press enter or
- Type modifier letter and then press enter

Modifiers:
- no modifier - place cursor at the begining of the word
- `$`, `.`    - pace cursor at the end of the word
- `+`, `,`    - select word

How to install
--------------

Just put AceJump folder to Packages directory of ST2
(Preferences > Browse Packages)

Thoughts
--------

I did it that way, because that's all I found about Sublime Text 2 API.
I used
- Window.show_input_panel to collect user input
- View.replace, View.add_regions and command undo to impement labels
- similiar mechanism to goto_line.py to jump

tl;dr
-----

Press `ctrl+;`, type first character, letter, `<enter>`, profit.
