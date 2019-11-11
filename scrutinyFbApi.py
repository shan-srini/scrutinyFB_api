from os import environ
from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

cnx = mysql.connector.connect(user=environ.get('user'), password=environ.get('pass'),
                              host=environ.get('host'),
                              port=environ.get('port'),
                              database=environ.get('database'),
                              connection_timeout=10)

#def getPlayerInfo(playerID):
#    mycursor = cnx.cursor()
#    mycursor.execute("SELECT * from playerInfo WHERE player_id = '/players/M/McCaCh01'")
#    myresult = mycursor.fetchall()
#    return myresult[0]

@app.route('/')
def welcome():
    return 'Welcome to Scrutiny FB API! Hosted by Heroku, documentation to be released on my github soon!'

@app.route('/getPlayerId')
def hello():
#    playerID = request.args.get('player_id')
#    return jsonify(database_hello(playerID))
    mycursor = cnx.cursor()
    mycursor.execute("SELECT * from playerInfo WHERE player_id = '/players/M/McCaCh01'")
    myresult = mycursor.fetchall()
    return jsonify(myresult[0])

if __name__ == "__main__":
	app.run()
