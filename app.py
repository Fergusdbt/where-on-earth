from cs50 import SQL
from flask import Flask, flash, redirect, render_template, jsonify, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///whereonearth.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Home page to present user data summary
@app.route("/")
@login_required
def index():
    user_id = session.get('user_id')
    username = session.get('username')

    country_result = db.execute("SELECT COUNT(*) AS count FROM visits WHERE user_id = ? AND country_id IN (SELECT id FROM countries WHERE unMember = ?)", user_id, 1)
    country_count = country_result[0]['count']

    territory_result = db.execute("SELECT COUNT(*) AS count FROM visits WHERE user_id = ? AND country_id IN (SELECT id FROM countries WHERE unMember = ?)", user_id, 0)
    territory_count = territory_result[0]['count']

    return render_template("index.html", username=username, country_count=country_count, territory_count=territory_count)


# Registration page to validate username and password and update SQL database
@app.route("/register", methods=["GET", "POST"])
def register():
    
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            flash("You must provide a username!", "error")
            return render_template("register.html")

        if not password:
            flash("You must provide a password!", "error")
            return render_template("register.html")
        
        if len(password) < 6:
            flash("You must use at least 6 characters in your password!", "error")
            return render_template("register.html")

        if not confirmation:
            flash("You must confirm the password!", "error")
            return render_template("register.html")

        if not password == confirmation:
            flash("The passwords did not match!", "error")
            return render_template("register.html")

        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        if not len(user) == 0:
            flash("This username already exists!", "error")
            return render_template("register.html")
        
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?);", username, generate_password_hash(password))

        flash("You have successfully registered!")
        return redirect("/login")

    else:
        return render_template("register.html")


# Log in page to check username and password
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if not username:
            flash("You must provide a username!", "error")
            return render_template("login.html")

        if not password:
            flash("You must provide a password", "error")
            return render_template("login.html")

        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        if not len(user) == 1:
            flash("This username does not exist!", "error")
            return render_template("login.html")
        
        if not check_password_hash(user[0]["hash"], password):
            flash("The password is incorrect!", "error")
            return render_template("login.html")

        session["user_id"] = user[0]["id"]
        session['username'] = user[0]["username"]

        return redirect("/")

    else:
        return render_template("login.html")


# Checklist page to update SQL database and pass in saved countries
@app.route("/checklist", methods=["GET", "POST"])
@login_required
def checklist():
   
    user_id = session.get("user_id")
    countries = db.execute("SELECT * FROM countries ORDER BY name ASC")
    saved_country_list = db.execute("SELECT name FROM countries WHERE id IN (SELECT country_id FROM visits WHERE user_id = ?)", user_id)
    saved_countries = [row['name'] for row in saved_country_list]
    
    if request.method == "POST":
        visited_countries = request.form.getlist("country")

        db.execute("DELETE FROM visits WHERE user_id = ?", user_id)

        for country_name in visited_countries:
            country_id_list = db.execute("SELECT id FROM countries WHERE name = ?", country_name)

            if country_id_list:
                country_id = country_id_list[0]['id']
                db.execute("INSERT INTO visits (user_id, country_id) VALUES (?, ?);", user_id, country_id)

        saved_country_list = db.execute("SELECT name FROM countries WHERE id IN (SELECT country_id FROM visits WHERE user_id = ?)", user_id)
        saved_countries = [row['name'] for row in saved_country_list]
    
        return render_template("checklist.html", countries=countries, saved_countries=saved_countries)
    
    if request.method == "GET":
        return render_template("checklist.html", countries=countries, saved_countries=saved_countries)


# Scratch Map page to pass in saved countries
@app.route("/scratchmap", methods=["GET", "POST"])
@login_required
def scratchmap():

    if request.method == "POST":
        user_id = session.get("user_id")
        visited_countries = db.execute("SELECT * FROM countries WHERE id IN (SELECT country_id FROM visits WHERE user_id = ?)", user_id)
        return jsonify(visited_countries)

    if request.method == "GET":
        return render_template("/scratchmap.html")


# Pinboard page to update SQL database and pass in saved markers
@app.route("/pinboard", methods=["GET", "POST"])
@login_required
def pinboard():

    if request.method == "POST":
        user_id = session.get("user_id")
        data = request.get_json()
        marker = data.get('marker')
        latitude = marker["latitude"]
        longitude = marker["longitude"]

        db.execute("INSERT INTO markers (user_id, latitude, longitude) VALUES (?, ?, ?);", user_id, latitude, longitude)

        return jsonify()
    
    if request.method == "GET":
        return render_template("/pinboard.html")


# Pinboard page to update SQL database and pass in marker data to be deleted
@app.route("/markerRemoved", methods=["GET", "POST"])
@login_required
def markerRemoved():

    if request.method == "POST":
        user_id = session.get("user_id")
        data = request.get_json()
        marker = data.get('marker')
        latitude = marker["latitude"]
        longitude = marker["longitude"]
        db.execute("DELETE FROM markers WHERE latitude = ? AND longitude = ? AND user_id = ?", latitude, longitude, user_id)

        return jsonify()

    if request.method == "GET":
        return render_template("/pinboard.html")
            

# Pinboard page to pass in marker data to be loaded
@app.route("/uploadMarkers", methods=["GET", "POST"])
@login_required
def uploadMarkers():

    if request.method == "POST":
        user_id = session.get("user_id")
        saved_markers = db.execute("SELECT * FROM markers WHERE user_id = ?", user_id) 
        return jsonify(saved_markers)
    
    if request.method == "GET":
        return render_template("/pinboard.html")


# Log out button to end session
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")


# Reset password page to validate username and password and update SQL database
@app.route("/reset", methods=["GET", "POST"])
@login_required
def reset():

    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        if not current_password:
            flash("You must provide the current password!", "error")
            return render_template("reset.html")

        if not new_password:
            flash("You must provide a new password!", "error")
            return render_template("reset.html")
        
        if len(new_password) < 6:
            flash("You must use at least 6 characters in your password!", "error")
            return render_template("reset.html")

        if not confirmation:
            flash("You must confirm the new password!", "error")
            return render_template("reset.html")

        user = db.execute("SELECT * FROM users WHERE id = ?;", session["user_id"])
        if not check_password_hash(user[0]["hash"], current_password):
            flash("The current password is incorrect!", "error")
            return render_template("reset.html")

        if not new_password == confirmation:
            flash("The new passwords do not match!", "error")
            return render_template("reset.html")

        db.execute("UPDATE users SET hash = ? WHERE id = ?;", generate_password_hash(new_password), session["user_id"])

        flash("You have successfully updated your password!")
        return redirect("/")

    else:
        return render_template("reset.html")
    

# Delete account button to delete user data and end session
@app.route("/delete")
@login_required
def delete():
    user_id = session.get("user_id")
    db.execute("DELETE FROM visits WHERE user_id = ?;", user_id)
    db.execute("DELETE FROM users WHERE id = ?;", user_id)
    session.clear()
    return redirect("/")