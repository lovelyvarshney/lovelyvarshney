from flask import Flask,render_template,request,jsonify
from flask_mysqldb import MySQL
from flask_caching import Cache
from random import randint

app = Flask(__name__)

app.config['CACHE_TYPE'] = 'simple'
app.config['MYSQL_HOST'] ="localhost"
app.config['MYSQL_USER'] ="oyelovely"
app.config['MYSQL_PASSWORD'] ="L0v3ly@9917"
app.config['MySQL_DB'] ="mydatabase"

cache = Cache()
cache.init_app(app)
mysql = MySQL(app)

@app.route('/')
@cache.cached(timeout=10)
def trying():
    rn = randint(1,1000)
    return f'<h1>The number is: {rn} </h1>'


@app.route('/sub', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO mydatabase.users (name,email) VALUES (%s, %s)",(username,email))

        mysql.connection.commit()

        cur.close()
        return "success"
    return render_template('index.html')

@app.route('/users')
def user():
    cur = mysql.connection.cursor()

    users = cur.execute("SELECT * FROM mydatabase.users")

    if users > 0:
        userDetails = cur.fetchall()

        return jsonify(userDetails)
        #return render_template('users.html', userDetails = userDetails)

if __name__ == '__main__':
    app.run(debug=True)