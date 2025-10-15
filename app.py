from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import socket
import json
import mysql.connector
import re
import webbrowser
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    student1_name = request.form['student1_name']
    student1_phone = request.form['student1_phone']
    student2_name = request.form['student2_name']
    student2_phone = request.form['student2_phone']
    college_name = request.form['college_name']

    # Validate inputs
    if not (student1_name and student1_phone and student2_name and student2_phone and college_name):
        flash("Please fill in all fields.")
        return redirect(url_for('index'))

    # Validate phone numbers
    if not re.match(r'^[0-9]{10}$', student1_phone) or not re.match(r'^[0-9]{10}$', student2_phone):
        flash("Invalid phone number for one or both team members!")
        return redirect(url_for('index'))

    # Check if any student has already attempted the quiz
    if check_attempt(student1_phone) or check_attempt(student2_phone):
        flash("One or both team members have already attempted the quiz!")
        return redirect(url_for('index'))

    # Fetch questions
    questions = fetch_questions()
    if not questions:
        flash("No questions available.")
        return redirect(url_for('index'))

    # Store team information and quiz details in session
    session['team'] = {
        'student1_name': student1_name,
        'student1_phone': student1_phone,
        'student2_name': student2_name,
        'student2_phone': student2_phone,
        'college_name': college_name
    }
    session['questions'] = questions
    session['current_question'] = 0
    session['score'] = 0
    session['time_left'] = 900  # 15 minutes

    return redirect(url_for('quiz'))


@app.route('/quiz')
def quiz():
    if 'questions' not in session:
        return redirect(url_for('index'))
    
    question = session['questions'][session['current_question']]
    return render_template('quiz.html', question=question, question_num=session['current_question'] + 1)

@app.route('/next_question', methods=['POST'])
def next_question():
    selected_answer = request.form['answer']
    correct_answer = session['questions'][session['current_question']]['answer']

    if selected_answer.lower() == correct_answer.lower():
        session['score'] += 1

    session['current_question'] += 1

    if session['current_question'] < len(session['questions']):
        return redirect(url_for('quiz'))
    else:
        save_score(session['team'], session['score'])  # Pass the whole team data
        return redirect(url_for('result'))

@app.route('/result')
def result():
    score = session.get('score', 0)
    return render_template('result.html', score=score)

def fetch_questions():
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
        return random.sample(all_questions, 25)
    except Exception as e:
        print(f"Error fetching questions: {e}")
        return []
    finally:
        client_socket.close()

def check_attempt(phone_number):
    connection = mysql.connector.connect(
        host="172.20.10.3",
        user="root",
        password="",
        database="quiz_event"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Student_record WHERE student1_phone = %s OR student2_phone = %s", (phone_number, phone_number))
    result = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return result > 0

def save_score(team, score):
    connection = mysql.connector.connect(
        host="172.20.10.3",
        user="root",
        password="",
        database="quiz_event"
    )
    cursor = connection.cursor()

    # Save score for both team members in the new table schema
    cursor.execute("INSERT INTO Student_record (student1_name, student1_phone, student2_name, student2_phone, std_score, collage_name) VALUES (%s, %s, %s, %s, %s, %s)",
                   (team['student1_name'], team['student1_phone'], team['student2_name'], team['student2_phone'], score, team['college_name']))

    connection.commit()
    cursor.close()
    connection.close()

if __name__ == '__main__':
    # Start the Flask app on port 5001 to avoid macOS port 5000 conflicts
    app.run(host='127.0.0.1', port=5001, debug=False)

    # Open the default web browser after a short delay
    time.sleep(1)
    webbrowser.open('http://127.0.0.1:5001')
