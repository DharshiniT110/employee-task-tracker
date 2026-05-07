# Employee Task Tracker

This is a simple web application made using Flask and SQLite.
It helps a user register, login, and manage daily tasks.

The project is beginner-friendly and suitable for a student portfolio.

## Features

- User registration
- Login and logout
- Add task
- Edit task
- Delete task
- Update task status
- Flash messages
- Basic form validation
- Simple responsive Bootstrap UI

## Task Status Options

- Pending
- In Progress
- Completed

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- SQLite
- Bootstrap 5

## Project Structure

```text
employee-task-tracker/
├── app.py
├── requirements.txt
├── README.md
├── static/
│   └── styles.css
└── templates/
    ├── base.html
    ├── home.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── task_form.html
    ├── 404.html
    └── 500.html
```

## Database Tables

### Users

- id
- name
- email
- password

### Tasks

- id
- title
- description
- status
- created_at
- user_id

## How to Run

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python app.py
```

4. Open in browser:
   [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Sample Screenshots

Create a folder named `screenshots` and add images like:

- `screenshots/home.png`
- `screenshots/login.png`
- `screenshots/dashboard.png`
- `screenshots/task-form.png`

Example markdown:

```md
![Home](screenshots/home.png)
![Dashboard](screenshots/dashboard.png)
```
