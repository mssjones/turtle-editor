"""A small turtle editor: type code on the left, see the drawing on the right.

Run it with:  python3 turtle_editor.py     (Windows: py turtle_editor.py)
It only needs Python with tkinter. Your code is ordinary turtle code, so a
program written here also runs on its own, and the other way around.

Keys: F5 runs the code, Ctrl+O opens a file, Ctrl+S saves it (Cmd on a Mac).
"""

import contextlib
import tkinter as tk
import traceback
import turtle
from tkinter import filedialog, ttk

FILENAME = "<editor>"
FILETYPES = [("Python files", "*.py"), ("All files", "*.*")]
CANVAS_WIDTH = 2000
CANVAS_HEIGHT = 1600
STARTER_CODE = """\
import turtle

t = turtle.Turtle()

for side in range(4):
    t.forward(100)
    t.left(90)

turtle.done()
"""


def do_nothing(*args, **kwargs):
    """Stands in for the screen calls that would fight with the editor."""


class TurtleEditor:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.closing = False
        root.title("Turtle Editor")
        root.geometry("1200x720")
        root.protocol("WM_DELETE_WINDOW", self.close)

        panes = ttk.PanedWindow(root, orient="horizontal")
        panes.pack(fill="both", expand=True)
        left = ttk.Frame(panes)
        right = ttk.Frame(panes)
        panes.add(left, weight=1)
        panes.add(right, weight=2)
        self.build_editor(left)
        self.build_screen(right)
        self.bind_keys()
        self.update_position()

    def build_editor(self, parent):
        buttons = ttk.Frame(parent)
        buttons.pack(fill="x")
        self.run_button = ttk.Button(buttons, text="Run (F5)", command=self.run)
        self.stop_button = ttk.Button(
            buttons, text="Stop", command=self.stop, state="disabled"
        )
        self.clear_button = ttk.Button(buttons, text="Clear", command=self.clear)
        self.open_button = ttk.Button(buttons, text="Open", command=self.open_file)
        self.save_button = ttk.Button(buttons, text="Save", command=self.save_file)
        for button in (
            self.run_button,
            self.stop_button,
            self.clear_button,
            self.open_button,
            self.save_button,
        ):
            button.pack(side="left", padx=2, pady=4)
        self.position = ttk.Label(buttons)
        self.position.pack(side="right", padx=6)

        code_frame = ttk.Frame(parent)
        code_frame.pack(fill="both", expand=True)
        self.code = tk.Text(
            code_frame, font=("Courier", 12), undo=True, wrap="none", width=40
        )
        scroll = ttk.Scrollbar(code_frame, command=self.code.yview)
        self.code["yscrollcommand"] = scroll.set
        scroll.pack(side="right", fill="y")
        self.code.pack(side="left", fill="both", expand=True)
        self.code.tag_configure("error", background="#ffd6d6")
        self.code.insert("1.0", STARTER_CODE)
        self.code.edit_reset()

        self.output = tk.Text(
            parent, font=("Courier", 10), height=7, state="disabled", wrap="word"
        )
        self.output.pack(fill="x")
        self.output.tag_configure("error", foreground="#b00000")

    def build_screen(self, parent):
        # The turtle module normally opens its own window. Like turtledemo, we
        # hand it our window and canvas before it gets the chance.
        turtle._Screen._root = self.root
        self.canvas = turtle.ScrolledCanvas(
            parent, 800, 600, CANVAS_WIDTH, CANVAS_HEIGHT
        )
        turtle._Screen._canvas = self.canvas
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.center_canvas)
        self.screen = turtle.Screen()
        turtle.TurtleScreen.__init__(self.screen, self.canvas)
        turtle.RawTurtle.screens = [self.screen]

        # A program may end with turtle.done() or set the window size. Here the
        # editor owns the window, so those calls must do nothing.
        for name in ("mainloop", "done", "exitonclick", "bye", "setup"):
            setattr(self.screen, name, do_nothing)

    def center_canvas(self, event=None):
        """Keep (0, 0) in the middle of the visible part of the canvas."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.canvas.xview_moveto(0.5 * (CANVAS_WIDTH - width) / CANVAS_WIDTH)
        self.canvas.yview_moveto(0.5 * (CANVAS_HEIGHT - height) / CANVAS_HEIGHT)

    def bind_keys(self):
        self.root.bind("<F5>", lambda event: self.run())
        for modifier in ("Control", "Command"):
            try:
                self.root.bind(f"<{modifier}-o>", self.open_shortcut)
                self.root.bind(f"<{modifier}-s>", self.save_shortcut)
            except tk.TclError:  # Command only exists on a Mac
                pass
        self.code.bind("<Tab>", self.insert_tab)
        self.code.bind("<Return>", self.insert_newline)
        self.code.bind("<KeyRelease>", self.update_position)
        self.code.bind("<ButtonRelease>", self.update_position)

    def open_shortcut(self, event):
        self.open_file()
        return "break"

    def save_shortcut(self, event):
        self.save_file()
        return "break"

    def insert_tab(self, event):
        self.code.insert("insert", "    ")
        return "break"

    def insert_newline(self, event):
        """Start the new line at the right indent, as Python expects."""
        line = self.code.get("insert linestart", "insert")
        indent = line[: len(line) - len(line.lstrip())]
        if line.rstrip().endswith(":"):
            indent += "    "
        self.code.insert("insert", "\n" + indent)
        self.code.see("insert")
        self.update_position()
        return "break"

    def update_position(self, event=None):
        line = self.code.index("insert").split(".")[0]
        self.position["text"] = f"Line {line}"

    def write(self, text, tag=None):
        self.output["state"] = "normal"
        self.output.insert("end", text, tag or ())
        self.output.see("end")
        self.output["state"] = "disabled"
        self.output.update_idletasks()

    def flush(self):
        """print(..., flush=True) expects this; write() already shows the text."""

    def clear_output(self):
        self.output["state"] = "normal"
        self.output.delete("1.0", "end")
        self.output["state"] = "disabled"

    def clear(self):
        if self.running:
            return
        self.screen.clear()
        self.screen.mode("standard")
        self.clear_output()
        self.code.tag_remove("error", "1.0", "end")

    def set_running(self, running):
        self.running = running
        idle = "disabled" if running else "normal"
        for button in (
            self.run_button,
            self.clear_button,
            self.open_button,
            self.save_button,
        ):
            button["state"] = idle
        self.stop_button["state"] = "normal" if running else "disabled"

    def run(self):
        if self.running:
            return
        self.clear()
        self.set_running(True)
        turtle.TurtleScreen._RUNNING = True
        source = self.code.get("1.0", "end-1c")
        try:
            with contextlib.redirect_stdout(self), contextlib.redirect_stderr(self):
                exec(
                    compile(source, FILENAME, "exec"),
                    {"__name__": "__main__"},
                )
        except turtle.Terminator:
            if not self.closing:
                self.write("Stopped.\n")
        except SystemExit:
            pass
        except Exception as error:
            # A TclError while closing only means the drawing was interrupted.
            if not self.closing:
                self.show_error(error)
        finally:
            turtle.TurtleScreen._RUNNING = True
            if self.closing:
                self.root.destroy()
            else:
                self.set_running(False)

    def show_error(self, error):
        """Show the error in terms of your own code, without the turtle internals."""
        exception = traceback.TracebackException.from_exception(error)
        exception.stack = traceback.StackSummary.from_list(
            [frame for frame in exception.stack if frame.filename == FILENAME]
        )
        self.write("".join(exception.format()), "error")
        lines = [frame.lineno for frame in exception.stack]
        line = getattr(exception, "lineno", None) or (lines[-1] if lines else None)
        if line:
            self.code.tag_add("error", f"{line}.0", f"{line}.0 lineend+1c")
            self.code.see(f"{line}.0")

    def stop(self):
        turtle.TurtleScreen._RUNNING = False

    def close(self):
        if self.running:
            self.closing = True
            self.stop()
        else:
            self.root.destroy()

    def open_file(self):
        if self.running:
            return
        name = filedialog.askopenfilename(filetypes=FILETYPES)
        if name:
            with open(name, encoding="utf-8") as file:
                text = file.read()
            self.code.delete("1.0", "end")
            self.code.insert("1.0", text)
            self.root.title(f"Turtle Editor - {name}")

    def save_file(self):
        name = filedialog.asksaveasfilename(
            defaultextension=".py", filetypes=FILETYPES
        )
        if name:
            with open(name, "w", encoding="utf-8") as file:
                file.write(self.code.get("1.0", "end-1c"))
            self.root.title(f"Turtle Editor - {name}")


def main():
    root = tk.Tk()
    TurtleEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
