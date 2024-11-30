import tkinter as tk
from tkinter import messagebox, ttk
import json

class QuizifyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quizify - Create and Take Quizzes")
        self.root.geometry("800x600")
        self.root.config(bg="#F4F4F4")

        self.quizzes = {}
        self.current_quiz = None
        self.correct_answers = 0
        self.wrong_answers = 0
        self.time_limit = 300  # Default time limit (5 minutes)
        self.student_details = {}
        self.user_type = None  # Track whether the user is a "Student" or "Teacher"

        self.create_initial_screen()
        self.load_data()

        # Handle app closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_initial_screen(self):
        """Create the initial screen to select user type."""
        self.main_frame = tk.Frame(self.root, bg="#F4F4F4")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame on the screen

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

        student_button = ttk.Button(self.main_frame, text="Student", command=lambda: self.set_user_type("Student"))
        student_button.pack(pady=10)

        teacher_button = ttk.Button(self.main_frame, text="Teacher", command=lambda: self.set_user_type("Teacher"))
        teacher_button.pack(pady=10)

    def set_user_type(self, user_type):
        """Set the user type and navigate to the main homepage."""
        self.user_type = user_type
        self.clear_frame()
        self.create_homepage()

    def create_homepage(self):
        """Create the homepage layout with conditional Student ID field."""
        self.main_frame = tk.Frame(self.root, bg="#F4F4F4")
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        tk.Label(
            self.main_frame,
            text=f"Welcome, {self.user_type}!",
            font=("Helvetica", 24, "bold"),
            bg="#F4F4F4",
            fg="#4A90E2"
        ).grid(row=0, column=0, columnspan=2, pady=20)

        tk.Label(self.main_frame, text="First Name:", font=("Helvetica", 12), bg="#F4F4F4").grid(row=1, column=0, pady=10, sticky="e")
        self.first_name_entry = ttk.Entry(self.main_frame, width=30)
        self.first_name_entry.grid(row=1, column=1, pady=10, sticky="w")

        tk.Label(self.main_frame, text="Last Name:", font=("Helvetica", 12), bg="#F4F4F4").grid(row=2, column=0, pady=10, sticky="e")
        self.last_name_entry = ttk.Entry(self.main_frame, width=30)
        self.last_name_entry.grid(row=2, column=1, pady=10, sticky="w")

        if self.user_type == "Student":
            tk.Label(self.main_frame, text="Student ID:", font=("Helvetica", 12), bg="#F4F4F4").grid(row=3, column=0, pady=10, sticky="e")
            self.student_id_entry = ttk.Entry(self.main_frame, width=30)
            self.student_id_entry.grid(row=3, column=1, pady=10, sticky="w")

        tk.Label(self.main_frame, text="Section:", font=("Helvetica", 12), bg="#F4F4F4").grid(row=4, column=0, pady=10, sticky="e")
        self.section_entry = ttk.Entry(self.main_frame, width=30)
        self.section_entry.grid(row=4, column=1, pady=10, sticky="w")

        tk.Label(self.main_frame, text="Time Limit (seconds):", font=("Helvetica", 12), bg="#F4F4F4").grid(row=5, column=0, pady=10, sticky="e")
        self.time_limit_var = tk.StringVar(value=str(self.time_limit))
        self.time_limit_entry = ttk.Entry(self.main_frame, textvariable=self.time_limit_var, width=10)
        self.time_limit_entry.grid(row=5, column=1, pady=10, sticky="w")

        self.create_button("Create Quiz", self.create_quiz).grid(row=6, column=0, pady=15)
        self.create_button("Take Quiz", self.select_quiz).grid(row=6, column=1, pady=15)
        self.create_button("Save & Exit", self.save_data).grid(row=7, column=0, columnspan=2, pady=20)

    def create_button(self, text, command):
        """Create a consistent button style."""
        return ttk.Button(self.main_frame, text=text, width=30, command=command)

    def clear_frame(self):
        """Clear the frame to make space for new widgets."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_quiz(self):
        """Create the quiz creation form for the teacher."""
        self.clear_frame()

        tk.Label(self.main_frame, text="Enter Quiz Title:", font=("Helvetica", 14), bg="#F4F4F4").grid(row=0, column=0, pady=10, sticky="e")
        self.quiz_title_entry = ttk.Entry(self.main_frame, width=30)
        self.quiz_title_entry.grid(row=0, column=1, pady=10)

        self.question_frame = tk.Frame(self.main_frame, bg="#F4F4F4")
        self.question_frame.grid(row=1, column=0, columnspan=2, pady=10)

        self.create_question_widgets()

        self.create_button("Save Quiz", self.save_quiz).grid(row=2, column=0, columnspan=2, pady=20)

    def create_question_widgets(self):
        """Create widgets for adding questions to the quiz."""
        self.question_entries = []

        tk.Label(self.question_frame, text="Question:", font=("Helvetica", 12), bg="#F4F4F4").grid(row=0, column=0, pady=10, sticky="e")
        self.question_entry = ttk.Entry(self.question_frame, width=40)
        self.question_entry.grid(row=0, column=1, pady=10)

        self.options_entries = []
        for i in range(4):  # 4 options per question
            tk.Label(self.question_frame, text=f"Option {i+1}:", font=("Helvetica", 12), bg="#F4F4F4").grid(row=i+1, column=0, pady=5, sticky="e")
            option_entry = ttk.Entry(self.question_frame, width=40)
            option_entry.grid(row=i+1, column=1, pady=5)
            self.options_entries.append(option_entry)

        tk.Label(self.question_frame, text="Correct Option Number:", font=("Helvetica", 12), bg="#F4F4F4").grid(row=5, column=0, pady=10, sticky="e")
        self.correct_option_entry = ttk.Entry(self.question_frame, width=10)
        self.correct_option_entry.grid(row=5, column=1, pady=10)

    def save_quiz(self):
        """Save the quiz data."""
        quiz_title = self.quiz_title_entry.get().strip()
        if not quiz_title:
            messagebox.showerror("Error", "Quiz title is required!")
            return

        questions = []
        for i in range(len(self.question_entries)):
            question = self.question_entries[i].get().strip()
            options = [entry.get().strip() for entry in self.options_entries[i]]
            correct_option = self.correct_option_entry.get().strip()

            if not question or any(not option for option in options):
                messagebox.showerror("Error", "All question fields must be filled!")
                return

            questions.append({
                "question": question,
                "options": options,
                "correct_option": correct_option
            })

        self.quizzes[quiz_title] = questions
        messagebox.showinfo("Quiz Created", f"Quiz '{quiz_title}' created successfully!")
        self.create_homepage()

    def select_quiz(self):
        """Placeholder for quiz selection."""
        messagebox.showinfo("Feature Coming Soon", "Take Quiz functionality is not implemented yet!")

    def save_data(self):
        """Save quizzes to a file."""
        try:
            with open("quizzes.json", "w") as file:
                json.dump(self.quizzes, file)
            messagebox.showinfo("Save Successful", "Data has been saved successfully!")
        except Exception as e:
            messagebox.showerror("Save Failed", f"Error saving data: {e}")
        self.root.quit()

    def load_data(self):
        """Load quizzes from a file."""
        try:
            with open("quizzes.json", "r") as file:
                self.quizzes = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def on_closing(self):
        """Handle app closing."""
        self.save_data()

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizifyApp(root)
    root.mainloop()
