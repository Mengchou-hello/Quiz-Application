import tkinter as tk
from tkinter import messagebox, ttk
import json
import threading

class QuizifyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quizify - Create and Take Quizzes")
        self.root.geometry("800x600")
        self.root.config(bg="#F4F4F4")

        self.quizzes = {}
        self.current_quiz = None
        self.time_limit = 300  # Default time limit (5 minutes)
        self.user_type = None  # Track whether the user is a "Student" or "Teacher"
        self.question_data = []  # Stores questions for the current quiz
        self.timer_thread = None  # Thread for the timer
        self.current_question_index = 0  # Track the current question index
        self.score = 0  # Track the score

        self.create_initial_screen()
        self.load_data()

        # Handle app closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_initial_screen(self):
        """Create the initial screen to select user type."""
        self.clear_frame()
        self.main_frame = tk.Frame(self.root, bg="#F4F4F4")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            self.main_frame,
            text="Welcome to Quizify",
            font=("Helvetica", 24, "bold"),
            bg="#F4F4F4",
            fg="#4A90E2"
        ).pack(pady=20)

        tk.Label(
            self.main_frame,
            text="Are you a Student or a Teacher?",
            font=("Helvetica", 16),
            bg="#F4F4F4"
        ).pack(pady=10)

        ttk.Button(self.main_frame, text="Student", command=lambda: self.set_user_type("Student")).pack(pady=10)
        ttk.Button(self.main_frame, text="Teacher", command=lambda: self.set_user_type("Teacher")).pack(pady=10)

    def set_user_type(self, user_type):
        self.user_type = user_type
        self.create_user_type_form()

    def create_user_type_form(self):
        """Create user-type-specific form fields."""
        self.clear_frame()
        self.main_frame = tk.Frame(self.root, bg="#F4F4F4")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            self.main_frame,
            text=f"Welcome, {self.user_type}!",
            font=("Helvetica", 24, "bold"),
            bg="#F4F4F4",
            fg="#4A90E2"
        ).pack(pady=20)

        if self.user_type == "Student":
            tk.Label(self.main_frame, text="First Name:", font=("Helvetica", 12), bg="#F4F4F4").pack(pady=5)
            self.first_name_entry = ttk.Entry(self.main_frame, width=30)
            self.first_name_entry.pack(pady=5)

            tk.Label(self.main_frame, text="Last Name:", font=("Helvetica", 12), bg="#F4F4F4").pack(pady=5)
            self.last_name_entry = ttk.Entry(self.main_frame, width=30)
            self.last_name_entry.pack(pady=5)

        elif self.user_type == "Teacher":
            tk.Label(self.main_frame, text="Teacher Name:", font=("Helvetica", 12), bg="#F4F4F4").pack(pady=5)
            self.teacher_name_entry = ttk.Entry(self.main_frame, width=30)
            self.teacher_name_entry.pack(pady=5)

        tk.Label(self.main_frame, text="Section:", font=("Helvetica", 12), bg="#F4F4F4").pack(pady=5)
        self.section_entry = ttk.Entry(self.main_frame, width=30)
        self.section_entry.pack(pady=5)

        tk.Label(self.main_frame, text="Time Setting (seconds):", font=("Helvetica", 12), bg="#F4F4F4").pack(pady=5)
        self.time_limit_var = tk.StringVar(value=str(self.time_limit))
        self.time_limit_entry = ttk.Entry(self.main_frame, textvariable=self.time_limit_var, width=10)
        self.time_limit_entry.pack(pady=5)

        ttk.Button(self.main_frame, text="Proceed", command=self.create_homepage).pack(pady=10)
        ttk.Button(self.main_frame, text="Back", command=self.create_initial_screen).pack(pady=10)

    def create_homepage(self):
        """Create the homepage layout."""
        self.clear_frame()
        self.main_frame = tk.Frame(self.root, bg="#F4F4F4")
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        tk.Label(
            self.main_frame,
            text=f"Welcome, {self.user_type}!",
            font=("Helvetica", 24, "bold"),
            bg="#F4F4F4",
            fg="#4A90E2"
        ).pack(pady=20)

        ttk.Button(self.main_frame, text="Create Quiz", command=self.create_quiz).pack(pady=10)
        ttk.Button(self.main_frame, text="Take Quiz", command=self.select_quiz).pack(pady=10)
        ttk.Button(self.main_frame, text="Save & Exit", command=self.save_data).pack(pady=10)

    def create_quiz(self):
        """Create the quiz creation form for the teacher."""
        self.clear_frame()
        self.main_frame = tk.Frame(self.root, bg="#F4F4F4")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            self.main_frame,
            text="Enter Quiz Title:",
            font=("Helvetica", 14),
            bg="#F4F4F4"
        ).grid(row=0, column=0, pady=10, sticky="e")

        self.quiz_title_entry = ttk.Entry(self.main_frame, width=40)
        self.quiz_title_entry.grid(row=0, column=1, pady=10)

        self.question_frame = tk.Frame(self.main_frame, bg="#F4F4F4")
        self.question_frame.grid(row=1, column=0, columnspan=2, pady=10)

        self.create_question_widgets()

        ttk.Button(self.main_frame, text="Add Question", command=self.add_question).grid(row=2, column=0, pady=20)
        ttk.Button(self.main_frame, text="Save Quiz", command=self.save_quiz).grid(row=2, column=1, pady=20)

    def create_question_widgets(self):
        """Create widgets for adding a single question."""
        for widget in self.question_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.question_frame,
            text="Question Type:",
            font=("Helvetica", 12),
            bg="#F4F4F4"
        ).grid(row=0, column=0, pady=5, sticky="e")

        self.question_type_var = tk.StringVar(value="Multiple Choice")
        question_types = ["Multiple Choice", "Short Answer", "Fill-in-the-Blank", "True/False"]
        ttk.OptionMenu(
            self.question_frame,
            self.question_type_var,
            "Multiple Choice",
            *question_types,
            command=self.update_question_widgets
        ).grid(row=0, column=1, pady=5)

        self.update_question_widgets()

    def update_question_widgets(self, *args):
        """Update the UI to show relevant fields based on the question type."""
        question_type = self.question_type_var.get()
        for widget in self.question_frame.winfo_children()[2:]:
            widget.destroy()

        tk.Label(
            self.question_frame,
            text="Question:",
            font=("Helvetica", 12),
            bg="#F4F4F4"
        ).grid(row=1, column=0, pady=5, sticky="e")

        self.question_entry = ttk.Entry(self.question_frame, width=40)
        self.question_entry.grid(row=1, column=1, pady=5)

        if question_type == "Multiple Choice":
            self.options_entries = []
            for i in range(4):
                tk.Label(
                    self.question_frame,
                    text=f"Option {i + 1}:",
                    font=("Helvetica", 12),
                    bg="#F4F4F4"
                ).grid(row=2 + i, column=0, pady=5, sticky="e")

                option_entry = ttk.Entry(self.question_frame, width=30)
                option_entry.grid(row=2 + i, column=1, pady=5)
                self.options_entries.append(option_entry)

            tk.Label(
                self.question_frame,
                text="Correct Answer:",
                font=("Helvetica", 12),
                bg="#F4F4F4"
            ).grid(row=6, column=0, pady=5, sticky="e")

            self.correct_answer_entry = ttk.Entry(self.question_frame, width=30)
            self.correct_answer_entry.grid(row=6, column=1, pady=5)

    def add_question(self):
        """Add the current question to the quiz."""
        question_type = self.question_type_var.get()
        question_text = self.question_entry.get()

        if question_type == "Multiple Choice":
            options = [entry.get() for entry in self.options_entries]
            correct_answer = self.correct_answer_entry.get()
            if not question_text or not all(options) or not correct_answer:
                messagebox.showerror("Error", "Please fill in all fields.")
                return

            question = {
                "type": question_type,
                "question": question_text,
                "options": options,
                "correct_answer": correct_answer,
            }
        else:
            # Handle other types of questions (e.g., Short Answer, True/False)
            correct_answer = self.correct_answer_entry.get() if question_type != "True/False" else None
            if not question_text or (question_type != "True/False" and not correct_answer):
                messagebox.showerror("Error", "Please fill in all fields.")
                return

            question = {
                "type": question_type,
                "question": question_text,
                "correct_answer": correct_answer,
            }

        self.question_data.append(question)
        self.clear_question_form()
        messagebox.showinfo("Success", "Question added successfully!")

    def clear_question_form(self):
        """Clear the question form after adding a question."""
        self.question_entry.delete(0, tk.END)
        if self.question_type_var.get() == "Multiple Choice":
            for entry in self.options_entries:
                entry.delete(0, tk.END)
            self.correct_answer_entry.delete(0, tk.END)

    def save_quiz(self):
        """Save the created quiz."""
        quiz_title = self.quiz_title_entry.get()
        if not quiz_title or not self.question_data:
            messagebox.showerror("Error", "Please provide a title and add at least one question.")
            return

        self.quizzes[quiz_title] = self.question_data
        self.question_data = []  # Clear questions for the next quiz
        self.save_data()
        messagebox.showinfo("Success", f"Quiz '{quiz_title}' saved successfully!")
        self.create_homepage()

    def select_quiz(self):
        """Select a quiz to take."""
        self.clear_frame()
        self.main_frame = tk.Frame(self.root, bg="#F4F4F4")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            self.main_frame,
            text="Select a Quiz to Take:",
            font=("Helvetica", 16),
            bg="#F4F4F4",
        ).pack(pady=20)

        if not self.quizzes:
            tk.Label(
                self.main_frame,
                text="No quizzes available. Create a quiz first!",
                font=("Helvetica", 14),
                bg="#F4F4F4",
            ).pack(pady=20)
            ttk.Button(self.main_frame, text="Back", command=self.create_homepage).pack(pady=10)
            return

        for quiz_title in self.quizzes.keys():
            ttk.Button(
                self.main_frame,
                text=quiz_title,
                command=lambda title=quiz_title: self.start_quiz(title),
            ).pack(pady=10)

    def start_quiz(self, quiz_title):
        """Start a quiz."""
        self.current_quiz = self.quizzes[quiz_title]
        self.current_question_index = 0
        self.score = 0
        self.remaining_time = self.time_limit  # Set timer based on the time limit
        self.start_timer()
        self.show_question()

    def start_timer(self):
        """Start the quiz timer."""
        if self.timer_thread:
            self.timer_thread.join()

        def timer():
            while self.remaining_time > 0:
                self.remaining_time -= 1
                self.update_timer_display()
                self.root.update()
                threading.Event().wait(1)
            else:
                self.end_quiz()

        self.timer_thread = threading.Thread(target=timer, daemon=True)
        self.timer_thread.start()

    def update_timer_display(self):
        """Update the timer display."""
        minutes, seconds = divmod(self.remaining_time, 60)
        timer_text = f"Time Remaining: {minutes:02}:{seconds:02}"
        if hasattr(self, 'timer_label'):
            self.timer_label.config(text=timer_text)

    def show_question(self):
        """Display the current question."""
        if self.current_question_index >= len(self.current_quiz):
            self.end_quiz()
            return

        self.clear_frame()
        question = self.current_quiz[self.current_question_index]

        self.timer_label = tk.Label(
            self.root,
            text="",
            font=("Helvetica", 12),
            bg="#F4F4F4",
        )
        self.timer_label.pack(pady=10)

        tk.Label(
            self.root,
            text=f"Question {self.current_question_index + 1}: {question['question']}",
            font=("Helvetica", 14),
            bg="#F4F4F4",
        ).pack(pady=20)

        self.answer_var = tk.StringVar()

        # Show question based on type
        if question["type"] == "Multiple Choice":
            for option in question["options"]:
                tk.Radiobutton(
                    self.root,
                    text=option,
                    variable=self.answer_var,
                    value=option,
                    font=("Helvetica", 12),
                    bg="#F4F4F4",
                ).pack(anchor="w")
        elif question["type"] == "True/False":
            for option in ["True", "False"]:
                tk.Radiobutton(
                    self.root,
                    text=option,
                    variable=self.answer_var,
                    value=option,
                    font=("Helvetica", 12),
                    bg="#F4F4F4",
                ).pack(anchor="w")
        else:
            ttk.Entry(self.root, textvariable=self.answer_var, width=40).pack(pady=10)

        ttk.Button(self.root, text="Submit Answer", command=self.submit_answer).pack(pady=20)

    def submit_answer(self):
        """Submit the user's answer and proceed to the next question."""
        if self.current_question_index < len(self.current_quiz):
            question = self.current_quiz[self.current_question_index]
            user_answer = self.answer_var.get().strip()

            # Validate answer
            if question["type"] in ["Short Answer", "Fill-in-the-Blank", "True/False"]:
                if user_answer.lower() == question["correct_answer"].lower():
                    self.score += 1
            elif question["type"] == "Multiple Choice":
                if user_answer == question["correct_answer"]:
                    self.score += 1

            self.current_question_index += 1
            if self.current_question_index < len(self.current_quiz):
                self.show_question()
            else:
                self.end_quiz()
        else:
            self.end_quiz()

    def end_quiz(self):
        """Display the final score and reset."""
        if self.timer_thread:
            self.timer_thread.join()

        messagebox.showinfo(
            "Quiz Completed",
            f"You scored {self.score} out of {len(self.current_quiz)}!",
        )
        self.create_homepage()

    def save_data(self):
        """Save quizzes to a file."""
        try:
            with open("quizzes.json", "w") as file:
                json.dump(self.quizzes, file)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving data: {e}")

    def load_data(self):
        """Load quizzes from a file."""
        try:
            with open("quizzes.json", "r") as file:
                self.quizzes = json.load(file)
        except FileNotFoundError:
            self.quizzes = {}
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading data: {e}")

    def clear_frame(self):
        """Clear all widgets from the current frame."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def on_closing(self):
        """Handle the app closing event."""
        self.save_data()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizifyApp(root)
    root.mainloop()