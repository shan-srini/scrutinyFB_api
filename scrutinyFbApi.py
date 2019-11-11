from os import environ
from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

cnx = mysql.connector.connect(user=environ.get('user'), password=environ.get('pass'),
                              host=environ.get('host'),
                              port=environ.get('port'),
                              database=environ.get('database'),
                              connection_timeout=10)

def formatString(f):
    return "'" + f + "'"

@app.route('/')
def welcome():
    return 'Welcome to Scrutiny FB API! Hosted by Heroku, documentation to be released on my github soon!'

@app.route('/getPlayerId')
def getPlayerId():
    #playerID = "'/players/M/McCaCh01'"
#    return jsonify(database_hello(playerID))
    playerID1 = "'" + request.args['player_id1'] + "'"
    #playerID2 = "'" + request.args['player_id2'] + "'"
    query = "SELECT * from playerInfo WHERE player_id = %s" % (playerID1)
    mycursor = cnx.cursor()
#    try:
    mycursor.execute(query)
#    except my.Error as e:
#        return jsonify(e)
    myresult = mycursor.fetchall()
    myresult = jsonify(myresult)
    return myresult

@app.route('/insertPlayer')
def updatePlayerId():
    playerID = request.args['playerID']
    playerName = request.args['playerName']
    position = request.args['position']
    teamID = request.args['teamID']
    height = request.args['height']
    weight = request.args['weight']
    
    insert_player = "INSERT INTO `shan`.`playerInfo` (`player_id`, `player_name`, `player_position`, `current_team`, `player_height`, `player_weight`) VALUES (%s,%s,%s,%s,%s,%s)" % (formatString(playerID), formatString(playerName), formatString(position), formatString(teamID), formatString(height), formatString(weight))
    
    mycursor = cnx.cursor()
    mycursor.execute(insert_player)
    
    return 'Success, Player Inserted'
    
@app.route('/deletePlayer')
def deletePlayerById():
    playerID = formatString(request.args['playerID'])
    delete_player = "DELETE FROM playerInfo WHERE player_id = %s" % (playerID)
    
    mycursor = cnx.cursor()
    mycursor.execute(delete_player)
    
    return 'Success, Player Deleted'



if __name__ == "__main__":
    app.run()
