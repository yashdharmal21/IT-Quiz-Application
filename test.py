import tkinter as tk
import random
from tkinter import messagebox
import socket
import json
import os
import mysql.connector
import re

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Competition")
        self.root.geometry("500x400")

        self.student_name = tk.StringVar()
        self.student_phone = tk.StringVar()  
        self.college_name = tk.StringVar()
        self.attempts_file = "attempts.txt"  
        self.timer_label = None
        self.time_left = 900  

        # List of colleges
        self.colleges = [
            "KCES’s M.J. College (Autonomous), Jalgaon (G)",
            "KCES’s M.J. College (Autonomous), Jalgaon (PNG)",
            "SES College of Physical Education, Jalgaon, Dist. Jalgaon",
            "Smt. S.M. Agrawal Institute of Management, Chalisgaon, Dist. Jalgaon",
            "A.S.P.M.’s Bapusaheb D.D.Vispute College, of Education, Walwadi. Dhule",
            "I.E.S.’s Iqra College of Education, Jalgaon",
            "L.D.C.B.E.D.T.’s Biyani B.Ed. College, Jamner Road, Bhusawal",
            "NPS College of Education, Amalner",
            "S.S.B.T.’s Art’s, Commerce and Science College Bambhori, Jalgaon",
            "S.S.P.M.’s Vasantrao Naik Art’s Science and Commerce College, Shahada, Dist-Nandurbar",
            "V.W.S’s Dr. M.Y.Vaidya Art’s, Prof. P.D.Dalal Commerce and Dr. D.S.Shah Science College, Dhule",
            "W.E.S.’s Sunderbai Maganlal Biyani Law College, Dhule",
            "GSB-USs M. G. Tele Commerce, C. and B. R. Tele Science, K. Tele Management college, Thalner, Tal. Shirpur, Dist. Dhule",
            "KCEs College of Education & Physical Education, Jalgaon",
            "KCEs Post Graduate College of Science, Arts & Commerce, Jalgaon",
            "NESs Gangamai College of Pharmacy, Nagaon Tal. & Dist. Dhule",
            "NTVSs College of Education, Nandurbar",
            "P.R. High School Society’s, Arts, Commerce & Science College, Dharangaon, Tal-Dharangaon, Dist.-Jalgaon",
            "SESs College of Education, Jalgaon"
        ]

        self.build_start_screen()

    def fetch_questions(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect(('172.20.10.3', 5000))  
            chunks = []
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
            data = b''.join(chunks)
            all_questions = json.loads(data.decode())
            self.questions = random.sample(all_questions, 5)
            random.shuffle(self.questions)
            print("Questions fetched and shuffled successfully.")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server: {e}")
            self.questions = []
        finally:
            client_socket.close()

    def build_start_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Enter Name:").pack(pady=10)
        tk.Entry(self.root, textvariable=self.student_name).pack(pady=5)
        tk.Label(self.root, text="Select College Name:").pack(pady=10)

        college_dropdown = tk.OptionMenu(self.root, self.college_name, *self.colleges)
        college_dropdown.pack(pady=5)

        tk.Label(self.root, text="Or Enter College Name:").pack(pady=10)
        tk.Entry(self.root, textvariable=self.college_name).pack(pady=5)

        tk.Label(self.root, text="Enter Phone Number:").pack(pady=10)
        tk.Entry(self.root, textvariable=self.student_phone).pack(pady=5)

        tk.Button(self.root, text="Start Quiz", command=self.check_phone).pack(pady=20)

    def check_phone(self):
        phone_number = self.student_phone.get()
        if self.is_valid_phone(phone_number):
            self.check_attempt()
        else:
            messagebox.showwarning("Invalid Phone Number", "Your Phone Number is not valid!")

    def is_valid_phone(self, phone):
        return re.match(r'^[0-9]{10}$', phone) is not None

    def check_attempt(self):
        phone_number = self.student_phone.get()
        connection = None
        try:
            connection = mysql.connector.connect(
                host="172.20.10.3",
                user="akshay",
                password="2121",
                database="quiz_event"
            )
            cursor = connection.cursor()
            sql = "SELECT COUNT(*) FROM students123 WHERE phone_number = %s"
            cursor.execute(sql, (phone_number,))
            result = cursor.fetchone()
            if result[0] > 0:
                messagebox.showwarning("Already Attempted", "You have already attempted the quiz!")
                return
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            return
        finally:
            if connection is not None and connection.is_connected():
                cursor.close()
                connection.close()
        
        self.start_quiz()

    def start_quiz(self):
        if self.student_name.get() and self.student_phone.get() and self.college_name.get():
            self.fetch_questions()
            if not self.questions:
                messagebox.showerror("No Questions", "No questions available for the quiz.")
                return

            self.current_question = 0
            self.score = 0
            self.start_timer()
            self.display_question()
        else:
            messagebox.showwarning("Input Error", "Please enter all required fields (Name, College, and Phone Number)")

    def start_timer(self):
        self.timer_label = tk.Label(self.root, text="Time left: 15:00", font=("Helvetica", 12))
        self.timer_label.pack(pady=5)
        self.update_timer()

    def update_timer(self):
        if self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            time_str = f"Time left: {mins:02}:{secs:02}"
            self.timer_label.config(text=time_str)
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        else:
            self.auto_submit()

    def auto_submit(self):
        messagebox.showinfo("Time's Up", "Time is up! The quiz will be submitted automatically.")
        self.show_result()

    def display_question(self):
        self.clear_screen()
        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]
            question_num = self.current_question + 1
            tk.Label(self.root, text=f"Question {question_num}: {q['question']}").pack(pady=10)

            self.var = tk.StringVar()
            for option in q['options']:
                tk.Radiobutton(self.root, text=option, variable=self.var, value=option).pack(pady=5)

            tk.Button(self.root, text="Next", command=self.next_question).pack(pady=20)
        else:
            self.show_result()

    def next_question(self):
        selected_answer = str(self.var.get()).strip().lower()
        if selected_answer == "":
            messagebox.showwarning("Select an Answer", "Please select an answer before proceeding!")
            return

        correct_answer = str(self.questions[self.current_question]['answer']).strip().lower()
        if selected_answer == correct_answer:
            self.score += 1

        self.current_question += 1
        self.display_question()

    def show_result(self):
        self.clear_screen()
        tk.Label(self.root, text="Quiz Over!").pack(pady=10)
        tk.Label(self.root, text=f"Your Score: {self.score} / {len(self.questions)}").pack(pady=10)

        self.save_score()

        tk.Button(self.root, text="Exit", command=self.root.quit).pack(pady=20)

    def save_score(self):
        connection = None
        try:
            connection = mysql.connector.connect(
                host="172.20.10.3",
                user="akshay",
                password="2121",
                database="quiz_event"
            )
            cursor = connection.cursor()
            sql = "INSERT INTO students123 (student_name, phone_number, Std_score, college_name) VALUES (%s, %s, %s, %s)"
            values = (self.student_name.get(), self.student_phone.get(), self.score, self.college_name.get())
            cursor.execute(sql, values)
            connection.commit()
            messagebox.showinfo("Success", "Score saved successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            if connection is not None and connection.is_connected():
                cursor.close()
                connection.close()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
