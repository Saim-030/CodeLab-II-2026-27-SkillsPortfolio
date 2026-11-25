import random                      # used to pick random jokes and random colours/positions
import tkinter as tk               # the library that builds the window and buttons
from pathlib import Path           # an easy way to work with file paths
from tkinter import messagebox     # used to show a pop-up error message

# SETTINGS - change these to customise the app
# BASE_DIR is the folder where this Python file is saved
BASE_DIR = Path(__file__).resolve().parent

# Each line in this file should look like:  Question? Answer
JOKES_FILE = Path(
    r"C:/Users/dell/OneDrive/Documents/Code lab 2 Assessment/exercise 2/randomJokes.txt"
)

# ICON
# This picture is shown in the top-left corner of the window
ICON_FILE = Path(
    r"C:/Users/dell/OneDrive/Documents/Code lab 2 Assessment/exercise 2/Logo 2.ico"
)

# COLORS
PAGE_BG = "#FFF0F3"      # light pink window background
HEADER_BG = "#E63946"    # red header at the top
CARD_BG = "#FFFFFF"      # white card that holds the joke
# The card border picks one of these colours for each new joke
ACCENTS = ("#FFB3C1", "#FF8FA3", "#E63946", "#C77DFF", "#FFD166", "#4CC9F0")
# Colours used for the falling confetti pieces
CONFETTI_COLORS = ("#E63946", "#FF8FA3", "#9B3FB5", "#FFD166", "#06D6A0", "#4CC9F0")


class JokeAssistantApp:
    # The whole app lives inside this class so all functions can share the same data
    def __init__(self, root: tk.Tk) -> None:
        # "root" is the main window created in main() at the bottom
        self.root = root
        self.root.title("Alexa - Joke Teller")

        # Set the window size and background colour
        # The height is 780 at most, but smaller if the screen is short
        height = min(780, root.winfo_screenheight() - 90)
        root.geometry(f"700x{height}")   # width 700, height as calculated above
        root.minsize(600, 600)           # the window cannot be made smaller than this
        root.configure(bg=PAGE_BG)

        # Variables that keep track of the app's data
        self.jokes: list[tuple[str, str]] = []                   # all jokes as (setup, punchline)
        self.current_joke: tuple[str, str] | None = None         # the joke on screen right now
        self.jokes_told = 0                                      # how many jokes were told
        self.haha_count = 0                                      # how many Haha clicks
        self.groan_count = 0                                     # how many Groan clicks
        self.accent = ACCENTS[0]                                 # current card border colour

        # Storage for button colours, timers, confetti pieces and header stripes
        self.button_colors: dict[tk.Button, tuple[str, str]] = {}  # normal and hover colour per button
        self.jobs: dict[str, str] = {}                              # running timers, saved by name
        self.confetti: list[list] = []                              # confetti pieces being animated
        self.stripes: list[tk.Frame] = []                           # coloured stripes under the header

        # Start the app: icon, jokes, screen, keys, first state
        # The order matters: jokes must be loaded before the screen is built
        self.set_icon()
        self.load_jokes()
        self.build_ui()
        self.bind_keys()
        self.set_initial_state()

    # Setup: icon, jokes file
    def set_icon(self) -> None:
        # Skip if the icon file does not exist (the app still works without it)
        if not ICON_FILE.exists():
            return
        try:
            # .ico files use iconbitmap, other images (png) use iconphoto
            if ICON_FILE.suffix.lower() == ".ico":
                self.root.iconbitmap(str(ICON_FILE))
            else:
                # Keep the image in self so Python does not delete it from memory
                self.icon_image = tk.PhotoImage(file=str(ICON_FILE))
                self.root.iconphoto(True, self.icon_image)
        except tk.TclError:
            # If the icon cannot be loaded, just ignore it
            pass

    def load_jokes(self) -> None:
        # Show an error pop-up if the jokes file is missing
        if not JOKES_FILE.exists():
            messagebox.showerror("File Not Found", f"Could not find jokes file at:\n{JOKES_FILE}")
            return

        # Read the file line by line
        for line in JOKES_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()          # remove spaces at the start and end
            if not line:
                continue                 # skip empty lines

            # Split each line at the first "?" into setup and punchline
            if "?" in line:
                setup, punchline = line.split("?", 1)
                # Put the "?" back on the setup and clean the spaces
                setup, punchline = setup.strip() + "?", punchline.strip()
                # Only save the joke if it really has a question and an answer
                if setup != "?" and punchline:
                    self.jokes.append((setup, punchline))
            else:
                # No "?" in the line, so treat the whole line as the setup
                self.jokes.append((line, "No punchline found for this joke."))

    # Small helpers
    def schedule(self, name: str, ms: int, func, *args) -> None:
        # Run a function after some milliseconds (replaces any timer with the same name)
        self.cancel(name)                                   # stop the old timer first
        self.jobs[name] = self.root.after(ms, func, *args)  # start a new one and remember it

    def cancel(self, name: str) -> None:
        # Stop a timer if it is running
        job = self.jobs.pop(name, None)     # remove it from the saved timers
        if job is not None:
            self.root.after_cancel(job)     # tell Tkinter to stop it

    def make_button(self, parent, text, fg, bg, hover, command, font=("Arial", 12, "bold"), padx=16, pady=9):
        # Create a flat coloured button
        # fg = text colour, bg = normal colour, hover = colour when the mouse is over it
        button = tk.Button(
            parent, text=text, font=font, fg=fg, bg=bg,
            activebackground=hover, activeforeground=fg,
            relief="flat", bd=0, padx=padx, pady=pady,
            cursor="hand2", takefocus=0, command=command,
        )
        # Remember the colours so set_enabled() can restore them later
        self.button_colors[button] = (bg, hover)

        def is_on() -> bool:
            # True when the button is enabled
            return str(button["state"]) != "disabled"

        # Hover and click effects (only when the button is enabled)
        button.bind("<Enter>", lambda _e: is_on() and button.config(bg=hover))                  # mouse enters
        button.bind("<Leave>", lambda _e: is_on() and button.config(bg=bg, relief="flat"))      # mouse leaves
        button.bind("<ButtonPress-1>", lambda _e: is_on() and button.config(relief="sunken"))   # mouse pressed
        button.bind("<ButtonRelease-1>", lambda _e: is_on() and button.config(relief="flat"))   # mouse released
        return button

    def set_enabled(self, button: tk.Button, enabled: bool) -> None:
        # Turn a button on (normal colours) or off (greyed out)
        if enabled:
            button.config(state="normal", bg=self.button_colors[button][0], relief="flat", cursor="hand2")
        else:
            button.config(state="disabled", bg="#F3D9E0", disabledforeground="#6B4A55",
                          relief="flat", cursor="arrow")

    def is_disabled(self, button: tk.Button) -> bool:
        # Check if a button is currently disabled
        return str(button["state"]) == "disabled"

    # Building the window
    def build_ui(self) -> None:
        # Widgets packed with side="bottom" are created first so they stay at the bottom.
        # The order below is: bottom items (from the very bottom up), then top items.

        # Bottom: keyboard shortcut hints
        tk.Label(
            self.root,
            text="SPACE  new joke    P  punchline    H  haha    G  groan    C  copy    ESC  quit",
            font=("Arial", 10), fg="#8A5A66", bg=PAGE_BG,
        ).pack(side="bottom", pady=(0, 6))

        # Row with Haha button, score and Groan button
        reaction_row = tk.Frame(self.root, bg=PAGE_BG)
        reaction_row.pack(side="bottom", pady=(0, 8))

        # Green Haha button (column 0)
        self.haha_button = self.make_button(
            reaction_row, "Haha!", "#0B3D1E", "#80ED99", "#B5F5C4", lambda: self.react("haha"))
        self.haha_button.grid(row=0, column=0, padx=5)

        # Score text between the two buttons (column 1)
        self.stats_label = tk.Label(
            reaction_row, text="Haha 0    Groan 0",
            font=("Arial", 13, "bold"), fg="#7A0F2A", bg=PAGE_BG, padx=10)
        self.stats_label.grid(row=0, column=1, padx=5)

        # Blue Groan button (column 2)
        self.groan_button = self.make_button(
            reaction_row, "Groan", "#032B3A", "#4CC9F0", "#8FDDF7", lambda: self.react("groan"))
        self.groan_button.grid(row=0, column=2, padx=5)

        # Row with Show Punchline, Next Joke, Copy and Quit buttons
        action_row = tk.Frame(self.root, bg=PAGE_BG)
        action_row.pack(side="bottom", pady=(0, 8))

        # Purple button: reveals the answer right away
        self.punchline_button = self.make_button(
            action_row, "Show Punchline", "#FFFFFF", "#9B3FB5", "#7E2F96", self.show_punchline)
        self.punchline_button.grid(row=0, column=0, padx=5)

        # Orange button: tells another joke
        self.next_button = self.make_button(
            action_row, "Next Joke", "#3D1F00", "#FF9F1C", "#FFBF69", self.tell_joke)
        self.next_button.grid(row=0, column=1, padx=5)

        # Teal button: copies the joke to the clipboard
        self.copy_button = self.make_button(
            action_row, "Copy", "#022B27", "#2EC4B6", "#6FE3D8", self.copy_joke)
        self.copy_button.grid(row=0, column=2, padx=5)

        # Grey-purple button: closes the app
        self.quit_button = self.make_button(
            action_row, "Quit", "#FFFFFF", "#6D597A", "#56455F", self.root.destroy)
        self.quit_button.grid(row=0, column=3, padx=5)

        # Big main button that tells a joke
        self.alexa_button = self.make_button(
            self.root, "Alexa tell me a Joke", "#FFFFFF", "#E63946", "#C9303C",
            self.tell_joke, font=("Arial", 15, "bold"), padx=36, pady=12)
        self.alexa_button.pack(side="bottom", pady=(2, 6))

        # Canvas where the confetti is drawn
        self.confetti_canvas = tk.Canvas(self.root, height=40, bg=PAGE_BG, highlightthickness=0)
        self.confetti_canvas.pack(side="bottom", fill="x", padx=28)

        # Top: red header with the title and mascot label
        header = tk.Frame(self.root, bg=HEADER_BG)
        header.pack(side="top", fill="x")

        # The title and the mascot label sit side by side in this row
        title_row = tk.Frame(header, bg=HEADER_BG)
        title_row.pack(pady=(8, 0))
        tk.Label(title_row, text="ALEXA", font=("Arial", 24, "bold"),
                 fg="#FFFFFF", bg=HEADER_BG).pack(side="left")

        # Small label that changes with the mood (READY, THINKING, HA HA...)
        self.mascot_label = tk.Label(
            title_row, text="READY", font=("Arial", 12, "bold"),
            fg="#E63946", bg="#FFFFFF", padx=12, pady=4)
        self.mascot_label.pack(side="left", padx=(14, 0))

        # Subtitle under the title
        tk.Label(header, text="YOUR PERSONAL JOKE ASSISTANT", font=("Arial", 11, "bold"),
                 fg="#FFFFFF", bg=HEADER_BG).pack(pady=(0, 8))

        # Coloured strip under the header (it rotates its colours)
        strip = tk.Frame(self.root, bg=PAGE_BG, height=5)
        strip.pack(side="top", fill="x")
        for color in ("#E63946", "#FF8FA3", "#9B3FB5", "#FFD166"):
            # Each colour gets its own piece, all sharing the width equally
            piece = tk.Frame(strip, bg=color, height=5)
            piece.pack(side="left", fill="x", expand=True)
            self.stripes.append(piece)   # saved so rotate_stripes() can change them

        # Welcome texts
        tk.Label(self.root, text="Ready for a good laugh?", font=("Arial", 16, "bold"),
                 fg="#333333", bg=PAGE_BG).pack(side="top", pady=(8, 0))
        tk.Label(self.root, text="Click below and let Alexa make your day!", font=("Arial", 11),
                 fg="#6B6B6B", bg=PAGE_BG).pack(side="top", pady=(0, 4))

        # Counter showing how many jokes were told
        self.counter_label = tk.Label(
            self.root, text="JOKES TOLD: 0", font=("Arial", 12, "bold"),
            fg="#C9184A", bg="#FFB3C1", padx=22, pady=4)
        self.counter_label.pack(side="top", pady=(0, 6))

        # White card that holds the joke setup and punchline
        # expand=True lets the card use all the free space left in the window
        self.card = tk.Frame(
            self.root, bg=CARD_BG, padx=22, pady=6,
            highlightbackground=ACCENTS[0], highlightthickness=3)   # highlight = the coloured border
        self.card.pack(side="top", fill="both", expand=True, padx=28, pady=(0, 2))

        # Small heading above the question
        tk.Label(self.card, text="JOKE SETUP", font=("Arial", 12, "bold"),
                 fg="#E63946", bg=CARD_BG).pack(pady=(2, 0))

        # Label that shows the joke question
        # wraplength makes long text continue on the next line instead of going off screen
        self.welcome_text = "Press 'Alexa tell me a Joke' to begin!"
        self.setup_label = tk.Label(
            self.card, text=self.welcome_text, font=("Arial", 16, "bold"),
            fg="#2B2B2B", bg=CARD_BG, wraplength=520, justify="center")
        self.setup_label.pack(fill="x", pady=(4, 4), expand=True)

        # Thin line between setup and punchline
        tk.Frame(self.card, bg="#FFB3C1", height=2).pack(fill="x", padx=18, pady=(0, 6))

        # Small heading above the answer
        tk.Label(self.card, text="PUNCHLINE", font=("Arial", 12, "bold"),
                 fg="#9B3FB5", bg=CARD_BG).pack()

        # Label that shows the joke answer
        self.punchline_label = tk.Label(
            self.card, text="The punchline is waiting...", font=("Arial", 16, "bold"),
            fg="#9B3FB5", bg=CARD_BG, wraplength=520, justify="center")
        self.punchline_label.pack(fill="x", pady=(4, 2), expand=True)

    def bind_keys(self) -> None:
        # Keyboard shortcuts and the action each key runs
        shortcuts = {
            "<space>": self.tell_joke,                 # Space = new joke
            "n": self.tell_joke,                       # N = new joke
            "p": self.show_punchline,                  # P = show punchline
            "h": lambda: self.react("haha"),           # H = haha
            "g": lambda: self.react("groan"),          # G = groan
            "c": self.copy_joke,                       # C = copy joke
            "<Escape>": self.root.destroy,             # Esc = quit
        }
        # Bind each key (and its capital letter too)
        # "a=action" saves the right action for each key inside the loop
        for key, action in shortcuts.items():
            self.root.bind(key, lambda _e, a=action: a())
            if len(key) == 1:
                self.root.bind(key.upper(), lambda _e, a=action: a())

        # Run on_resize every time the window size changes
        self.root.bind("<Configure>", self.on_resize)

    def on_resize(self, event: tk.Event) -> None:
        # Keep the text wrapping nicely when the window size changes
        # (the check makes sure only the main window triggers this, not inner widgets)
        if event.widget is self.root:
            wrap = max(260, event.width - 140)   # never narrower than 260 pixels
            self.setup_label.config(wraplength=wrap)
            self.punchline_label.config(wraplength=wrap)

    def set_initial_state(self) -> None:
        # Only the main Alexa button works at the start (and only if jokes loaded)
        has_jokes = bool(self.jokes)
        self.set_enabled(self.alexa_button, has_jokes)
        # Everything else is greyed out until a joke is told
        for button in (self.punchline_button, self.next_button, self.copy_button,
                       self.haha_button, self.groan_button):
            self.set_enabled(button, False)

        if has_jokes:
            # Type out the welcome message
            self.typewrite(self.setup_label, self.welcome_text, delay=14)
        else:
            # Tell the person something is wrong with the jokes file
            self.setup_label.config(
                text="No valid jokes loaded. Check your randomJokes.txt file.", fg="#C9184A")

        # Start the moving stripe animation
        self.rotate_stripes()

    # Animations
    def typewrite(self, label: tk.Label, text: str, delay: int, index: int = 0) -> None:
        # Show text one letter at a time
        # index = how many letters are shown so far, delay = milliseconds between letters
        if index == 0:
            self.cancel(str(label))          # stop any older typing on the same label
        label.config(text=text[:index])      # show only the first "index" letters
        if index < len(text):
            # Call this function again for the next letter
            self.schedule(str(label), delay, self.typewrite, label, text, delay, index + 1)

    def pulse_card(self, colors: list[str], step: int = 0) -> None:
        # Flash the card border through a list of colours
        self.card.config(highlightbackground=colors[step])
        if step + 1 < len(colors):
            self.schedule("pulse", 70, self.pulse_card, colors, step + 1)

    def bump_counter(self) -> None:
        # Briefly highlight the joke counter
        self.counter_label.config(bg="#E63946", fg="#FFFFFF")
        # After 180 ms, return to the normal pink colours
        self.schedule("bump", 180, lambda: self.counter_label.config(bg="#FFB3C1", fg="#C9184A"))

    def rotate_stripes(self) -> None:
        # Move the stripe colours one step so the strip looks animated
        colors = [stripe["bg"] for stripe in self.stripes]   # read the current colours
        colors = colors[-1:] + colors[:-1]                   # move the last colour to the front
        for stripe, color in zip(self.stripes, colors):
            stripe.config(bg=color)
        # Repeat every 700 ms, forever
        self.schedule("stripes", 700, self.rotate_stripes)

    def drumroll(self, punchline: str, step: int = 0) -> None:
        # Show "drumroll..." for a few steps before the answer
        if step < 6:
            dots = "." * (step % 3 + 1)      # cycles through ".", "..", "..."
            self.punchline_label.config(text=f"drumroll{dots}", fg="#B08A94")
            self.schedule("drum", 260, self.drumroll, punchline, step + 1)
            return

        # Reveal punchline after drumroll
        self.punchline_label.config(fg="#9B3FB5")
        self.typewrite(self.punchline_label, punchline, delay=22)   # type the answer letter by letter
        self.pulse_card(["#9B3FB5", "#E63946", "#9B3FB5", "#E63946", self.accent])
        self.mascot_label.config(text="HA HA")
        self.burst_confetti()

        # Now the person can react to the joke
        self.set_enabled(self.haha_button, True)
        self.set_enabled(self.groan_button, True)

    def clear_confetti(self) -> None:
        # Remove all confetti from the canvas
        self.cancel("confetti")                  # stop the confetti animation
        self.confetti_canvas.delete("all")       # erase everything drawn on the canvas
        self.confetti = []                       # forget the old pieces

    def burst_confetti(self) -> None:
        # Create 40 small coloured pieces in the middle of the canvas
        self.clear_confetti()
        width = max(self.confetti_canvas.winfo_width(), 200)   # canvas width (at least 200)
        for _ in range(40):
            # Start each piece near the centre with a small random offset
            x = width / 2 + random.randint(-50, 50)
            item = self.confetti_canvas.create_rectangle(
                x, 32, x + 7, 39, fill=random.choice(CONFETTI_COLORS), outline="")
            # Each piece stores: drawing id, sideways speed, upward speed
            self.confetti.append([item, random.uniform(-7, 7), random.uniform(-7, -3)])
        self.animate_confetti()

    def animate_confetti(self, frame: int = 0) -> None:
        # Move every piece, add gravity, and remove pieces that are done
        alive = []   # pieces that are still moving
        for piece in self.confetti:
            item, vx, vy = piece
            self.confetti_canvas.move(item, vx, vy)   # move sideways and up/down
            piece[2] = vy + 0.35                      # gravity: pulls the piece down more each frame
            coords = self.confetti_canvas.coords(item)
            # Keep the piece only while it is still on the canvas and the animation is short enough
            if coords and coords[1] < 50 and frame < 70:
                alive.append(piece)
            else:
                self.confetti_canvas.delete(item)
        self.confetti = alive
        if alive:
            # Run again in 30 ms for the next frame
            self.schedule("confetti", 30, self.animate_confetti, frame + 1)

    # Joke actions
    def tell_joke(self) -> None:
        # Do nothing if there are no jokes or the main button is disabled
        if not self.jokes or (self.current_joke is None and self.is_disabled(self.alexa_button)):
            return

        # Pick a random joke (different from the last one if possible)
        choices = [j for j in self.jokes if j != self.current_joke] or self.jokes
        self.current_joke = random.choice(choices)
        setup, _ = self.current_joke      # "_" means we ignore the punchline here

        # Update the joke counter
        self.jokes_told += 1
        self.counter_label.config(text=f"JOKES TOLD: {self.jokes_told}")
        self.bump_counter()

        # Stop old animations and timers from the previous joke
        self.cancel("drum")                          # old drumroll
        self.cancel("auto_punch")                    # old automatic punchline timer
        self.cancel(str(self.punchline_label))       # old punchline typing
        self.clear_confetti()

        # Show the new joke setup with a random card colour
        self.accent = random.choice(ACCENTS)
        self.pulse_card(["#E63946", self.accent])
        self.setup_label.config(fg="#2B2B2B")
        self.typewrite(self.setup_label, setup, delay=14)
        # Reset the punchline area until the answer is revealed
        self.punchline_label.config(text="The punchline is waiting...", fg="#9B3FB5")
        self.mascot_label.config(text="THINKING")

        # Enable and disable the right buttons
        self.set_enabled(self.punchline_button, True)
        self.set_enabled(self.next_button, True)
        self.set_enabled(self.copy_button, True)
        self.set_enabled(self.haha_button, False)
        self.set_enabled(self.groan_button, False)

        # Automatically show the punchline once the setup has finished typing
        # Wait time = typing time (14 ms per letter) + a short pause of 800 ms
        wait_ms = len(setup) * 14 + 800
        self.schedule("auto_punch", wait_ms, self.show_punchline)

    def show_punchline(self) -> None:
        """Show the punchline with a drumroll."""
        # Do nothing if there is no joke or the punchline is already showing
        if self.current_joke is None or self.is_disabled(self.punchline_button):
            return

        # Stop the automatic timer in case the button/key was pressed first
        self.cancel("auto_punch")
        self.cancel("drum")

        # Disable the button so the drumroll cannot be started twice
        self.set_enabled(self.punchline_button, False)
        self.mascot_label.config(text="DRUMROLL")

        # Start the drumroll, then the answer appears
        punchline = self.current_joke[1]    # index 1 is the punchline, index 0 is the setup
        self.drumroll(punchline)

    def react(self, kind: str) -> None:
        # Pick which button was pressed and ignore it if it is disabled
        button = self.haha_button if kind == "haha" else self.groan_button
        if self.current_joke is None or self.is_disabled(button):
            return

        # Count the reaction and play a matching effect
        if kind == "haha":
            self.haha_count += 1
            self.mascot_label.config(text="LOVED IT")
            self.pulse_card(["#06D6A0", "#FFD166", "#06D6A0", self.accent])
            self.burst_confetti()
        else:
            self.groan_count += 1
            self.mascot_label.config(text="COOL")
            self.pulse_card(["#4CC9F0", "#C77DFF", "#4CC9F0", self.accent])

        # Update the score and allow only one reaction per joke
        self.stats_label.config(text=f"Haha {self.haha_count}    Groan {self.groan_count}")
        self.set_enabled(self.haha_button, False)
        self.set_enabled(self.groan_button, False)

    def copy_joke(self) -> None:
        # Do nothing if there is no joke to copy
        if self.current_joke is None or self.is_disabled(self.copy_button):
            return

        # Put the full joke (setup + punchline) on the clipboard
        setup, punchline = self.current_joke
        self.root.clipboard_clear()                              # remove the old clipboard text
        self.root.clipboard_append(f"{setup} {punchline}")       # add the new joke text

        # Show "Copied!" for a moment, then go back to "Copy"
        self.copy_button.config(text="Copied!")
        self.schedule("copy", 1200, lambda: self.copy_button.config(text="Copy"))


def main() -> None:
    # Create the window and start the app
    root = tk.Tk()
    JokeAssistantApp(root)
    root.mainloop()      # keeps the window open and listening for clicks and keys


# This runs main() only when the file is started directly (not when imported)
if __name__ == "__main__":
    main()