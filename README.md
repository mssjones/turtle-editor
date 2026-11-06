# Turtle Editor

A small editor for Python's `turtle` module: type code on the left, see the
drawing on the right. Change a line, run it again, and the new drawing appears
straight away.

It is one Python file with no dependencies beyond Python and `tkinter`.

## Run it

Download `turtle_editor.py` and run:

```bash
python3 turtle_editor.py
```

On Windows, use `py turtle_editor.py`.

The python.org installers for Windows and macOS include `tkinter`. On Debian,
Ubuntu or Raspberry Pi OS you may need to install it:

```bash
sudo apt install python3-tk
```

The editor opens a window, so it needs a computer with a screen. It does not
work in a plain SSH session.

## Use it

| Button | Key | What it does |
| ------ | --- | ------------ |
| Run | F5 | Clears the drawing and runs your code |
| Stop | | Ends a program that keeps drawing |
| Clear | | Wipes the drawing and the messages |
| Open | Ctrl+O (Cmd+O on a Mac) | Opens a `.py` file |
| Save | Ctrl+S (Cmd+S on a Mac) | Saves your code as a `.py` file |

Your code is ordinary turtle code, so a program written here also runs on its
own, and the other way around. Errors appear under your code, with the line
marked.

## Limits

- Stop only works while the turtle is drawing. A loop that never calls a turtle
  command freezes the editor, and you have to close it from your system.
- The editor runs your code as a normal Python program, with the same access to
  your files as any other script. Only run code you trust.

## Tested on

Linux with Python 3.11, and Windows. Other systems and versions have not been
tested.

## License

[MIT](LICENSE) © 2026 Mariëlle Ernst
