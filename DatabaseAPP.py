import sqlite3

class QuizifyDatabase:
    def __init__(self, db_name='quizify.db'):
        # Connect to the SQLite database (or create it if it doesn't exist)
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        """Create tables for quizzes, questions, and options if they don't exist."""
        # Create quizzes table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL
        )''')

        # Create questions table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            question TEXT NOT NULL,
            correct_option INTEGER,
            FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
        )''')

        # Create options table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER,
            option_text TEXT NOT NULL,
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )''')

        self.conn.commit()

    def save_quiz(self, title, questions):
        """Save a new quiz to the database."""
        # Insert the quiz title
        self.cursor.execute('INSERT INTO quizzes (title) VALUES (?)', (title,))
        quiz_id = self.cursor.lastrowid

        for question_data in questions:
            question_text = question_data['question']
            correct_option = question_data['correct_option']

            # Insert the question
            self.cursor.execute('''
            INSERT INTO questions (quiz_id, question, correct_option)
            VALUES (?, ?, ?)
            ''', (quiz_id, question_text, correct_option))
            question_id = self.cursor.lastrowid

            # Insert the options for this question
            for option in question_data['options']:
                self.cursor.execute('''
                INSERT INTO options (question_id, option_text)
                VALUES (?, ?)
                ''', (question_id, option))

        self.conn.commit()

    def get_all_quizzes(self):
        """Get a list of all quizzes."""
        self.cursor.execute('SELECT id, title FROM quizzes')
        quizzes = self.cursor.fetchall()
        return quizzes

    def get_quiz_by_id(self, quiz_id):
        """Get a quiz and its questions by quiz ID."""
        # Get quiz title
        self.cursor.execute('SELECT title FROM quizzes WHERE id = ?', (quiz_id,))
        quiz = self.cursor.fetchone()
        if not quiz:
            return None

        quiz_title = quiz[0]

        # Get questions for this quiz
        self.cursor.execute('SELECT id, question, correct_option FROM questions WHERE quiz_id = ?', (quiz_id,))
        questions = self.cursor.fetchall()

        quiz_data = {'title': quiz_title, 'questions': []}
        for question in questions:
            question_id, question_text, correct_option = question
            self.cursor.execute('SELECT option_text FROM options WHERE question_id = ?', (question_id,))
            options = [row[0] for row in self.cursor.fetchall()]
            quiz_data['questions'].append({
                'question': question_text,
                'options': options,
                'correct_option': correct_option
            })

        return quiz_data

    def delete_quiz(self, quiz_id):
        """Delete a quiz and its associated data."""
        self.cursor.execute('DELETE FROM options WHERE question_id IN (SELECT id FROM questions WHERE quiz_id = ?)', (quiz_id,))
        self.cursor.execute('DELETE FROM questions WHERE quiz_id = ?', (quiz_id,))
        self.cursor.execute('DELETE FROM quizzes WHERE id = ?', (quiz_id,))
        self.conn.commit()

    def close(self):
        """Close the database connection."""
        self.conn.close()


# Example usage:
if __name__ == "__main__":
    db = QuizifyDatabase()

    # Save a quiz
    quiz_title = "Science Quiz"
    questions = [
        {
            'question': 'What is the chemical symbol for water?',
            'options': ['H2O', 'CO2', 'O2', 'H2'],
            'correct_option': 1
        },
        {
            'question': 'What planet is known as the Red Planet?',
            'options': ['Earth', 'Mars', 'Jupiter', 'Venus'],
            'correct_option': 2
        }
    ]
    db.save_quiz(quiz_title, questions)

    # Get all quizzes
    quizzes = db.get_all_quizzes()
    print("Quizzes:", quizzes)

    # Get a specific quiz by ID
    quiz_data = db.get_quiz_by_id(quizzes[0][0])  # Get the first quiz
    print("Quiz Data:", quiz_data)

    # Close the database
    db.close()
