from os import environ
from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

cnx = mysql.connector.connect(user=environ.get('user'), password=environ.get('pass'),
                              host=environ.get('host'),
                              port=environ.get('port'),
                              database=environ.get('database'),
                              connection_timeout=10)

@app.route('/')
def welcome():
    return 'Welcome to Scrutiny FB API! Hosted by Heroku, documentation to be released on https://github.com/shan-srini soon!'
    
@app.route('/error')
def oops():
    return 'Oops API hit an error'

@app.route('/getPlayerId')
def getPlayerId():
    #playerID = "'/players/M/McCaCh01'"
#    return jsonify(database_hello(playerID))
    playerID = "'" + request.args['player_id1'] + "'"
    #playerID2 = "'" + request.args['player_id2'] + "'"
    query = "SELECT * from playerInfo WHERE player_id = %s" % (playerID)
    mycursor = cnx.cursor()
#    try:
    mycursor.execute(query)
#    except my.Error as e:
#        return jsonify(e)
    myresult = mycursor.fetchall()
    return jsonify(myresult)

#@app.route('/updatePlayerId')
#def updatePlayerId():
#    playerID1 = request.args[]



if __name__ == "__main__":
    app.run()
