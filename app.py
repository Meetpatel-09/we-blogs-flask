from flask import Flask, render_template, request, url_for, redirect, session
from flask_session import Session
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_USER'] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "we-blogs"

mysql = MySQL(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def home():

    query = "SELECT blogs_tbl.*, users_tbl.user_id, users_tbl.first_name FROM blogs_tbl JOIN users_tbl ON blogs_tbl.user_id = users_tbl.user_id"

    cur = mysql.connection.cursor()
    cur.execute(query)
    blogs = cur.fetchall()

    listDict = []

    for blog in blogs:
        dict = {
            "title": blog[2],
            "shortDesc": blog[3],
            "fullDesc": blog[4],
            "dateTime": blog[6],
            "userName": blog[8],
        }
        listDict.append(dict)

    return render_template("home.html", blogs=listDict)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['inputEmail']
        password = request.form['inputPassword']

        cur = mysql.connection.cursor()

        query = "SELECT * FROM users_tbl WHERE email = %s"

        cur.execute(query, (email,))

        result = cur.fetchone()

        if result:
            if result[-1] == password:
                session['user_id'] = result[0]
                return redirect(url_for('home'))
            else:
                return render_template('login.html',  message="1")

            # print(result.user_id)
            # print(result.email)
            # print(result.password)
            # return redirect(url_for('home'))
        else:
            return render_template('login.html',  message="2")

        # return
    if request.method == 'GET':
        return render_template("login.html")

    return "Method Not Allow"


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fName = request.form['inputFName']
        lName = request.form['inputLName']
        email = request.form['inputEmail']
        password = request.form['inputPassword']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users_tbl (first_name, last_name, email, password) VALUES (%s,%s,%s,%s)",
                    (fName, lName, email, password))

        mysql.connection.commit()

        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('register.html')

    return "Method Not Allow"


@app.route("/add-blog", methods=['GET', 'POST'])
def addBlog():
    if session['user_id']:
        if request.method == 'GET':
            return render_template('addblog.html')
        else:
            title = request.form['inputTitle']
            sDesc = request.form['inputShortDescription']
            fDesc = request.form['inputFullDescription']
            userID = session['user_id']
            # img = request.form['inputImage']

            cur = mysql.connection.cursor()

            query = "INSERT INTO blogs_tbl(user_id, title, short_description, full_description) VALUES (%s, %s, %s, %s)"

            result = cur.execute(query, (userID, title, sDesc, fDesc))

            mysql.connection.commit()

            print(result)

            return redirect(url_for('home'))

    else:
        return redirect(url_for('login'))


@app.route("/my-blogs")
def myBlogs():
    if session['user_id']:
        return render_template('myblogs.html')
    else:
        return redirect(url_for('login'))


@app.route("/profile")
def profile():
    if session['user_id']:
        return render_template('profile.html')
    else:
        return redirect(url_for('login'))


@app.route("/logout")
def logout():
    session['user_id'] = None
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
