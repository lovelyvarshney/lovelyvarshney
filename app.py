import re
import MySQLdb
import redis, json
from flask import Flask,render_template,request,jsonify,session, redirect, sessions, url_for
from flask_mysqldb import MySQL
from flask_caching import Cache
from random import randint
from flask_redis import FlaskRedis
from datetime import timedelta


app = Flask(__name__)
redis_client = redis.Redis(host='127.0.0.1', port=6379, db =0)

app.config['CACHE_TYPE'] = 'simple'
app.config['MYSQL_HOST'] ="localhost"
app.config['MYSQL_USER'] ="oyelovely"
app.config['MYSQL_PASSWORD'] ="L0v3ly@9917"
app.config['MySQL_DB'] ="mydatabase"
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

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
        res = cur.execute("INSERT INTO mydatabase.users (name,email) VALUES (%s, %s)",(username,email))
        #redis_client.set('userD',json.dumps(res))
        #reply = json.loads(r.execute_command('JSON.GET', 'object'))
        mysql.connection.commit()

        cur.close()
        return "success"
    return render_template('index.html')

@app.route('/alluser', methods=['GET'])
def alluser():
    try:
        cur = mysql.connection.cursor()
        users = cur.execute("SELECT * FROM mydatabase.users")
        userD = redis_client.get('userD')
        #redis_client.incr('userD')
        if userD is not None:
            print('User found in Redis')
            return userD
        else:
            print ("Not found in redis so retrieving from database")
            if users > 0:
                userDetails = cur.fetchall()
                res = jsonify(userDetails)
                redis_client.set('userD',json.dumps(userDetails))
                res.status_code = 200
                return res   
                
            else:
                return not_found()  
    except Exception as e:
        print (e)
    finally:
        cur.close()
    #return render_template('users.html', userDetails = userDetails)

@app.route('/user/<int:id>')
def userid(id):
    try:
        cur = mysql.connection.cursor()
        try: 
            users = cur.execute("SELECT * FROM mydatabase.users where id =%s",[id])
        except Exception:
            return "Error"
        userkey = f"key_{id}"
        userk = redis_client.get(userkey)
        if userk is not None:
            print('User found in Redis')
            return userk
        else:
            print ("Not found in redis so retrieving from database")
            if users > 0:
                userDetails = cur.fetchall()
                res = jsonify(userDetails)

                redis_client.set(userkey,json.dumps(userDetails))
                res.status_code = 200
                #redis_client.set('userD',res)
                #userD = json.loads(res)
                return res   
                
            else:
                raise (TypeError, Exception)

    except Exception as e:
        print ("Something went wrong")
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        return ("MYSQL error")
    except IndexError as e:
        return not_found()
    except TypeError as e:
        return ("Error")
    except ValueError as e:
        print(e)
        return None

@app.route('/user/delete/<int:id>', methods=['DELETE'])
def deleteuser(id):
    try:
        cur = mysql.connection.cursor()
        #userkey = f"key_{id}"
        cur.execute("Delete * FROM mydatabase.users where id =%s",[id])
        mysql.connection.commit()
        resp = jsonify("User deleted successfully")
        resp.status_code = 200
        return resp
        """ if res == 0:
            print ("User not present in database")
        elif res > 0:
            print ("Deleting user from database")
            return "Deleted user from database successfully"  """
        """ elif userkey is not None:
                userk = redis_client.delete(userkey)
                return "User deleted from cache"
        else:
            return not_found()  """

    except (MySQLdb.Error, MySQLdb.Warning):
        return not_found()
    except IndexError:
        return not_found()
    except TypeError:
        return not_found()
    except ValueError as e:
        print(e)
        return None

@app.errorhandler(404)
def not_found(error=None):
	message = {
	        'status': 404,
	        'message': 'There is no record',
	    }
	res = jsonify(message)
	res.status_code = 404
 
	return res

@app.errorhandler(500)
def not_found(error=None):
	message = {
	        'status': 500,
	        'message': '500 internal server error',
	    }
	res = jsonify(message)
	res.status_code = 500
 
	return res

if __name__ == '__main__':
    app.run(debug=True)
