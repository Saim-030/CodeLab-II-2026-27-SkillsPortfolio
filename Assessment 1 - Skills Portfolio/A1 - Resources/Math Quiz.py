import random               # Used to generate random numbers, operations and confetti
import tkinter as tk        # Python's built-in GUI library
from pathlib import Path    # Used to build file paths in a safe, readable way

# SETTINGS - change these to customise the app
# BASE_DIR is the folder this script is saved in
BASE_DIR = Path(__file__).resolve().parent
# Location of the window icon (.ico file). 
ICON_FILE = BASE_DIR / "C:\\Users\\dell\\OneDrive\\Documents\\Vending-Machine\\CodeLab-II-2026-27-SkillsPortfolio\\Assessment 1 - Skills Portfolio\\A1 - Resources\\Logo 1.ico"

# Game settings
TOTAL_QUESTIONS = 10        # How many questions are asked in one quiz
FIRST_ATTEMPT_POINTS = 10   # Points for a correct answer on the first try
SECOND_ATTEMPT_POINTS = 5   # Points for a correct answer on the second try

# Colour theme (hex colour codes used throughout the interface)
BG = "#1e1b4b"       # Main window background
CARD = "#312e81"     # Background of the question card
TEXT = "#f8fafc"     # Main text colour
MUTED = "#a5b4fc"    # Softer text colour for less important text
DARK = "#0f172a"     # Dark colour used for text on bright buttons
GREY = "#4c4a7a"     # Neutral colour for borders and unused progress blocks
GREEN = "#22c55e"
YELLOW = "#facc15"
ORANGE = "#fb923c"
RED = "#fb7185"
CYAN = "#22d3ee"
PINK = "#ec4899"
PURPLE = "#a855f7"

# Difficulty level -> (name, min, max, colour, description)
# min and max set the range of the random numbers used in each level
LEVELS = {
    1: ("Easy", 1, 9, GREEN, "single digit numbers"),
    2: ("Moderate", 10, 99, ORANGE, "double digit numbers"),
    3: ("Advanced", 1000, 9999, RED, "4-digit numbers"),
}

# Colour used to display each letter grade
GRADE_COLOURS = {"A+": GREEN, "A": GREEN, "B": CYAN, "C": YELLOW, "D": ORANGE, "F": RED}

# Messages shown under the score
GRADE_MESSAGES = {
    "A+": "Outstanding! You're a maths genius!",
    "A": "Excellent work!",
    "B": "Great job!",
    "C": "Good effort - keep going!",
    "D": "Not bad - keep practising!",
    "F": "Don't give up - try again!",
}

# Helper functions
def randomInt(minimum, maximum):
    # Return a random whole number between minimum and maximum (both included)
    return random.randint(minimum, maximum)


def decideOperation():
    # Randomly choose whether the question will be an addition or a subtraction
    return random.choice(["+", "-"])


def getGrade(score):
    # Convert the final score (out of 100) into a letter grade
    # The checks go from highest to lowest, so the first match is the grade
    if score > 90:
        return "A+"
    elif score > 80:
        return "A"
    elif score > 70:
        return "B"
    elif score > 60:
        return "C"
    elif score > 50:
        return "D"
    return "F"  # Anything 50 or below


def adjustColour(hex_colour, factor):
    # Make a colour lighter or darker
    # factor > 1 lightens the colour, factor < 1 darkens it, factor = 1 leaves it unchanged
    hex_colour = hex_colour.lstrip("#")

    # Split the hex string into red, green and blue and convert each to a number (0-255)
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (0, 2, 4))

    if factor >= 1:
        # Lighten: move each value towards 255 (white)
        r, g, b = (int(c + (255 - c) * (factor - 1)) for c in (r, g, b))
    else:
        # Darken: scale each value towards 0 (black)
        r, g, b = (int(c * factor) for c in (r, g, b))

    # Keep colour values within the valid 0-255 range
    r, g, b = (max(0, min(255, c)) for c in (r, g, b))

    # Convert back to a hex colour string such as "#22c55e"
    return f"#{r:02x}{g:02x}{b:02x}"


# Custom button
# from a Label that changes colour when hovered or clicked
class HoverButton(tk.Label):
    def __init__(self, parent, text, command, colour, fg=DARK,
                 font=("Arial", 14, "bold"), width=18, pady=8):
        super().__init__(parent, text=text, bg=colour, fg=fg, font=font,
                         width=width, pady=pady, cursor="hand2")

        # Remember the base colour and the function to run when the button is clicked
        self.colour = colour
        self.command = command

        # Mouse events:
        self.bind("<Enter>", lambda e: self.config(bg=adjustColour(colour, 1.25)))   # Hover: lighter
        self.bind("<Leave>", lambda e: self.config(bg=colour))                       # Mouse leaves: normal
        self.bind("<Button-1>", lambda e: self.config(bg=adjustColour(colour, 0.8))) # Mouse pressed: darker
        self.bind("<ButtonRelease-1>", self._released)                               # Mouse released: click

    def _released(self, event):
        # Only count it as a click if the mouse is still over the button when released
        inside = 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height()

        if inside:
            self.config(bg=adjustColour(self.colour, 1.25))
            self.command()  # Run the function given when the button was created


# GUI application
class MathsQuiz:
    def __init__(self, root):
        # Set up the main window
        self.root = root
        self.root.title("Maths Quiz")
        self.root.geometry("560x600")      # Fixed window size (width x height)
        self.root.resizable(False, False)  # Stop the user resizing the window
        self.root.config(bg=BG)

        # Apply the custom icon if the file exists
        if ICON_FILE.exists():
            try:
                self.root.iconbitmap(str(ICON_FILE))
            except tk.TclError:
                # The file exists but is not a valid icon
                print("The icon file could not be loaded.")
        else:
            print("Icon file not found:", ICON_FILE)

        # A single frame holds everything on screen; each "screen" is built inside it
        self.container = tk.Frame(self.root, bg=BG, padx=20, pady=15)
        self.container.pack(fill="both", expand=True)

        # Quiz state (these variables track the progress of the game)
        self.level = 1               # Chosen difficulty level (1, 2 or 3)
        self.score = 0               # Current score
        self.best_score = 0          # Highest score in this session
        self.question_number = 0     # Which question the player is on
        self.attempt = 1             # Current attempt for this question (1 or 2)
        self.num1 = 0                # First number in the question
        self.num2 = 0                # Second number in the question
        self.operation = "+"         # Operation used in the question
        self.correct_answer = 0      # The right answer to the current question
        self.streak = 0              # Number of correct answers in a row
        self.results = []            # Result of each question: "first", "second" or "missed"
        self.locked = False          # True while input is disabled (e.g. between questions)
        self.anim_job = None         # Stores the running animation so it can be cancelled
        self.confetti = []           # List of confetti pieces on the results screen

        # Start by showing the menu
        self.displayMenu()

    # Utilities
    def clearScreen(self):
        # Remove everything on screen so a new screen can be drawn

        # Stop any running animation (such as the confetti)
        if self.anim_job is not None:
            try:
                self.root.after_cancel(self.anim_job)
            except tk.TclError:
                pass
            self.anim_job = None

        # Remove keyboard shortcuts from the previous screen
        for key in ("<Key-1>", "<Key-2>", "<Key-3>", "<Return>"):
            try:
                self.root.unbind(key)
            except tk.TclError:
                pass

        # Destroy every widget currently inside the container
        for widget in self.container.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass

    # Menu
    def displayMenu(self):
        self.clearScreen()

        # Title made of one label per letter so each letter can have its own colour
        title_row = tk.Frame(self.container, bg=BG)
        title_row.pack(pady=(25, 5))

        # One colour for each of the 10 characters in "MATHS QUIZ" (including the space)
        rainbow = [GREEN, YELLOW, ORANGE, RED, PINK, PURPLE, CYAN, GREEN, YELLOW, ORANGE]

        for i, letter in enumerate("MATHS QUIZ"):
            tk.Label(title_row, text=letter, bg=BG, fg=rainbow[i],
                     font=("Arial", 34, "bold")).pack(side="left")

        tk.Label(self.container, text="DIFFICULTY LEVEL", bg=BG, fg=TEXT,
                 font=("Arial", 16, "bold")).pack(pady=(15, 20))

        # Create one button (and description) for each difficulty level
        for number, (name, _, _, colour, description) in LEVELS.items():
            # "n=number" stores the current number so each button starts its own level
            HoverButton(self.container, f"{number}.  {name}",
                        command=lambda n=number: self.startQuiz(n),
                        colour=colour, width=22, pady=10).pack(pady=(8, 0))

            tk.Label(self.container, text=description, bg=BG, fg=MUTED,
                     font=("Arial", 10)).pack()

            # Keyboard shortcut: pressing 1, 2 or 3 also starts that level
            self.root.bind(f"<Key-{number}>", lambda e, n=number: self.startQuiz(n))

        tk.Label(self.container, text="Tip: press 1, 2 or 3 on your keyboard",
                 bg=BG, fg=GREY, font=("Arial", 10, "italic")).pack(side="bottom", pady=5)

    def startQuiz(self, level):
        # Reset everything for a new game, then ask the first question
        self.level = level
        self.score = 0
        self.question_number = 0
        self.streak = 0
        self.results = []
        self.nextQuestion()

    # Questions
    def nextQuestion(self):
        # If all questions have been asked, show the results instead
        if self.question_number >= TOTAL_QUESTIONS:
            self.displayResults()
            return

        # Prepare the state for the new question
        self.question_number += 1
        self.attempt = 1
        self.locked = False

        # Get the number range for the chosen level (the other values are not needed here)
        _, low, high, _, _ = LEVELS[self.level]

        # Generate two random numbers and a random operation
        self.num1 = randomInt(low, high)
        self.num2 = randomInt(low, high)
        self.operation = decideOperation()

        # Work out the correct answer
        if self.operation == "+":
            self.correct_answer = self.num1 + self.num2
        else:
            self.correct_answer = self.num1 - self.num2  # May be negative

        self.displayProblem()

    def displayProblem(self):
        self.clearScreen()

        name, _, _, colour, _ = LEVELS[self.level]

        # Top bar: level name, question number and score
        top = tk.Frame(self.container, bg=BG)
        top.pack(fill="x")

        tk.Label(top, text=f" {name} ", bg=colour, fg=DARK,
                 font=("Arial", 11, "bold")).pack(side="left")

        tk.Label(top, text=f"Question {self.question_number} of {TOTAL_QUESTIONS}",
                 bg=BG, fg=MUTED, font=("Arial", 11)).pack(side="left", padx=12)

        # Saved as self.score_label so it can be updated later without redrawing
        self.score_label = tk.Label(top, text=f"Score: {self.score}", bg=BG,
                                    fg=YELLOW, font=("Arial", 18, "bold"))
        self.score_label.pack(side="right")

        # Progress bar: a canvas with one coloured block per question
        self.progress = tk.Canvas(self.container, width=500, height=14, bg=BG,
                                  highlightthickness=0)
        self.progress.pack(pady=(14, 8))
        self.drawProgress()

        # Question card (the coloured border is used to flash green/red for feedback)
        self.card = tk.Frame(self.container, bg=CARD, highlightthickness=4,
                             highlightbackground=GREY, highlightcolor=GREY)
        self.card.pack(padx=30, pady=10, fill="x")

        # The maths problem, for example "7 + 5 ="
        self.problem_label = tk.Label(
            self.card, text=f"{self.num1} {self.operation} {self.num2} =",
            bg=CARD, fg=TEXT, font=("Arial", 38, "bold"))
        self.problem_label.pack(pady=(25, 12))

        # Answer box where the player types their answer
        self.answer_entry = tk.Entry(
            self.card, font=("Arial", 26, "bold"), width=10, justify="center",
            bg="#ede9fe", fg=DARK, insertbackground=DARK, relief="flat",
            highlightthickness=3, highlightbackground=PURPLE, highlightcolor=CYAN,
            disabledbackground="#c4b5fd", disabledforeground=DARK)

        self.answer_entry.pack(ipady=4)
        self.answer_entry.focus_set()  # Place the cursor in the box automatically
        self.answer_entry.bind("<Return>", lambda event: self.submitAnswer())  # Enter key submits

        # Attempt label 
        self.attempt_label = tk.Label(self.card, bg=CARD, font=("Arial", 11, "bold"))
        self.attempt_label.pack(pady=(12, 18))
        self.updateAttemptLabel()

        HoverButton(self.container, "Submit", command=self.submitAnswer,
                    colour=CYAN, width=16).pack(pady=8)

        # Feedback 
        self.feedback_label = tk.Label(self.container, text="", bg=BG,
                                       font=("Arial", 14, "bold"), wraplength=480)
        self.feedback_label.pack(pady=(8, 2))

        # Streak 
        self.streak_label = tk.Label(self.container, text="", bg=BG, fg=PINK,
                                     font=("Arial", 12, "bold"))
        self.streak_label.pack()
        self.updateStreakLabel()

    def drawProgress(self):
        # Redraw the progress bar from scratch
        self.progress.delete("all")

        # Colour of each finished block depends on how the question was answered
        colours = {"first": GREEN, "second": YELLOW, "missed": RED}
        block = 50  # Width of each block in pixels (10 blocks x 50 = 500)

        for i in range(TOTAL_QUESTIONS):
            if i < len(self.results):
                fill = colours[self.results[i]]   # Already answered
            elif i == self.question_number - 1:
                fill = CYAN                       # The current question
            else:
                fill = GREY                       # Not reached yet

            # Draw the block, leaving a 2 pixel gap on each side
            self.progress.create_rectangle(i * block + 2, 2, (i + 1) * block - 2, 12,
                                           fill=fill, outline="")

    def updateAttemptLabel(self):
        # Show the attempt number and how many points it is worth
        if self.attempt == 1:
            self.attempt_label.config(
                text=f"Attempt 1 of 2  •  worth {FIRST_ATTEMPT_POINTS} points", fg=GREEN)
        else:
            self.attempt_label.config(
                text=f"Attempt 2 of 2  •  worth {SECOND_ATTEMPT_POINTS} points", fg=ORANGE)

    def updateStreakLabel(self):
        # Only show the streak message from 2 correct answers in a row
        if self.streak >= 2:
            self.streak_label.config(text=f"Streak: {self.streak} correct in a row!")
        else:
            self.streak_label.config(text="")

    # Answering
    def submitAnswer(self):
        # Ignore the click or Enter key if input is locked (e.g. waiting for the next question)
        if self.locked:
            return

        text = self.answer_entry.get().strip()

        # Make sure the player typed a whole number
        try:
            user_answer = int(text)
        except ValueError:
            self.feedback_label.config(text="Please enter a whole number.", fg=ORANGE)
            self.shake(self.card)
            return  # Not counted as an attempt

        if self.isCorrect(user_answer):
            # Correct answer: award points depending on the attempt
            if self.attempt == 1:
                self.score += FIRST_ATTEMPT_POINTS
                self.results.append("first")
            else:
                self.score += SECOND_ATTEMPT_POINTS
                self.results.append("second")

            self.streak += 1

            # Update the screen to match the new state
            self.score_label.config(text=f"Score: {self.score}")
            self.updateStreakLabel()
            self.drawProgress()
            self.flash(GREEN)
            self.lockInput()

            # Wait 1.2 seconds so the player can see the feedback, then move on
            self.root.after(1200, self.nextQuestion)

        elif self.attempt == 1:
            # Wrong on the first attempt: give the player a second chance
            self.attempt = 2
            self.updateAttemptLabel()
            self.answer_entry.delete(0, tk.END)  # Clear the box for the new try
            self.flash(RED)
            self.shake(self.card)

        else:
            # Wrong on the second attempt: the question is missed
            self.results.append("missed")
            self.streak = 0  # Streak is broken
            self.updateStreakLabel()
            self.drawProgress()
            self.flash(RED)
            self.shake(self.card)
            self.lockInput()

            # Wait 2 seconds so the player has time to read the correct answer
            self.root.after(2000, self.nextQuestion)

    def isCorrect(self, user_answer):
        # Check the answer, show the matching feedback message and return True or False
        if user_answer == self.correct_answer:
            points = FIRST_ATTEMPT_POINTS if self.attempt == 1 else SECOND_ATTEMPT_POINTS
            self.feedback_label.config(text=f"Correct!  +{points} points", fg=GREEN)
            return True

        if self.attempt == 1:
            self.feedback_label.config(text="Not quite - you have one more try!", fg=RED)
        else:
            self.feedback_label.config(
                text=f"Wrong again. The answer was {self.correct_answer}.", fg=RED)

        return False

    def lockInput(self):
        # Stop the player from typing or submitting while the app waits for the next question
        self.locked = True
        self.answer_entry.config(state="disabled")

    # Animations
    def flash(self, colour):
        # Change the card border to the given colour (green or red) for a moment
        try:
            self.card.config(highlightbackground=colour, highlightcolor=colour)
        except tk.TclError:
            return  # The card no longer exists (screen changed)

        # After half a second, put the border back to normal
        self.root.after(500, self.resetBorder)

    def resetBorder(self):
        # Return the card border to its normal grey colour
        try:
            self.card.config(highlightbackground=GREY, highlightcolor=GREY)
        except tk.TclError:
            pass

    def shake(self, widget, step=0):
        # Shake a widget left and right by changing its padding step by step
        # Each offset is smaller than the last, so the shake fades out
        offsets = [12, -12, 9, -9, 5, -5, 0]

        # Stop when every step has been played
        if step >= len(offsets):
            return

        offset = offsets[step]

        try:
            # Adding to the left padding and removing from the right moves the widget sideways
            widget.pack_configure(padx=(30 + offset, 30 - offset))
        except tk.TclError:
            return

        # Run the next step after 35 milliseconds
        self.root.after(35, lambda: self.shake(widget, step + 1))

    def startConfetti(self, canvas, width, height):
        # Create 50 small coloured squares at random positions above the canvas
        colours = [GREEN, YELLOW, RED, CYAN, PINK, PURPLE, ORANGE]
        self.confetti = []

        for _ in range(50):
            x = random.randint(0, width)
            y = random.randint(-height, 0)  # Start above the visible area
            size = random.randint(5, 10)

            item = canvas.create_rectangle(x, y, x + size, y + size,
                                           fill=random.choice(colours), outline="")

            # Store each piece with its sideways speed (dx) and falling speed (dy)
            self.confetti.append((item, random.uniform(-1.5, 1.5), random.uniform(2, 5)))

        self.animateConfetti(canvas, width, height)

    def animateConfetti(self, canvas, width, height):
        # Move every piece a little, then schedule the next frame
        for item, dx, dy in self.confetti:
            try:
                canvas.move(item, dx, dy)
                x1, y1, x2, y2 = canvas.coords(item)

                # If a piece falls below the canvas, send it back above the top
                if y1 > height:
                    canvas.move(item, 0, -(height + random.randint(10, 60)))

                # Wrap pieces around if they drift off the left or right side
                if x1 > width:
                    canvas.move(item, -width, 0)
                elif x2 < 0:
                    canvas.move(item, width, 0)

            except tk.TclError:
                return  # The canvas was destroyed, so stop animating

        # Run again after 30 ms (about 33 frames per second); the job is saved so it can be cancelled
        self.anim_job = self.root.after(
            30, lambda: self.animateConfetti(canvas, width, height))

    # Results
    def displayResults(self):
        self.clearScreen()

        # Work out the grade and its colour from the final score
        grade = getGrade(self.score)
        colour = GRADE_COLOURS[grade]

        # Update the best score for this session if the player beat it
        self.best_score = max(self.best_score, self.score)

        # Banner
        width, height = 520, 90

        banner = tk.Canvas(self.container, width=width, height=height, bg=BG,
                           highlightthickness=0)
        banner.pack()

        # No confetti for a fail grade
        if grade != "F":
            self.startConfetti(banner, width, height)

        banner.create_text(width // 2, height // 2, text="QUIZ COMPLETE!",
                           font=("Arial", 28, "bold"), fill=TEXT)

        # Grade badge 
        badge = tk.Canvas(self.container, width=130, height=130, bg=BG,
                         highlightthickness=0)
        badge.pack(pady=(5, 0))

        badge.create_oval(5, 5, 125, 125, fill=colour,
                          outline=adjustColour(colour, 1.4), width=4)

        badge.create_text(65, 65, text=grade, font=("Arial", 44, "bold"), fill=DARK)

        # Final score
        tk.Label(self.container, text=f"{self.score} / 100", bg=BG, fg=TEXT,
                 font=("Arial", 30, "bold")).pack(pady=(8, 0))

        tk.Label(self.container, text=GRADE_MESSAGES[grade], bg=BG, fg=colour,
                 font=("Arial", 14, "bold")).pack(pady=(2, 8))

        # Stats: how many questions were answered on the first try, second try, or missed
        stats = tk.Frame(self.container, bg=BG)
        stats.pack()

        tk.Label(stats, text=f"First try: {self.results.count('first')}",
                 bg=BG, fg=GREEN, font=("Arial", 12, "bold")).pack(side="left", padx=10)

        tk.Label(stats, text=f"Second try: {self.results.count('second')}",
                 bg=BG, fg=YELLOW, font=("Arial", 12, "bold")).pack(side="left", padx=10)

        tk.Label(stats, text=f"Missed: {self.results.count('missed')}",
                 bg=BG, fg=RED, font=("Arial", 12, "bold")).pack(side="left", padx=10)

        tk.Label(self.container, text=f"Best score this session: {self.best_score}",
                 bg=BG, fg=MUTED, font=("Arial", 11)).pack(pady=(8, 0))

        tk.Label(self.container, text="Would you like to play again?",
                 bg=BG, fg=TEXT, font=("Arial", 13)).pack(pady=(10, 6))

        # Play Again / Quit buttons
        buttons = tk.Frame(self.container, bg=BG)
        buttons.pack()

        HoverButton(buttons, "Play Again", command=self.displayMenu,
                    colour=GREEN, width=12).grid(row=0, column=0, padx=8)

        HoverButton(buttons, "Quit", command=self.root.destroy,
                    colour=RED, width=12).grid(row=0, column=1, padx=8)

        # Pressing Enter also starts a new game
        self.root.bind("<Return>", lambda e: self.displayMenu())


def main():
    # Try to create the main window; this fails on systems with no desktop (e.g. online editors)
    try:
        root = tk.Tk()
    except tk.TclError as error:
        print("Could not open a window:", error)
        print("Run this file on a computer with a desktop (not an online editor).")
        return

    MathsQuiz(root)   # Build the quiz inside the window
    root.mainloop()   # Keep the window open and listen for clicks and key presses


# Only run the game when this file is executed directly
# (it will not start if the file is imported by another program)
if __name__ == "__main__":
    main()