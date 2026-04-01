from flask import Flask, render_template, request, redirect, session, flash
import os

from db import init_db, get_db
from matcher import match_dsl
from resume_parser import extract_text

app = Flask(__name__)
app.secret_key = "secret"
app.config['UPLOAD_FOLDER'] = 'uploads'

init_db()

# ---------- LOGIN ----------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form['username']
        p = request.form['password']

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
        user = c.fetchone()

        if user:
            session['user_id'] = user[0]
            session['role'] = user[3]

            if user[3] == "hr":
                return redirect("/hr")
            else:
                return redirect("/candidate")
        else:
            return "Invalid Login ❌"

    return render_template("login.html")


# ---------- REGISTER ----------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        u = request.form['username']
        p = request.form['password']
        role = request.form['role']
        linkedin = request.form['linkedin']

        conn = get_db()
        c = conn.cursor()

        c.execute("""
        INSERT INTO users(username,password,role,linkedin)
        VALUES (?,?,?,?)
        """, (u,p,role,linkedin))

        conn.commit()

        return redirect("/")

    return render_template("register.html")


# ---------- HR ----------
@app.route("/hr", methods=["GET","POST"])
def hr():

    if 'user_id' not in session or session['role'] != "hr":
        return redirect("/")

    conn = get_db()
    c = conn.cursor()

    # POST JOB
    if request.method == "POST":
        role = request.form['role']
        dsl = request.form['dsl']

        c.execute("INSERT INTO jobs(role,dsl) VALUES (?,?)",(role,dsl))
        conn.commit()

    # FETCH JOBS
    c.execute("SELECT * FROM jobs")
    jobs = c.fetchall()

    # 🔥 FETCH APPLICATIONS WITH LINKEDIN
    c.execute("""
    SELECT applications.id, users.username, users.linkedin, jobs.role, applications.status
    FROM applications
    JOIN users ON applications.user_id = users.id
    JOIN jobs ON applications.job_id = jobs.id
    """)
    apps = c.fetchall()

    return render_template("hr_dashboard.html", jobs=jobs, apps=apps)


# ---------- CANDIDATE ----------
@app.route("/candidate", methods=["GET","POST"])
def candidate():

    if 'user_id' not in session or session['role'] != "candidate":
        return redirect("/")

    jobs = []

    if request.method == "POST":
        dsl = request.form['dsl']
        file = request.files.get('resume')

        if file and file.filename != "":
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(path)
            dsl += " " + extract_text(path)

        session['candidate_dsl'] = dsl
        flash("Details submitted successfully ✅")

    dsl = session.get('candidate_dsl', "")

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM jobs")
    all_jobs = c.fetchall()

    for j in all_jobs:
        if match_dsl(dsl, j[2]) > 0:
            jobs.append(j)

    # APPLICATION STATUS
    c.execute("""
    SELECT jobs.role, applications.status
    FROM applications
    JOIN jobs ON applications.job_id = jobs.id
    WHERE applications.user_id = ?
    """, (session['user_id'],))

    applied_jobs = c.fetchall()

    return render_template("candidate_dashboard.html", jobs=jobs, applied_jobs=applied_jobs)


# ---------- APPLY ----------
@app.route("/apply/<int:job_id>")
def apply(job_id):

    if 'user_id' not in session:
        return redirect("/")

    conn = get_db()
    c = conn.cursor()

    c.execute("INSERT INTO applications(user_id,job_id,status) VALUES (?,?,?)",
              (session['user_id'], job_id, "Pending"))

    conn.commit()
    return redirect("/candidate")


# ---------- STATUS ----------
@app.route("/status/<int:app_id>/<status>")
def status(app_id, status):

    conn = get_db()
    c = conn.cursor()

    c.execute("UPDATE applications SET status=? WHERE id=?", (status, app_id))
    conn.commit()

    return redirect("/hr")


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)