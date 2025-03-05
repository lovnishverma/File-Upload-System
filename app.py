from flask import Flask, request, render_template, send_from_directory, g, redirect, url_for
import os
import sqlite3
import datetime
import pytz

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
DATABASE = "files.db"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Database helper functions
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE NOT NULL,
                description TEXT,
                size INTEGER,
                uploaded_at TEXT
            )
        """)
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

@app.route("/", methods=["GET", "POST"])
def upload_file():
    db = get_db()
    if request.method == "POST":
        file = request.files["file"]
        description = request.form.get("description", "").strip()
        
        if file:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)

            file_size = os.path.getsize(file_path)  # Get file size in bytes

            # Save file record in the database
            try:
                db.execute(
                    "INSERT INTO files (filename, description, size) VALUES (?, ?, ?)",
                    (file.filename, description, file_size)
                )
                db.commit()
            except sqlite3.IntegrityError:
                return "File already exists! <a href='/'>Go back</a>"

            return redirect(url_for("upload_file"))

    # Fetch all uploaded files (latest first)
    files = db.execute("SELECT * FROM files ORDER BY uploaded_at DESC").fetchall()
    total_files = len(files)  # Get total file count
    return render_template("index.html", files=files, total_files=total_files)

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

@app.route("/delete/<int:file_id>")
def delete_file(file_id):
    db = get_db()
    file = db.execute("SELECT * FROM files WHERE id = ?", (file_id,)).fetchone()

    if file:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file["filename"])

        # Delete the file from the server
        if os.path.exists(file_path):
            os.remove(file_path)

        # Remove record from the database
        db.execute("DELETE FROM files WHERE id = ?", (file_id,))
        db.commit()

    return redirect(url_for("upload_file"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
