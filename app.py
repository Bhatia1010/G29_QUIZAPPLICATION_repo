from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from werkzeug.security import check_password_hash
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SECRET_KEY"] = "Welcome"

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "loginFunction"

# User Model
class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String, default="user")

    def generate_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def registerFunction():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            flash("User Already Exists,Please login", "danger")
            return redirect(url_for("loginFunction"))

        user = User(username=username, email=email)
        user.generate_password(password)
        db.session.add(user)
        db.session.commit()

        flash("User Registered Successfully", "success")
        return redirect(url_for("loginFunction"))

    return render_template("signup.html")


@app.route('/login', methods=['GET', 'POST'])
def loginFunction():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        admin = User.query.filter_by(email=email).first()

        # Ensure admin account exists
        if email == "admin@gmail.com":
            login_user(admin)
            flash("admin logged in successfully", "success")
            return render_template("admindashboard.html")
        else:
            login_user(user)
            flash("User logged in successfully", "success")
            return render_template("dashboard.html", user=current_user)
            
    return render_template('login.html')



@app.route("/admindashboard")
@login_required
def admindashboard():
    if current_user.role != "admin":
        flash("Access Denied: Admins Only!", "danger")
        return redirect(url_for("dashboard"))
    return render_template("admin_dashboard.html", user=current_user)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("User logged out successfully", "info")
    return redirect(url_for("home"))

# Database Setup
with app.app_context():
    db.create_all()

    admin = User.query.filter_by(email="admin@gmail.com").first()
    if not admin:
        admin = User(username="admin", email="admin@gmail.com", role="admin")
        admin.generate_password("Admin@123")
        db.session.add(admin)
        db.session.commit()


# Route for displaying questions
@app.route('/ques')
def ques():
    questions = [
        "What is Flask?",
        "How do you set up a Flask route?",
        "What is Jinja templating?",
        "How do you serve static files in Flask?"
    ]
    return render_template('ques.html', questions=questions)

# Route for displaying the quiz
@app.route('/pyquiz')
def pyquizFunction():
    flask_quiz = {
        "questions": [
            {
                "question": "What is Flask in Python?",
                "options": ["A) A front-end framework", "B) A micro web framework", "C) A database management system", "D) A full-stack framework"],
                "answer": "B"
            },
            {
                "question": "Which command is used to install Flask?",
                "options": ["A) pip install flask", "B) install flask", "C) flask install", "D) python install flask"],
                "answer": "A"
            },
            {
                "question": "What is the default port for Flask development server?",
                "options": ["A) 5000", "B) 8080", "C) 8000", "D) 3000"],
                "answer": "A"
            },
            {
                "question": "Which template engine does Flask use by default?",
                "options": ["A) Django Templates", "B) Jinja2", "C) Mako", "D) React"],
                "answer": "B"
            },
            {
                "question": "Which of the following is NOT a built-in Flask extension?",
                "options": ["A) Flask-SQLAlchemy", "B) Flask-Login", "C) Flask-Django", "D) Flask-WTF"],
                "answer": "C"
            },
            {
                "question": "Which function is used to define routes in Flask?",
                "options": ["A) app.route()", "B) route.app()", "C) flask.route()", "D) def.route()"],
                "answer": "A"
            },
            {
                "question": "Which HTTP methods are allowed by default in Flask routes?",
                "options": ["A) GET", "B) POST", "C) GET and POST", "D) All methods"],
                "answer": "A"
            },
            {
                "question": "How do you run a Flask application?",
                "options": ["A) flask run", "B) python app.py", "C) Both A & B", "D) start flask"],
                "answer": "C"
            },
            {
                "question": "What is Flask-SQLAlchemy used for?",
                "options": ["A) Handling HTTP requests", "B) Managing front-end templates", "C) ORM for database interactions", "D) Debugging Flask applications"],
                "answer": "C"
            },
            {
                "question": "What is the purpose of the Flask `flash()` function?",
                "options": ["A) Debugging", "B) Sending messages to users", "C) Logging errors", "D) Running background tasks"],
                "answer": "B"
            }
        ]
    }

    return render_template('pyquiz.html', quiz=flask_quiz)


# Route for handling quiz submission
@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    flask_quiz = {
        "questions": [
            {"question": "What is Flask in Python?", "answer": "B"},
            {"question": "Which command is used to install Flask?", "answer": "A"},
            {"question": "What is the default port for Flask development server?", "answer": "A"},
            {"question": "Which template engine does Flask use by default?", "answer": "B"},
            {"question": "Which of the following is NOT a built-in Flask extension?", "answer": "C"},
            {"question": "Which function is used to define routes in Flask?", "answer": "A"},
            {"question": "Which HTTP methods are allowed by default in Flask routes?", "answer": "A"},
            {"question": "How do you run a Flask application?", "answer": "C"},
            {"question": "What is Flask-SQLAlchemy used for?", "answer": "C"},
            {"question": "What is the purpose of the Flask `flash()` function?", "answer": "B"}
        ]
    }

    score = 0
    total_questions = len(flask_quiz["questions"])
    results = []

    for i, question in enumerate(flask_quiz["questions"], 1):
        user_answer = request.form.get(f"q{i}")
        correct = user_answer == question["answer"]
        if correct:
            score += 1
        results.append({
            "question": question["question"],
            "user_answer": user_answer,
            "correct_answer": question["answer"],
            "correct": correct
        })

    return render_template("results.html", score=score, total=total_questions, results=results)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    selected_answer = request.form.get('answer')
    if selected_answer:
        # Process the answer (e.g., check if it is correct)
        pass
    return redirect(url_for('next_question'))

@app.route('/cppquiz')
def cppquizFunction():
    cpp_quiz = {
        "questions": [
            {
                "question": "What is C++?",
                "options": ["A) A high-level programming language", "B) A low-level programming language", "C) A hardware description language", "D) A markup language"],
                "answer": "A"
            },
            {
                "question": "Which of the following is used to declare a class in C++?",
                "options": ["A) class MyClass {}", "B) MyClass class {}", "C) class = MyClass {}", "D) MyClass {}"],
                "answer": "A"
            },
            {
                "question": "Which of the following is a C++ standard library?",
                "options": ["A) iostream", "B) java.io", "C) stdlib.h", "D) conio.h"],
                "answer": "A"
            },
            {
                "question": "Which operator is used to allocate memory dynamically in C++?",
                "options": ["A) new", "B) malloc", "C) alloc", "D) malloc_new"],
                "answer": "A"
            },
            {
                "question": "Which of the following is NOT a valid C++ access modifier?",
                "options": ["A) public", "B) private", "C) protected", "D) secure"],
                "answer": "D"
            },
            {
                "question": "Which keyword is used to declare a function in C++?",
                "options": ["A) func", "B) function", "C) def", "D) void"],
                "answer": "D"
            },
            {
                "question": "How do you comment a single line in C++?",
                "options": ["A) // This is a comment", "B) /* This is a comment */", "C) -- This is a comment", "D) <!-- This is a comment -->"],
                "answer": "A"
            },
            {
                "question": "What is the size of a `char` data type in C++?",
                "options": ["A) 2 bytes", "B) 1 byte", "C) 4 bytes", "D) 8 bytes"],
                "answer": "B"
            },
            {
                "question": "Which of the following is used to create an object in C++?",
                "options": ["A) object MyClass;", "B) MyClass obj;", "C) MyClass new;", "D) MyClass obj = new();"],
                "answer": "B"
            },
            {
                "question": "Which of the following operators is used to access class members in C++?",
                "options": ["A) .", "B) ->", "C) &", "D) #"],
                "answer": "A"
            }
        ]
    }

    return render_template('cppquiz.html', quiz=cpp_quiz)

@app.route('/submit_cpp_quiz', methods=['POST'])
def submit_cpp_quiz():
    cpp_quiz = {
        "questions": [
            {"question": "What is C++?", "answer": "A"},
            {"question": "Which of the following is used to declare a class in C++?", "answer": "A"},
            {"question": "Which of the following is a C++ standard library?", "answer": "A"},
            {"question": "Which operator is used to allocate memory dynamically in C++?", "answer": "A"},
            {"question": "Which of the following is NOT a valid C++ access modifier?", "answer": "D"},
            {"question": "Which keyword is used to declare a function in C++?", "answer": "D"},
            {"question": "How do you comment a single line in C++?", "answer": "A"},
            {"question": "What is the size of a `char` data type in C++?", "answer": "B"},
            {"question": "Which of the following is used to create an object in C++?", "answer": "B"},
            {"question": "Which of the following operators is used to access class members in C++?", "answer": "A"}
        ]
    }

    score = 0
    total_questions = len(cpp_quiz["questions"])
    results = []

    for i, question in enumerate(cpp_quiz["questions"], 1):
        user_answer = request.form.get(f"q{i}")
        correct = user_answer == question["answer"]
        if correct:
            score += 1
        results.append({
            "question": question["question"],
            "user_answer": user_answer,
            "correct_answer": question["answer"],
            "correct": correct
        })

    return render_template("results.html", score=score, total=total_questions, results=results)

@app.route("/contact_us")
def contact_us():
    return render_template("contactus.html")

@app.route("/about_us")
def about_us():
    return render_template("aboutus.html")

@app.route("/create_quiz", methods=["GET", "POST"])
@login_required
def create_quiz():
    if request.method == "POST":
        quiz_title = request.form.get("quiz_title")
        questions = request.form.getlist("question[]")
        optionsA = request.form.getlist("optionA[]")
        optionsB = request.form.getlist("optionB[]")
        optionsC = request.form.getlist("optionC[]")
        optionsD = request.form.getlist("optionD[]")
        answers = request.form.getlist("answer[]")

        quiz_data = {
            "title": quiz_title,
            "questions": []
        }

        for i in range(len(questions)):
            quiz_data["questions"].append({
                "question": questions[i],
                "options": [optionsA[i], optionsB[i], optionsC[i], optionsD[i]],
                "answer": answers[i]
            })

        # Save quiz data to JSON file (You can change this to database storage)
        with open("quizzes.json", "a") as file:
            json.dump(quiz_data, file)
            file.write("\n")

        flash("Quiz Created Successfully!", "success")
        return redirect(url_for("home"))

    return render_template("create_quiz.html")



if __name__ == '__main__':
    app.run(debug=True)
