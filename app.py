import os
import sqlite3
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, g

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-before-deployment")
DATABASE = os.path.join(os.path.dirname(__file__), "notices.db")

# Demo credentials for the experiential-learning project.
# Change these before deploying the application publicly.
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("""
            CREATE TABLE IF NOT EXISTS notices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                notice_date TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        g.db.commit()
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Please sign in as an administrator first.", "warning")
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped_view


@app.route("/")
def index():
    db = get_db()
    category = request.args.get("category", "").strip()
    sort = request.args.get("sort", "newest")
    search = request.args.get("q", "").strip()

    query = "SELECT * FROM notices WHERE 1=1"
    params = []
    if category:
        query += " AND category = ?"
        params.append(category)
    if search:
        query += " AND (title LIKE ? OR content LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if sort == "oldest":
        query += " ORDER BY notice_date ASC, id ASC"
    elif sort == "title":
        query += " ORDER BY title COLLATE NOCASE ASC"
    else:
        query += " ORDER BY notice_date DESC, id DESC"

    notices = db.execute(query, params).fetchall()
    categories = db.execute(
        "SELECT DISTINCT category FROM notices ORDER BY category COLLATE NOCASE"
    ).fetchall()
    return render_template(
        "index.html", notices=notices, categories=categories,
        selected_category=category, sort=sort, search=search
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session.clear()
            session["is_admin"] = True
            flash("Welcome back! You are signed in.", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Incorrect username or password.", "danger")
    return render_template("login.html")


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("index"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    notices = get_db().execute(
        "SELECT * FROM notices ORDER BY created_at DESC, id DESC"
    ).fetchall()
    return render_template("admin.html", notices=notices)


def validate_notice(form):
    title = form.get("title", "").strip()
    content = form.get("content", "").strip()
    category = form.get("category", "").strip()
    notice_date = form.get("notice_date", "").strip()
    if not all([title, content, category, notice_date]):
        return None, "Please complete every field."
    try:
        datetime.strptime(notice_date, "%Y-%m-%d")
    except ValueError:
        return None, "Please enter a valid notice date."
    if len(title) > 120:
        return None, "Title must be 120 characters or fewer."
    if len(category) > 50:
        return None, "Category must be 50 characters or fewer."
    return {
        "title": title, "content": content,
        "category": category, "notice_date": notice_date
    }, None


@app.route("/admin/notices/new", methods=["GET", "POST"])
@admin_required
def create_notice():
    if request.method == "POST":
        data, error = validate_notice(request.form)
        if error:
            flash(error, "danger")
        else:
            db = get_db()
            db.execute(
                "INSERT INTO notices (title, content, category, notice_date, created_at) VALUES (?, ?, ?, ?, ?)",
                (data["title"], data["content"], data["category"],
                 data["notice_date"], datetime.now().isoformat(timespec="seconds"))
            )
            db.commit()
            flash("Notice published successfully.", "success")
            return redirect(url_for("admin_dashboard"))
    return render_template("notice_form.html", notice=None, page_title="Publish a notice")


@app.route("/admin/notices/<int:notice_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_notice(notice_id):
    db = get_db()
    notice = db.execute("SELECT * FROM notices WHERE id = ?", (notice_id,)).fetchone()
    if notice is None:
        flash("That notice could not be found.", "danger")
        return redirect(url_for("admin_dashboard"))
    if request.method == "POST":
        data, error = validate_notice(request.form)
        if error:
            flash(error, "danger")
        else:
            db.execute(
                "UPDATE notices SET title=?, content=?, category=?, notice_date=? WHERE id=?",
                (data["title"], data["content"], data["category"], data["notice_date"], notice_id)
            )
            db.commit()
            flash("Notice updated successfully.", "success")
            return redirect(url_for("admin_dashboard"))
    return render_template("notice_form.html", notice=notice, page_title="Update notice")


@app.route("/admin/notices/<int:notice_id>/delete", methods=["POST"])
@admin_required
def delete_notice(notice_id):
    db = get_db()
    db.execute("DELETE FROM notices WHERE id = ?", (notice_id,))
    db.commit()
    flash("Notice deleted.", "info")
    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
