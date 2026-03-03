from flask import Flask, request
import sqlite3
from tabulate import tabulate

app = Flask(__name__)

# -----------------------
# Database Connection
# -----------------------
def get_db():
    conn = sqlite3.connect("members.db")
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------
# Setup Database
# -----------------------
def setup():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')

    cur = conn.execute("SELECT COUNT(*) FROM members")
    count = cur.fetchone()[0]

    # Insert initial data only if table empty
    if count == 0:
        for i in range(1, 6):
            conn.execute(
                "INSERT INTO members (id, name, email) VALUES (?, ?, ?)",
                (i, f"Member{i}", f"member{i}@test.com")
            )
        conn.commit()

    conn.close()


# -----------------------
# View Members (GET)
# -----------------------
@app.route("/", methods=["GET"])
def view_members():
    conn = get_db()
    members = conn.execute("SELECT * FROM members ORDER BY id").fetchall()
    conn.close()

    data = [tuple(member) for member in members]

    table = tabulate(
        data,
        headers=["ID", "Name", "Email"],
        tablefmt="grid"
    )

    return table, 200, {"Content-Type": "text/plain"}


# -----------------------
# Add Member (POST)
# -----------------------
@app.route("/add", methods=["POST"])
def add_member():
    member_id = request.form.get("id")
    name = request.form.get("name")
    email = request.form.get("email")

    if not member_id or not name or not email:
        return "Error: ID, Name and Email required\n", 400

    conn = get_db()

    # Check if ID already exists
    existing = conn.execute(
        "SELECT * FROM members WHERE id = ?",
        (member_id,)
    ).fetchone()

    if existing:
        conn.close()
        return "Error: ID already exists\n", 400

    # Insert with custom ID
    conn.execute(
        "INSERT INTO members (id, name, email) VALUES (?, ?, ?)",
        (member_id, name, email)
    )
    conn.commit()
    conn.close()

    return "Member added successfully\n"


# -----------------------
# Delete Member (POST)
# -----------------------
@app.route("/delete", methods=["POST"])
def delete_member():
    member_id = request.form.get("id")

    if not member_id:
        return "Error: ID required\n", 400

    conn = get_db()

    # Check if ID exists before deleting
    existing = conn.execute(
        "SELECT * FROM members WHERE id = ?",
        (member_id,)
    ).fetchone()

    if not existing:
        conn.close()
        return "Error: ID not found\n", 404

    conn.execute("DELETE FROM members WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()

    return "Member deleted successfully\n"


# -----------------------
# Run App
# -----------------------
if __name__ == "__main__":
    setup()
    app.run(debug=True)
