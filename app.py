from flask import Flask,render_template, request, redirect, session, flash, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from services.gemini_services import generate_study_notes, clean_content, answer_doubt, generate_notes_from_pdf, generate_quiz
from services.pdf_service import extract_text_from_pdf
from models import User,db,Note,Task,Activity
from config import Config
from datetime import datetime,timedelta
import markdown, bleach
import json

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
with app.app_context():
    db.create_all()

def user_activity(user_id,activity):
    activity = Activity(
        user_id=user_id,
        action=activity
    )
    db.session.add(activity)
    db.session.commit()

#Home
@app.route("/")
def index():
    return render_template('index.html')

#Register
@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash("All fields are required!", "warning")
            return redirect(url_for("index"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists!", "error")
            return redirect(url_for("index"))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registeration Successful! Please Login.", "success")
        return redirect(url_for("index"))

#Login
@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            user.last_activity = datetime.now()
            db.session.commit()
            flash("Login Successfull.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password!", "error")
            return redirect(url_for("index"))

#Dashboard
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please Login First!", "warning")
        return redirect(url_for("index"))

    user = User.query.get(session["user_id"])
    notes_count = Note.query.filter_by(user_id=session['user_id']).count()
    quiz_count = user.quiz_count
    study_hours = round((user.study_time / 3600),2)
    activities = Activity.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Activity.timestamp.desc()).limit(10).all()

    for act in activities:
        act.local_time = act.timestamp + timedelta(hours=5,minutes=30)

    return render_template("dashboard.html",
     username=session["username"],
     notes_count=notes_count,
     quiz_count=quiz_count,
     study_hours=study_hours,
     activities=activities
    )

@app.route("/update_study_time", methods=["POST"])
def update_study_time():
    if "user_id" not in session:
        return {"status": "error"}

    user = User.query.get(session["user_id"])
    now = datetime.now()
    if user.last_activity:
        duration = now - user.last_activity
        seconds = int(duration.total_seconds())
    
        if 0 < seconds < 300:
            user.study_time += seconds
    
    user.last_activity = now
    db.session.commit()

    return {"status": "success"}

#Logout
@app.route("/logout")
def logout():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        now = datetime.now()

        if user.last_activity:
            duration = now - user.last_activity
            seconds = int(duration.total_seconds())
            
            if 0 < seconds < 300:
                user.study_time += seconds
        
        user.last_activity = None
        db.session.commit()

    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

#Generate Notes
@app.route("/generate_notes", methods=["GET","POST"])
def generate_notes():
    if "user_id" not in session:
        flash("Please Login First!", "warning")
        return redirect(url_for("index"))
    
    raw_markdown_notes = None
    clean_ai_notes = None
    topic = None

    if request.method == "POST":
        action = request.form.get("action")
        if action == "generate":
            topic = request.form.get("topic","").strip()
            if topic:
                try:
                    raw_markdown_notes = generate_study_notes(topic)
                    ai_notes = markdown.markdown(
                        raw_markdown_notes,
                        extensions=["extra", "codehilite", "fenced_code"]
                    )
                    clean_ai_notes = clean_content(ai_notes)
                    # print(clean_ai_notes)
                    user_activity(session["user_id"],f"Generated Notes on {topic}")

                except Exception:
                    flash("Error generating notes!", "error")            
            else:
                flash("Topic can't be empty!", "error")
        
        elif action == "save":
            topic = request.form.get("topic")
            content = request.form.get("raw_markdown_notes")
            new_note = Note(
                title=topic,
                content=content,
                user_id=session["user_id"]
            )
            db.session.add(new_note)
            db.session.commit()

            flash("Notes Saved Successfully.", "success")
            return redirect(url_for("saved_notes"))

    return render_template(
        "generate_notes.html",
        topic=topic,
        ai_notes=clean_ai_notes,
        raw_markdown_notes = raw_markdown_notes
    )

#Saved Notes
@app.route("/saved_notes")
def saved_notes():
    if "user_id" not in session:
        flash("Please Login First!", "warning")
        return redirect(url_for("index"))
    
    notes = Note.query.filter_by(
        user_id = session["user_id"]
    ).order_by(Note.created_at.desc()).all()
    
    for note in notes:
        note.local_time = note.created_at + timedelta(hours=5,minutes=30)
        content = markdown.markdown(
            note.content,
            extensions=["extra", "codehilite", "fenced_code"]
        )
        note.rendered_content = clean_content(content)

    return render_template("saved_notes.html", notes=notes)

#View Note
@app.route("/note/<int:note_id>")
def view_note(note_id):
    if "user_id" not in session:
        flash("Please Login First!", "warning")
        return redirect(url_for("index"))

    note = Note.query.filter_by(id=note_id, user_id=session["user_id"]).first_or_404()

    content = markdown.markdown(
        note.content,
        extensions=['extra','codehilite','fenced_code']
    )
    note.rendered_content = clean_content(content)
    note.local_time = note.created_at + timedelta(hours=5,minutes=30)
    return render_template("view_note.html", note=note)

#Ask Doubts
@app.route("/ask_doubts", methods=["GET","POST"])
def ask_doubts():
    if "user_id" not in session:
        flash("Please Login First!", "warning")
        return redirect(url_for("index"))
    
    if "chat_history" not in session:
        session["chat_history"] = []
    
    if request.method == "POST":
        question = request.form.get("question")

        if question:
            answer = answer_doubt(question)
            answer_markdown = markdown.markdown(
                answer,
                extensions=["codehilite","extra","fenced_code"]
            )
            clean_answer = clean_content(answer_markdown)
            session["chat_history"].append({
                "question": question,
                "answer": clean_answer
            })
            session.modified = True
            user_activity(session["user_id"], f"Asked Doubt: {question[:30]}...")

    return render_template(
        "ask_doubts.html",
        chat_history = session["chat_history"]
    )

#PDF To Notes
@app.route("/pdf_to_notes", methods=["GET","POST"])
def pdf_to_notes():
    if "user_id" not in session:
        flash("Please Login First!", "warning")
        return redirect(url_for("index"))

    raw_generated_notes = None
    topic = None
    clean_notes = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "generate":
            pdf_file = request.files.get("pdf_file")

            if pdf_file:
                text = extract_text_from_pdf(pdf_file)
                raw_generated_notes = generate_notes_from_pdf(text)
                generated_notes_markdown = markdown.markdown(
                    raw_generated_notes,
                    extensions=["extra","codehilite","fenced_code"]
                )
                clean_notes = clean_content(generated_notes_markdown)
                topic = pdf_file.filename
                user_activity(session["user_id"], f"Uploaded PDF File: {pdf_file.filename}")

        elif action == "save":
            topic = request.form.get("topic")
            content = request.form.get("content")

            new_note = Note(
                title=topic,
                content=content,
                user_id=session["user_id"]
            )
            db.session.add(new_note)
            db.session.commit()

            flash("PDF notes saved successfully!", "success")

            return redirect(url_for("saved_notes"))

    return render_template("pdf_notes.html", generated_notes=clean_notes, topic=topic)

#Generate Quiz
@app.route("/quiz", methods=["GET","POST"])
def quiz():
    if "user_id" not in session:
        flash("Please Login First!", "warning")
        redirect (url_for("index"))

    topic = None
    score = None 

    if request.method == "POST":
        action = request.form.get("action")

        if action == "generate":
            topic = request.form.get("topic")
            raw_quiz = generate_quiz(topic)

            try:
                quiz_data = json.loads(raw_quiz)
                session["quiz_data"] = quiz_data
            except:
                flash("Error generating quiz!", "warning")
        
        elif action == "submit":
            quiz_data = session.get("quiz_data",[])
            score = 0

            for i, q in enumerate(quiz_data):
                user_answer = request.form.get(f"q{i}")
                if user_answer == q["answer"]:
                    score += 1

            user = User.query.get(session['user_id'])
            user.quiz_count += 1
            db.session.commit()
            user_activity(session["user_id"], f"Took a Quiz (Score: {score})")

    return render_template(
        "quiz.html",
        quiz_data=session.get("quiz_data"),
        score=score
    )

@app.route("/study_planner", methods=["GET","POST"])
def study_planner():
    if "user_id" not in session:
        flash("Please Login First!", "warning")
        return redirect(url_for("index"))
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        deadline = request.form.get("deadline")

        deadline_date = None
        if deadline:
            deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
        
        new_task = Task(
            title=title,
            description=description,
            deadline=deadline_date,
            user_id=session["user_id"]
        )
        db.session.add(new_task)
        db.session.commit()

        flash("Task Added Successfully.","success")
        return redirect(url_for("study_planner"))
    
    tasks = Task.query.filter_by(user_id=session["user_id"]).order_by(Task.deadline.asc()).all()
    return render_template("study_planner.html",tasks=tasks)

@app.route("/task_complete/<int:task_id>")
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != session["user_id"]:
        return redirect(url_for("study_planner"))

    task.status = "completed"
    db.session.commit()
    return redirect(url_for("study_planner"))

@app.route("/delete_task/<int:task_id>")
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != session["user_id"]:
        return redirect(url_for("study_planner"))
    
    db.session.delete(task)
    db.session.commit()
    flash("Task Deleted!", "info")

    return redirect(url_for("study_planner"))


if __name__ == "__main__":
    app.run(debug=True)