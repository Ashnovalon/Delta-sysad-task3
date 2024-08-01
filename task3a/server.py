import mysql.connector
import hashlib
import socket
import threading

db_config = {
    'user': 'user',
    'password': 'password',
    'host': 'db',
    'database': 'quiz_db'
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(64) NOT NULL
);
"""

create_questions_table = """
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT NOT NULL,
    option1 VARCHAR(255) NOT NULL,
    option2 VARCHAR(255) NOT NULL,
    option3 VARCHAR(255) NOT NULL,
    option4 VARCHAR(255) NOT NULL,
    correct_option INT NOT NULL,
    created_by VARCHAR(50),
    FOREIGN KEY (created_by) REFERENCES users(username)
);
"""

create_leaderboard_table = """
CREATE TABLE IF NOT EXISTS leaderboard (
    username VARCHAR(50) PRIMARY KEY,
    score INT DEFAULT 0,
    FOREIGN KEY (username) REFERENCES users(username)
);
"""


cursor.execute(create_users_table)
cursor.execute(create_questions_table)
cursor.execute(create_leaderboard_table)

conn.commit()

print("Database schema created successfully.")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(stored_password, provided_password):
    return stored_password == hashlib.sha256(provided_password.encode()).hexdigest()

def authenticate(client_socket):
    while True:
        client_socket.send("1. Login\n2. Register\nChoose an option: ".encode())
        option = client_socket.recv(1024).decode().strip()
        
        if option == '1':
            client_socket.send("Enter username: ".encode())
            username = client_socket.recv(1024).decode().strip()
            client_socket.send("Enter password: ".encode())
            password = client_socket.recv(1024).decode().strip()
            
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            if result and check_password(result[0], password):
                client_socket.send("Login successful!\n".encode())
                return username
            else:
                client_socket.send("Invalid username or password. Try again.\n".encode())
                
        elif option == '2':
            client_socket.send("Enter new username: ".encode())
            username = client_socket.recv(1024).decode().strip()
            client_socket.send("Enter new password: ".encode())
            password = client_socket.recv(1024).decode().strip()
            
            hashed_password = hash_password(password)
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
                conn.commit()
                client_socket.send("Registration successful! You can now login.\n".encode())
            except mysql.connector.errors.IntegrityError:
                client_socket.send("Username already exists. Try again.\n".encode())
        else:
            client_socket.send("Invalid option. Try again.\n".encode())

def client_thread(client_socket, addr):
    client_socket.send("Welcome to the Quiz Server.\n".encode())
    username = authenticate(client_socket)
    if not username:
        client_socket.send("Authentication failed. Disconnecting...\n".encode())
        client_socket.close()
        return

    while True:
        try:
            menu = "1. Add Question\n2. Answer Question\n3. View Leaderboard\n4. Exit\nChoose an option: "
            client_socket.send(menu.encode())
            option = client_socket.recv(1024).decode().strip()

            if option == '1':
                add_question(client_socket, username)
            elif option == '2':
                answer_question(client_socket, username)
            elif option == '3':
                view_leaderboard(client_socket)
            elif option == '4':
                client_socket.send("Goodbye!\n".encode())
                break
            else:
                client_socket.send("Invalid option. Try again.\n".encode())
        except:
            break

    client_socket.close()

def add_question(client_socket, username):
    try:
        client_socket.send("Enter the question: ".encode())
        question = client_socket.recv(1024).decode().strip()

        client_socket.send("Enter option 1: ".encode())
        option1 = client_socket.recv(1024).decode().strip()

        client_socket.send("Enter option 2: ".encode())
        option2 = client_socket.recv(1024).decode().strip()

        client_socket.send("Enter option 3: ".encode())
        option3 = client_socket.recv(1024).decode().strip()

        client_socket.send("Enter option 4: ".encode())
        option4 = client_socket.recv(1024).decode().strip()

        client_socket.send("Enter the correct option number (1-4): ".encode())
        correct_option = int(client_socket.recv(1024).decode().strip())

        cursor.execute('''INSERT INTO questions (question, option1, option2, option3, option4, correct_option, created_by)
                          VALUES (%s, %s, %s, %s, %s, %s, %s)''', 
                          (question, option1, option2, option3, option4, correct_option, username))
        conn.commit()
        client_socket.send("Question added successfully!\n".encode())
    except Exception as e:
        client_socket.send(f"Error: {str(e)}\n".encode())

def answer_question(client_socket, username):
    try:
        cursor.execute("SELECT * FROM questions")
        questions = cursor.fetchall()

        if not questions:
            client_socket.send("No questions available.\n".encode())
            return

        for question in questions:
            q_id, q_text, op1, op2, op3, op4, correct_option, created_by = question
            question_text = f"{q_text}\n1. {op1}\n2. {op2}\n3. {op3}\n4. {op4}\nYour answer: "
            client_socket.send(question_text.encode())
            answer = int(client_socket.recv(1024).decode().strip())

            if answer == correct_option:
                client_socket.send("Correct!\n".encode())
                cursor.execute("INSERT IGNORE INTO leaderboard (username, score) VALUES (%s, 0)", (username,))
                cursor.execute("UPDATE leaderboard SET score = score + 1 WHERE username = %s", (username,))
                conn.commit()
            else:
                client_socket.send("Wrong!\n".encode())
    except Exception as e:
        client_socket.send(f"Error: {str(e)}\n".encode())

def view_leaderboard(client_socket):
    cursor.execute("SELECT * FROM leaderboard ORDER BY score DESC")
    leaderboard = cursor.fetchall()
    leaderboard_text = "Leaderboard:\n"
    for user in leaderboard:
        leaderboard_text += f"{user[0]}: {user[1]} points\n"
    client_socket.send(leaderboard_text.encode())


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 12345))
server_socket.listen(5)
print("Server is listening on port 12345")

while True:
	client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        threading.Thread(target=client_thread, args=(client_socket, addr)).start()


        
