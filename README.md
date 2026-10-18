# NoticeHub — Digital Notice Board System

A responsive Python web application built with Flask and SQLite for an experiential learning project.

## Features
- Public notice board for all users
- Administrator login
- Create, update, and delete notices
- Filter notices by category
- Sort notices by newest, oldest, or title
- Search notice titles and content
- Responsive layout for desktop and mobile
- SQLite database created automatically

## Requirements
- Python 3.9 or newer
- pip

## Run the application

1. Extract the project ZIP and open a terminal in the `digital_notice_board` folder.
2. (Optional but recommended) Create and activate a virtual environment:

   Windows:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

   macOS/Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the web app:
   ```bash
   python app.py
   ```

5. Open `http://127.0.0.1:5000` in your browser.

## Demo administrator login
- Username: `admin`
- Password: `admin123`

Select **Admin login** in the navigation bar to sign in. After logging in, use **Manage notices** to publish, edit, or delete notices.

## Important security note
The default login and secret key are intended for a local classroom demonstration only. Before deploying publicly, set environment variables `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and `SECRET_KEY` to strong values. For a production application, add CSRF protection, rate limiting, and a proper password-hashing/user-management system. Do not use Flask's debug server for public deployment.

## Suggested project description
**Problem statement:** Traditional paper notice boards can be difficult to update and may not be seen by every student. This system provides a central digital platform where an administrator can manage notices and users can search, sort, and filter announcements.

**Objectives:**
1. Develop a web-based notice board using Python.
2. Provide administrator authentication.
3. Implement create, read, update, and delete (CRUD) operations.
4. Store notices in an SQLite database.
5. Let users search notices and sort them by date or category.
6. Build a responsive, easy-to-use interface.

**Technology stack:** Python, Flask, SQLite, HTML, CSS, Jinja templates.

**Experiential learning outcomes:** Practical experience with routing, form handling, database operations, session-based login, input validation, templating, and responsive web design.
