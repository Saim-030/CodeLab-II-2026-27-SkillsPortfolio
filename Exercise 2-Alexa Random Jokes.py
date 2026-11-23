import tkinter as tk                  # GUI library
from tkinter import messagebox        # pop-up dialog boxes (errors, warnings, questions)
import random                         # used to pick a random joke
from pathlib import Path              # used to build file paths that work on any OS

# MAIN WINDOW
# Create the main application window and set its title, size and background
root = tk.Tk()
root.title("Alexa - Joke Teller")
root.geometry("850x700")              # width x height in pixels
root.resizable(False, False)          # stop the user from resizing the window
root.configure(bg="#FFF0F3")

# COLOURS
# All colours are stored here so they can be changed in one place
BG = "#FFF0F3"                        # light pink window background
RED = "#E63946"                       # main accent colour (header, buttons)
DARK_RED = "#B71C2C"                  # darker red for text and button highlights
WHITE = "#FFFFFF"
DARK = "#333333"                      # dark grey for main text
PINK = "#FFB3C1"                      # pink for borders and the counter
GREEN = "#2ECC71"                     # success messages
BLUE = "#3498DB"                      # info messages and Next Joke button
PURPLE = "#8E44AD"                    # punchline colour

# LOAD JOKES FROM TEXT FILE
def load_jokes():
    # Read randomJokes.txt and return a list of (setup, punchline) pairs.
    # Returns an empty list if the file cannot be found.

    # The file can be next to this script or inside a "resources" folder
    possible_paths = [
        Path(__file__).parent / "randomJokes.txt",
        Path(__file__).parent / "resources" / "randomJokes.txt"
    ]

    # Try each location in order and use the first one that exists
    for file_path in possible_paths:

        if file_path.exists():

            jokes = []

            # Open the file for reading using UTF-8 so special characters work
            with open(file_path, "r", encoding="utf-8") as file:

                # Go through the file one line at a time
                for line in file:

                    # Remove spaces and the newline at the start/end of the line
                    line = line.strip()

                    # Every joke line must contain a "?" that separates
                    # the setup from the punchline
                    if "?" in line:

                        # Split only at the first "?" so the punchline
                        # can safely contain more question marks
                        setup, punchline = line.split("?", 1)

                        # Tidy up the text (remove any leading "- " bullet)
                        setup = setup.lstrip("- ").strip()
                        punchline = punchline.strip()

                        # Only keep jokes where both parts are not empty
                        if setup and punchline:
                            jokes.append((setup, punchline))

            return jokes

    # If neither path worked, tell the user where to put the file
    messagebox.showerror(
        "File Not Found",
        "randomJokes.txt was not found!\n\n"
        "Place it beside your Python file or inside a resources folder."
    )

    return []


# Load all jokes once when the program starts
jokes = load_jokes()

# VARIABLES
# These variables keep track of the state of the program
current_joke = None                   # the (setup, punchline) currently shown
used_jokes = []                       # jokes already told in this cycle
joke_count = 0                        # total number of jokes told
punchline_visible = False             # True while the punchline is showing

# FUNCTIONS
def update_status(message, colour=GREEN):
    # Show a short message with a coloured dot in the status bar

    status_label.config(
        text="● " + message,
        fg=colour
    )


def reset_punchline():
    # Hide the punchline and put the punchline button back to normal

    # "global" lets this function change the variable defined outside it
    global punchline_visible

    punchline_visible = False

    # Show the placeholder text instead of the real punchline
    punchline_label.config(
        text=" The punchline is waiting...",
        fg=PURPLE
    )

    # Change the button back to "Show Punchline"
    punchline_button.config(
        text=" Show Punchline",
        bg=PURPLE
    )


def show_joke():
    # Pick a random joke that has not been used yet and show its setup

    global current_joke, used_jokes, joke_count

    # Stop if no jokes were loaded from the file
    if not jokes:
        messagebox.showwarning(
            "No Jokes",
            "Please add jokes to randomJokes.txt."
        )
        return

    # Reset after all jokes have been used
    if len(used_jokes) == len(jokes):
        used_jokes = []

    # Build a list of jokes that have not been told yet
    available = [
        joke for joke in jokes
        if joke not in used_jokes
    ]

    # Choose one at random and remember it so it is not repeated
    current_joke = random.choice(available)
    used_jokes.append(current_joke)

    joke_count += 1

    # Display the setup (first part) of the joke
    setup_label.config(
        text= + current_joke[0]
    )

    # Hide any punchline left over from the previous joke
    reset_punchline()

    # Update the counter at the top of the screen
    counter_label.config(
        text=f"JOKES TOLD: {joke_count}"
    )

    update_status("A new joke is ready!", GREEN)

    # Make sure the buttons can be clicked now that a joke is showing
    next_button.config(state="normal")
    punchline_button.config(state="normal")


def show_punchline():
    # Show or hide the punchline of the current joke

    global punchline_visible

    # No joke has been told yet, so there is nothing to reveal
    if current_joke is None:
        update_status("Please ask Alexa for a joke first!", RED)
        return

    if punchline_visible:
        # Hide punchline when clicked again
        reset_punchline()
        update_status("Punchline hidden!", BLUE)
        return

    # Display the punchline (second part) of the joke
    punchline_label.config(
        text= + current_joke[1],
        fg=DARK_RED
    )

    # Turn the button into a "Hide Punchline" button
    punchline_button.config(
        text=" Hide Punchline",
        bg=RED
    )

    punchline_visible = True

    update_status("Hope that made you laugh!", GREEN)


def next_joke():
    # Move on to another joke (works even if no joke has been shown yet)

    if current_joke is None:
        show_joke()
    else:
        show_joke()


def quit_app():
    # Ask for confirmation before closing the program

    answer = messagebox.askyesno(
        "Exit Alexa",
        "Are you sure you want to quit Alexa Joke Teller?"
    )

    # askyesno returns True if the user clicked "Yes"
    if answer:
        root.destroy()


def on_enter(event, button, colour):
    # Change a button's colour when the mouse moves over it

    button.config(bg=colour)


def on_leave(event, button, colour):
    # Change a button's colour when the mouse moves away from it

    button.config(bg=colour)

# HEADER
# Red banner at the top of the window
header = tk.Frame(root, bg=RED, height=155)
header.pack(fill="x")

# Stop the frame from shrinking to fit its contents so the height stays 155
header.pack_propagate(False)

# Big title text
tk.Label(
    header,
    text="ALEXA",
    font=("Arial", 32, "bold"),
    bg=RED,
    fg=WHITE
).pack(pady=(20, 5))

# Smaller subtitle under the title
tk.Label(
    header,
    text="YOUR PERSONAL JOKE ASSISTANT",
    font=("Arial", 12, "bold"),
    bg=RED,
    fg=WHITE
).pack()

# MAIN CONTENT
# Frame that holds everything between the header and the footer
main_frame = tk.Frame(root, bg=BG)
main_frame.pack(fill="both", expand=True, padx=35, pady=20)

# Welcome heading
tk.Label(
    main_frame,
    text="Ready for a good laugh?",
    font=("Arial", 22, "bold"),
    bg=BG,
    fg=DARK
).pack(pady=(5, 10))

# Short instruction under the heading
tk.Label(
    main_frame,
    text="Click below and let Alexa make your day!",
    font=("Arial", 12),
    bg=BG,
    fg="#666666"
).pack(pady=5)

# JOKE COUNTER
# Pink badge that shows how many jokes have been told
counter_label = tk.Label(
    main_frame,
    text="JOKES TOLD: 0",
    font=("Arial", 11, "bold"),
    bg=PINK,
    fg=DARK_RED,
    padx=20,
    pady=8
)

counter_label.pack(pady=15)

# JOKE DISPLAY BOX
# White box with a pink border that holds the setup and the punchline
joke_frame = tk.Frame(
    main_frame,
    bg=WHITE,
    highlightbackground=PINK,
    highlightthickness=2
)

joke_frame.pack(fill="x", pady=10)

# Heading above the joke setup
tk.Label(
    joke_frame,
    text="JOKE SETUP",
    font=("Arial", 13, "bold"),
    bg=WHITE,
    fg=RED
).pack(pady=(18, 10))

# Label that displays the joke setup (updated by show_joke)
setup_label = tk.Label(
    joke_frame,
    text="Press 'Alexa tell me a Joke' to begin!",
    font=("Arial", 15, "bold"),
    bg=WHITE,
    fg=DARK,
    wraplength=680,                   # wrap long text onto a new line at 680 pixels
    justify="center",
    height=3                          # reserve 3 lines so the layout does not jump
)

setup_label.pack(padx=20, pady=5)

# Thin pink divider line between the setup and the punchline
tk.Frame(
    joke_frame,
    bg=PINK,
    height=2
).pack(fill="x", padx=25, pady=10)

# Heading above the punchline
tk.Label(
    joke_frame,
    text="PUNCHLINE",
    font=("Arial", 13, "bold"),
    bg=WHITE,
    fg=PURPLE
).pack(pady=5)

# Label that displays the punchline (updated by show_punchline)
punchline_label = tk.Label(
    joke_frame,
    text="The punchline is waiting...",
    font=("Arial", 14, "bold"),
    bg=WHITE,
    fg=PURPLE,
    wraplength=680,
    justify="center",
    height=3
)

punchline_label.pack(padx=20, pady=(5, 15))

# BUTTON DESIGN
def create_button(parent, text, colour, command):
    # Build a flat, coloured button so all buttons share the same style

    button = tk.Button(
        parent,
        text=text,
        command=command,              # function to run when clicked
        font=("Arial", 12, "bold"),
        bg=colour,
        fg=WHITE,
        activebackground=DARK_RED,    # colour while the button is pressed
        activeforeground=WHITE,
        relief="flat",
        bd=0,
        cursor="hand2",               # hand cursor when hovering
        padx=18,
        pady=13
    )

    return button

# BUTTONS
# The four buttons are arranged in a 2 x 2 grid inside this frame
button_frame = tk.Frame(main_frame, bg=BG)
button_frame.pack(pady=15)

# Top left: tells a new joke
ask_button = create_button(
    button_frame,
    "Alexa tell me a Joke",
    RED,
    show_joke
)

ask_button.grid(row=0, column=0, padx=7, pady=8)

# Top right: shows or hides the punchline
punchline_button = create_button(
    button_frame,
    "Show Punchline",
    PURPLE,
    show_punchline
)

punchline_button.grid(row=0, column=1, padx=7, pady=8)

# Bottom left: moves on to the next joke
next_button = create_button(
    button_frame,
    "Next Joke",
    BLUE,
    next_joke
)

next_button.grid(row=1, column=0, padx=7, pady=8)

# Bottom right: closes the program
quit_button = create_button(
    button_frame,
    "Quit",
    DARK_RED,
    quit_app
)

quit_button.grid(row=1, column=1, padx=7, pady=8)

# STATUS BAR
# Line of text at the bottom that gives feedback to the user
status_label = tk.Label(
    main_frame,
    text="Alexa is ready!",
    font=("Arial", 11, "bold"),
    bg=BG,
    fg=GREEN
)

status_label.pack(pady=8)

# KEYBOARD SHORTCUTS
# Each key press calls the same function as the matching button
root.bind("<Return>", lambda event: show_joke())        # Enter = new joke
root.bind("<space>", lambda event: show_punchline())    # Space = show/hide punchline
root.bind("<Right>", lambda event: next_joke())         # Right arrow = next joke
root.bind("<Escape>", lambda event: quit_app())         # Escape = quit

# FOOTER
# Red bar at the very bottom of the window with the credit line
tk.Label(
    root,
    text="Made by Muhammad Saim using Python & Tkinter",
    font=("Arial", 10),
    bg=RED,
    fg=WHITE,
    pady=10
).pack(fill="x", side="bottom")

# START APPLICATION
# Start the event loop so the window stays open and reacts to clicks and keys
root.mainloop()