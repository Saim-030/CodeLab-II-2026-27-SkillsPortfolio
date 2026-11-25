import random
import tkinter as tk

# SETTINGS - change these to customise the app
class BASE_DIR:
    ...

ICON_FILE = BASE_DIR / "Exercise 1/Logo 1.ico"
# Game settings
TOTAL_QUESTIONS = 10          # number of questions in one round
FIRST_ATTEMPT_POINTS = 10     # points for a correct answer on the first try
SECOND_ATTEMPT_POINTS = 5     # points for a correct answer on the second try

# Colour theme 
BG = "#1e1b4b"       # deep indigo background
CARD = "#312e81"     # lighter indigo for the question card
TEXT = "#f8fafc"     # main text colour 
MUTED = "#a5b4fc"    # softer text colour for less important labels
DARK = "#0f172a"     # dark text colour used on bright buttons
GREY = "#4c4a7a"     # neutral colour for borders and empty progress blocks
GREEN = "#22c55e"
YELLOW = "#facc15"
ORANGE = "#fb923c"
RED = "#fb7185"
CYAN = "#22d3ee"
PINK = "#ec4899"
PURPLE = "#a855f7"

# Difficulty level -> (name, min, max, colour, description)
# min and max set the range of the random numbers used in the questions
LEVELS = {
    1: ("Easy", 1, 9, GREEN, "single digit numbers"),
    2: ("Moderate", 10, 99, ORANGE, "double digit numbers"),
    3: ("Advanced", 1000, 9999, RED, "4-digit numbers"),
}

# Colour used to display each letter grade on the results screen
GRADE_COLOURS = {"A+": GREEN, "A": GREEN, "B": CYAN, "C": YELLOW, "D": ORANGE, "F": RED}

# Message shown under the score for each letter grade
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
    """Return a random integer between minimum and maximum (inclusive)."""
    return random.randint(minimum, maximum)


def decideOperation():
    """Randomly choose addition or subtraction and return '+' or '-'."""
    return random.choice(["+", "-"])


def getGrade(score):
    """Return a letter rank for a score out of 100."""
    # Checked from the highest grade down, so the first match wins
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
    return "F"


def adjustColour(hex_colour, factor):
    """Lighten (factor > 1) or darken (factor < 1) a #rrggbb colour."""
    # Remove the leading '#' and split the code into red, green and blue values
    hex_colour = hex_colour.lstrip("#")
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (0, 2, 4))
    if factor >= 1:
        # Lighten: move each channel towards 255 (white)
        r, g, b = (int(c + (255 - c) * (factor - 1)) for c in (r, g, b))
    else:
        # Darken: scale each channel down towards 0 (black)
        r, g, b = (int(c * factor) for c in (r, g, b))
    # Convert the three channels back into a #rrggbb string
    return f"#{r:02x}{g:02x}{b:02x}"


# Custom button: a Label that reacts to hover and click (looks the same on
# Windows, macOS and Linux, unlike tk.Button which ignores colours on macOS)
class HoverButton(tk.Label):
    def __init__(self, parent, text, command, colour, fg=DARK,
                 font=("Arial", 14, "bold"), width=18, pady=8):
        super().__init__(parent, text=text, bg=colour, fg=fg, font=font,
                         width=width, pady=pady, cursor="hand2")
        self.colour = colour      # remember the normal colour
        self.command = command    # function to run when the button is clicked
        # Lighten when the mouse enters, restore when it leaves
        self.bind("<Enter>", lambda e: self.config(bg=adjustColour(colour, 1.25)))
        self.bind("<Leave>", lambda e: self.config(bg=colour))
        # Darken while the mouse button is held down
        self.bind("<Button-1>", lambda e: self.config(bg=adjustColour(colour, 0.8)))
        self.bind("<ButtonRelease-1>", self._released)

    def _released(self, event):
        # Only count it as a click if the mouse is still over the button
        inside = 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height()
        if inside:
            self.config(bg=adjustColour(self.colour, 1.25))
            self.command()

# GUI application
class MathsQuiz:
    def __init__(self, root):
        # Set up the main window
        self.root = root
        self.root.title("Maths Quiz")
        self.root.geometry("560x600")
        self.root.resizable(False, False)
        self.root.config(bg=BG)

        # One container frame holds every screen; screens are swapped by
        # destroying its children and drawing new ones
        self.container = tk.Frame(self.root, bg=BG, padx=20, pady=15)
        self.container.pack(fill="both", expand=True)

        # Quiz state
        self.level = 1               # chosen difficulty level (1, 2 or 3)
        self.score = 0               # current score out of 100
        self.best_score = 0          # best score this session
        self.question_number = 0     # which question the player is on
        self.attempt = 1             # 1 = first try, 2 = second try
        self.num1 = 0                # first number in the problem
        self.num2 = 0                # second number in the problem
        self.operation = "+"         # '+' or '-'
        self.correct_answer = 0      # the right answer for the current problem
        self.streak = 0              # correct answers in a row
        self.results = []            # "first", "second" or "missed" per question
        self.locked = False          # True while waiting for the next question
        self.anim_job = None         # confetti animation job
        self.confetti = []           # list of confetti pieces on the results screen

        # Start on the difficulty menu
        self.displayMenu()

    # utilities
    def clearScreen(self):
        """Remove everything from the window so a new screen can be drawn."""
        # Stop any running confetti animation
        if self.anim_job is not None:
            try:
                self.root.after_cancel(self.anim_job)
            except tk.TclError:
                pass                      # the job had already finished
            self.anim_job = None
        # Remove keyboard shortcuts from the previous screen
        for key in ("<Key-1>", "<Key-2>", "<Key-3>", "<Return>"):
            try:
                self.root.unbind(key)
            except tk.TclError:
                pass                      # nothing was bound to this key
        # Destroy all widgets currently in the container
        for widget in self.container.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass                      # the widget was already destroyed

    # Menu
    def displayMenu(self):
        """Show the difficulty level menu."""
        self.clearScreen()

        # Rainbow title: one label per letter
        title_row = tk.Frame(self.container, bg=BG)
        title_row.pack(pady=(25, 5))
        rainbow = [GREEN, YELLOW, ORANGE, RED, PINK, PURPLE, CYAN, GREEN, YELLOW, ORANGE]
        for i, letter in enumerate("MATHS QUIZ"):
            tk.Label(title_row, text=letter, bg=BG, fg=rainbow[i],
                     font=("Arial", 34, "bold")).pack(side="left")

        tk.Label(self.container, text="DIFFICULTY LEVEL", bg=BG, fg=TEXT,
                 font=("Arial", 16, "bold")).pack(pady=(15, 20))

        # Create one button for each difficulty level
        for number, (name, _, _, colour, description) in LEVELS.items():
            HoverButton(self.container, f"{number}.  {name}",
                        command=lambda n=number: self.startQuiz(n),
                        colour=colour, width=22, pady=10).pack(pady=(8, 0))
            tk.Label(self.container, text=description, bg=BG, fg=MUTED,
                     font=("Arial", 10)).pack()
            # Keyboard shortcut: pressing 1, 2 or 3 starts that level
            self.root.bind(f"<Key-{number}>", lambda e, n=number: self.startQuiz(n))

        tk.Label(self.container, text="Tip: press 1, 2 or 3 on your keyboard",
                 bg=BG, fg=GREY, font=("Arial", 10, "italic")).pack(side="bottom", pady=5)

    def startQuiz(self, level):
        """Reset the state and begin a new round at the chosen level."""
        self.level = level
        self.score = 0
        self.question_number = 0
        self.streak = 0
        self.results = []
        self.nextQuestion()

    # Questions
    def nextQuestion(self):
        """Generate the next problem, or show results after the last one."""
        # All questions answered: go to the results screen
        if self.question_number >= TOTAL_QUESTIONS:
            self.displayResults()
            return

        # Prepare the state for the new question
        self.question_number += 1
        self.attempt = 1
        self.locked = False

        # Pick two random numbers within the range of the chosen level
        _, low, high, _, _ = LEVELS[self.level]
        self.num1 = randomInt(low, high)
        self.num2 = randomInt(low, high)
        self.operation = decideOperation()

        # Work out the correct answer
        if self.operation == "+":
            self.correct_answer = self.num1 + self.num2
        else:
            self.correct_answer = self.num1 - self.num2

        self.displayProblem()

    def displayProblem(self):
        """Show the current problem and an Entry box for the answer."""
        self.clearScreen()
        name, _, _, colour, _ = LEVELS[self.level]

        # Top bar: level chip, question number, score
        top = tk.Frame(self.container, bg=BG)
        top.pack(fill="x")
        tk.Label(top, text=f" {name} ", bg=colour, fg=DARK,
                 font=("Arial", 11, "bold")).pack(side="left")
        tk.Label(top, text=f"Question {self.question_number} of {TOTAL_QUESTIONS}",
                 bg=BG, fg=MUTED, font=("Arial", 11)).pack(side="left", padx=12)
        self.score_label = tk.Label(top, text=f"Score: {self.score}", bg=BG,
                                    fg=YELLOW, font=("Arial", 18, "bold"))
        self.score_label.pack(side="right")

        # Progress bar (one block per question)
        self.progress = tk.Canvas(self.container, width=500, height=14, bg=BG,
                                  highlightthickness=0)
        self.progress.pack(pady=(14, 8))
        self.drawProgress()

        # Question card (the border colour flashes green/red after an answer)
        self.card = tk.Frame(self.container, bg=CARD, highlightthickness=4,
                             highlightbackground=GREY, highlightcolor=GREY)
        self.card.pack(padx=30, pady=10, fill="x")

        # The maths problem itself, e.g. "12 + 7 ="
        self.problem_label = tk.Label(
            self.card, text=f"{self.num1} {self.operation} {self.num2} =",
            bg=CARD, fg=TEXT, font=("Arial", 38, "bold"))
        self.problem_label.pack(pady=(25, 12))

        # Entry box where the player types their answer
        self.answer_entry = tk.Entry(
            self.card, font=("Arial", 26, "bold"), width=10, justify="center",
            bg="#ede9fe", fg=DARK, insertbackground=DARK, relief="flat",
            highlightthickness=3, highlightbackground=PURPLE, highlightcolor=CYAN,
            disabledbackground="#c4b5fd", disabledforeground=DARK)
        self.answer_entry.pack(ipady=4)
        self.answer_entry.focus_set()   # put the cursor in the box straight away
        self.answer_entry.bind("<Return>", lambda event: self.submitAnswer())

        # Label showing which attempt the player is on and its points
        self.attempt_label = tk.Label(self.card, bg=CARD, font=("Arial", 11, "bold"))
        self.attempt_label.pack(pady=(12, 18))
        self.updateAttemptLabel()

        HoverButton(self.container, "Submit", command=self.submitAnswer,
                    colour=CYAN, width=16).pack(pady=8)

        # Feedback message (correct / wrong) appears here
        self.feedback_label = tk.Label(self.container, text="", bg=BG,
                                       font=("Arial", 14, "bold"), wraplength=480)
        self.feedback_label.pack(pady=(8, 2))

        # Streak message appears here once the player has 2+ correct in a row
        self.streak_label = tk.Label(self.container, text="", bg=BG, fg=PINK,
                                     font=("Arial", 12, "bold"))
        self.streak_label.pack()
        self.updateStreakLabel()

    def drawProgress(self):
        """Draw 10 blocks: green = 1st try, yellow = 2nd try, red = missed."""
        self.progress.delete("all")   # clear the old blocks before redrawing
        colours = {"first": GREEN, "second": YELLOW, "missed": RED}
        block = 50                    # width of each block in pixels
        for i in range(TOTAL_QUESTIONS):
            if i < len(self.results):
                # Question already finished: colour by how it went
                fill = colours[self.results[i]]
            elif i == self.question_number - 1:
                # The question currently being answered
                fill = CYAN
            else:
                # Questions still to come
                fill = GREY
            self.progress.create_rectangle(i * block + 2, 2, (i + 1) * block - 2, 12,
                                           fill=fill, outline="")

    def updateAttemptLabel(self):
        """Show whether this is attempt 1 or 2 and how many points it is worth."""
        if self.attempt == 1:
            self.attempt_label.config(
                text=f"Attempt 1 of 2  •  worth {FIRST_ATTEMPT_POINTS} points", fg=GREEN)
        else:
            self.attempt_label.config(
                text=f"Attempt 2 of 2  •  worth {SECOND_ATTEMPT_POINTS} points", fg=ORANGE)

    def updateStreakLabel(self):
        """Show the streak message only when the streak is 2 or more."""
        if self.streak >= 2:
            self.streak_label.config(text=f"Streak: {self.streak} correct in a row!")
        else:
            self.streak_label.config(text="")

    # Answering
    def submitAnswer(self):
        """Read the Entry box, check the answer and move the quiz along."""
        # Ignore clicks/Enter presses while waiting for the next question
        if self.locked:
            return

        # Make sure the player typed a whole number
        text = self.answer_entry.get().strip()
        try:
            user_answer = int(text)
        except ValueError:
            self.feedback_label.config(text="Please enter a whole number.", fg=ORANGE)
            self.shake(self.card)
            return

        if self.isCorrect(user_answer):
            # Correct: award points depending on which attempt it was
            if self.attempt == 1:
                self.score += FIRST_ATTEMPT_POINTS
                self.results.append("first")
            else:
                self.score += SECOND_ATTEMPT_POINTS
                self.results.append("second")
            self.streak += 1
            # Refresh the display
            self.score_label.config(text=f"Score: {self.score}")
            self.updateStreakLabel()
            self.drawProgress()
            self.flash(GREEN)
            # Lock the entry and move on after a short pause
            self.lockInput()
            self.root.after(1200, self.nextQuestion)
        elif self.attempt == 1:
            # Wrong on the first try: give the player a second chance
            self.attempt = 2
            self.updateAttemptLabel()
            self.answer_entry.delete(0, tk.END)
            self.flash(RED)
            self.shake(self.card)
        else:
            # Wrong on the second try: record a miss and reveal the answer
            self.results.append("missed")
            self.streak = 0
            self.updateStreakLabel()
            self.drawProgress()
            self.flash(RED)
            self.shake(self.card)
            self.lockInput()
            # Longer pause so the player can read the correct answer
            self.root.after(2000, self.nextQuestion)

    def isCorrect(self, user_answer):
        """Check the answer, show an appropriate message and return True/False."""
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
        """Disable the Entry box so no more answers can be typed."""
        self.locked = True
        self.answer_entry.config(state="disabled")

    # Animations
    def flash(self, colour):
        """Briefly colour the card border."""
        try:
            self.card.config(highlightbackground=colour, highlightcolor=colour)
        except tk.TclError:
            # The card was already destroyed (screen changed), so do nothing
            return
        # Return the border to normal after half a second
        self.root.after(500, self.resetBorder)

    def resetBorder(self):
        """Put the card border back to its normal grey colour."""
        try:
            self.card.config(highlightbackground=GREY, highlightcolor=GREY)
        except tk.TclError:
            pass

    def shake(self, widget, step=0):
        """Wiggle a packed widget left and right."""
        # Horizontal offsets in pixels; they get smaller so the shake settles
        offsets = [12, -12, 9, -9, 5, -5, 0]
        if step >= len(offsets):
            return
        offset = offsets[step]
        try:
            # Change the left/right padding to move the widget sideways
            widget.pack_configure(padx=(30 + offset, 30 - offset))
        except tk.TclError:
            return
        # Schedule the next step of the shake
        self.root.after(35, lambda: self.shake(widget, step + 1))

    def startConfetti(self, canvas, width, height):
        """Create the confetti pieces and start animating them."""
        colours = [GREEN, YELLOW, RED, CYAN, PINK, PURPLE, ORANGE]
        self.confetti = []
        for _ in range(50):
            # Start each piece at a random spot above the visible area
            x = random.randint(0, width)
            y = random.randint(-height, 0)
            size = random.randint(5, 10)
            item = canvas.create_rectangle(x, y, x + size, y + size,
                                           fill=random.choice(colours), outline="")
            # Store the piece with its sideways speed (dx) and falling speed (dy)
            self.confetti.append((item, random.uniform(-1.5, 1.5), random.uniform(2, 5)))
        self.animateConfetti(canvas, width, height)

    def animateConfetti(self, canvas, width, height):
        """Move every confetti piece one step and schedule the next frame."""
        for item, dx, dy in self.confetti:
            canvas.move(item, dx, dy)
            x1, y1, x2, y2 = canvas.coords(item)
            # If a piece has fallen off the bottom, send it back above the top
            if y1 > height:
                canvas.move(item, 0, -(height + random.randint(10, 60)))
            # Wrap pieces around the left and right edges
            if x1 > width:
                canvas.move(item, -width, 0)
            elif x2 < 0:
                canvas.move(item, width, 0)
        # Run again in 30 ms; the job id is saved so clearScreen can cancel it
        self.anim_job = self.root.after(30, lambda: self.animateConfetti(canvas, width, height))

    # Results
    def displayResults(self):
        """Show the final score out of 100, a rank, and replay options."""
        self.clearScreen()
        grade = getGrade(self.score)
        colour = GRADE_COLOURS[grade]
        # Update the best score for this session if the player beat it
        self.best_score = max(self.best_score, self.score)

        # Banner with falling confetti (not for an F)
        width, height = 520, 90
        banner = tk.Canvas(self.container, width=width, height=height, bg=BG,
                           highlightthickness=0)
        banner.pack()
        if grade != "F":
            self.startConfetti(banner, width, height)
        banner.create_text(width // 2, height // 2, text="QUIZ COMPLETE!",
                           font=("Arial", 28, "bold"), fill=TEXT)

        # Grade badge: a coloured circle with the letter grade inside
        badge = tk.Canvas(self.container, width=130, height=130, bg=BG, highlightthickness=0)
        badge.pack(pady=(5, 0))
        badge.create_oval(5, 5, 125, 125, fill=colour, outline=adjustColour(colour, 1.4), width=4)
        badge.create_text(65, 65, text=grade, font=("Arial", 44, "bold"), fill=DARK)

        # Final score and a message that matches the grade
        tk.Label(self.container, text=f"{self.score} / 100", bg=BG, fg=TEXT,
                 font=("Arial", 30, "bold")).pack(pady=(8, 0))
        tk.Label(self.container, text=GRADE_MESSAGES[grade], bg=BG, fg=colour,
                 font=("Arial", 14, "bold")).pack(pady=(2, 8))

        # Stats row: how many questions were answered on each attempt, or missed
        stats = tk.Frame(self.container, bg=BG)
        stats.pack()
        tk.Label(stats, text=f"First try: {self.results.count('first')}", bg=BG, fg=GREEN,
                 font=("Arial", 12, "bold")).pack(side="left", padx=10)
        tk.Label(stats, text=f"Second try: {self.results.count('second')}", bg=BG, fg=YELLOW,
                 font=("Arial", 12, "bold")).pack(side="left", padx=10)
        tk.Label(stats, text=f"Missed: {self.results.count('missed')}", bg=BG, fg=RED,
                 font=("Arial", 12, "bold")).pack(side="left", padx=10)

        tk.Label(self.container, text=f"Best score this session: {self.best_score}",
                 bg=BG, fg=MUTED, font=("Arial", 11)).pack(pady=(8, 0))

        tk.Label(self.container, text="Would you like to play again?", bg=BG, fg=TEXT,
                 font=("Arial", 13)).pack(pady=(10, 6))

        # Play Again / Quit buttons side by side
        buttons = tk.Frame(self.container, bg=BG)
        buttons.pack()
        HoverButton(buttons, "Play Again", command=self.displayMenu, colour=GREEN,
                    width=12).grid(row=0, column=0, padx=8)
        HoverButton(buttons, "Quit", command=self.root.destroy, colour=RED,
                    width=12).grid(row=0, column=1, padx=8)
        # Pressing Enter also starts a new game
        self.root.bind("<Return>", lambda e: self.displayMenu())


def main():
    """Create the window and start the Tkinter event loop."""
    # Opening the window fails if there is no screen (e.g. online editors,
    # SSH sessions), so catch that and explain instead of crashing
    try:
        root = tk.Tk()
    except tk.TclError as error:
        print("Could not open a window:", error)
        print("Run this file on a computer with a desktop (not an online editor).")
        return
    MathsQuiz(root)
    root.mainloop()


# Only run the game when this file is executed directly (not when imported)
if __name__ == "__main__":
    main()