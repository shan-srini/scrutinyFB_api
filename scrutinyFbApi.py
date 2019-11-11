from os import environ
from flask import Flask
import mysql.connector

app = Flask(__name__)

cnx = mysql.connector.connect(user=environ.get('user'), password=environ.get('pass'),
                              host=environ.get('host'),
                              port=environ.get('port'),
                              database=environ.get('database'))

@app.route('/')
def index():
	#return 'Welcome to our ScrutinyFB API!'
	return environ.get('database')

if __name__ == "__main__":
	app.run()
