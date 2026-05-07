from datetime import datetime
import os

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATUS_OPTIONS = {"Pending", "In Progress", "Completed"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(BASE_DIR, 'employee_tasks.db')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"
login_manager.login_message = "Please log in to continue."


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    tasks = db.relationship(
        "Task", backref="owner", lazy=True, cascade="all, delete-orphan"
    )


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Basic server-side validation to prevent invalid form submission.
        if not name or len(name) < 2:
            flash("Name must be at least 2 characters long.", "danger")
            return render_template("register.html")
        if not email or "@" not in email:
            flash("Please enter a valid email address.", "danger")
            return render_template("register.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html")
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists.", "warning")
            return render_template("register.html")

        hashed_password = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        login_user(user)
        flash("Welcome back! You are logged in.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    # Show only current user's tasks in latest-first order.
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    counts = {
        "Pending": Task.query.filter_by(user_id=current_user.id, status="Pending").count(),
        "In Progress": Task.query.filter_by(
            user_id=current_user.id, status="In Progress"
        ).count(),
        "Completed": Task.query.filter_by(
            user_id=current_user.id, status="Completed"
        ).count(),
    }

    return render_template(
        "dashboard.html",
        tasks=tasks,
        counts=counts,
    )


@app.route("/task/add", methods=["GET", "POST"])
@login_required
def add_task():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "Pending")

        if not title or len(title) < 3:
            flash("Task title must be at least 3 characters.", "danger")
            return render_template("task_form.html", form_title="Add Task", task=None)
        if not description or len(description) < 5:
            flash("Description must be at least 5 characters.", "danger")
            return render_template("task_form.html", form_title="Add Task", task=None)
        if status not in STATUS_OPTIONS:
            flash("Invalid task status selected.", "danger")
            return render_template("task_form.html", form_title="Add Task", task=None)

        task = Task(
            title=title,
            description=description,
            status=status,
            user_id=current_user.id,
        )
        db.session.add(task)
        db.session.commit()
        flash("Task added successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("task_form.html", form_title="Add Task", task=None)


@app.route("/task/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id: int):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", task.status)

        if not title or len(title) < 3:
            flash("Task title must be at least 3 characters.", "danger")
            return render_template("task_form.html", form_title="Edit Task", task=task)
        if not description or len(description) < 5:
            flash("Description must be at least 5 characters.", "danger")
            return render_template("task_form.html", form_title="Edit Task", task=task)
        if status not in STATUS_OPTIONS:
            flash("Invalid task status selected.", "danger")
            return render_template("task_form.html", form_title="Edit Task", task=task)

        task.title = title
        task.description = description
        task.status = status
        db.session.commit()

        flash("Task updated successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("task_form.html", form_title="Edit Task", task=task)


@app.route("/task/delete/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id: int):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted successfully.", "info")
    return redirect(url_for("dashboard"))


@app.route("/task/status/<int:task_id>", methods=["POST"])
@login_required
def update_task_status(task_id: int):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    new_status = request.form.get("status", "").strip()
    if new_status not in STATUS_OPTIONS:
        flash("Invalid status update request.", "danger")
        return redirect(url_for("dashboard"))

    task.status = new_status
    db.session.commit()
    flash("Task status updated.", "success")
    return redirect(url_for("dashboard"))


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return render_template("500.html"), 500


def create_database():
    # Create tables if they do not exist yet.
    with app.app_context():
        db.create_all()


# Create tables at startup so it works with Gunicorn on Render.
create_database()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
