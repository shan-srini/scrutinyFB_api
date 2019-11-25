from os import environ
from flask import Flask, jsonify, request
import mysql.connector
import pandas as pd
import pymysql

app = Flask(__name__)

def getConnection():
    cnx = mysql.connector.connect(user=environ.get('user'),
    password=environ.get('pass'),
    host=environ.get('host'),
    port=environ.get('port'),
    database=environ.get('database'),
    connection_timeout=20)
    return cnx

def formatString(f):
    return "'" + f + "'"


@app.route('/')
def welcome():
    return """
    <h1> Welcome to Scrutiny FB API! </h1>
    <h2> Created by Shan </h2>
    <p>Documentation to be released on my
    <a href="https://github.com/shan-srini/scrutinyFB_api"> Github </a>
    soon!</p>
    <p>Thanks to Heroku, hosted on a free tier Dyno!<p>"""

# Get player by ID
@app.route('/getPlayerId')
def getPlayerId():
    cnx = getConnection()
    #playerID = "'/players/M/McCaCh01'"
#    return jsonify(database_hello(playerID))
    playerID1 = "'" + request.args['playerId'] + "'"
    #playerID2 = "'" + request.args['player_id2'] + "'"
    query = "SELECT * from playerInfo WHERE player_id = %s" % (playerID1)
    df = pd.read_sql(query,cnx)
    cnx.commit()
    cnx.close()
    return jsonify(df.to_json(orient='records')[1:-1])
#    mycursor = cnx.cursor(dictionary=True)
##    try:
#    mycursor.execute(query)
##    except my.Error as e:
##        return jsonify(e)
#    myresult = mycursor.fetchall()
#    return jsonify(myresult)

# get player by name
@app.route('/getPlayerByName')
def getPlayerByName():
    cnx = getConnection()
    playerName = "'" + request.args['playerName'] + "'"
    query = "SELECT * from playerInfo WHERE player_name = %s" % (playerName)
    df = pd.read_sql(query,cnx)
    cnx.commit()
    cnx.close()
    return jsonify(df.to_json(orient='records')[1:-1])

# insert player must include all details
@app.route('/insertPlayer')
def updatePlayerId():
    cnx = getConnection()
    playerID = request.args['playerID']
    playerName = request.args['playerName']
    position = request.args['position']
    teamID = request.args['teamID']
    height = request.args['height']
    weight = request.args['weight']

    insert_player = "INSERT INTO `shan`.`playerInfo` (`player_id`, `player_name`, `player_position`, `current_team`, `player_height`, `player_weight`) VALUES (%s,%s,%s,%s,%s,%s)" % (formatString(playerID), formatString(playerName), formatString(position), formatString(teamID), formatString(height), formatString(weight))

    mycursor = cnx.cursor()
    mycursor.execute(insert_player)
    cnx.commit()
    cnx.close()
    return 'Success, Player Inserted'

# delete player by ID
@app.route('/deletePlayer')
def deletePlayerById():
    cnx = getConnection()
    playerID = formatString(request.args['playerID'])
    delete_player = "DELETE FROM playerInfo WHERE player_id = %s" % (playerID)

    mycursor = cnx.cursor()
    mycursor.execute(delete_player)
    cnx.commit()
    cnx.close()
    return 'Success, Player Deleted'

# Returns all player names
@app.route('/getAllPlayerNames')
def getAllPlayerNames():
    cnx = getConnection()
    query = "SELECT player_name FROM playerInfo"
    cursor = cnx.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cnx.commit()
    cnx.close()
    return jsonify(data)

# Returns all player statistics by ID
@app.route('/getStatsById')
def getStatsById():
    cnx = getConnection()
    playerID = formatString(request.args['playerID'])
    query = "SELECT * FROM playerStats WHERE player_id = %s" % (playerID)
    cursor = cnx.cursor()
    df = pd.read_sql(query, cnx)
    cnx.commit()
    cnx.close()
    return jsonify(df.to_json(orient='records'))

# Returns all player statistics by ID
@app.route('/getStatsByIdAway')
def getStatsByIdAway():
    cnx = getConnection()
    playerID = formatString(request.args['playerID'])
    query = "SELECT * FROM playerStats WHERE player_id = %s AND home_or_away = '@'" % (playerID)
    cursor = cnx.cursor()
    df = pd.read_sql(query, cnx)
    cnx.commit()
    cnx.close()
    return jsonify(df.to_json(orient='records'))

# Returns all player statistics by ID
@app.route('/getStatsByIdHome')
def getStatsByIdHome():
    cnx = getConnection()
    playerID = formatString(request.args['playerID'])
    query = "SELECT * FROM playerStats WHERE player_id = %s AND NOT home_or_away = '@'" % (playerID)
    cursor = cnx.cursor()
    df = pd.read_sql(query, cnx)
    cnx.commit()
    cnx.close()
    return jsonify(df.to_json(orient='records'))

##########################################
# LOGIN TO THE favUser SCREEN
@app.route('/login', methods=['POST'])
def login():
    cnx = getConnection()
    if request.method == 'POST':
        #data = request.body
        username = request.form.get("username")
        password = request.form.get("password")
    args=[username, password]
    cursor = cnx.cursor()
    try:
        cursor.callproc('loginAttempt', args)
    except:
        return "User already exists"
    cnx.commit()
    cnx.close()
    return "user added"

@app.route('/addPlayerForUser')
def addPlayerForUser():
    cnx = getConnection()
    userName = request.args['userName']
    playerName = request.args['playerName']
    args = [userName, playerName]
    cursor = cnx.cursor()
    cursor.callproc('addFavPlayer', args)
    cnx.commit()
    cnx.close()
    return "player added for %s" % (userName)

@app.route('/getFavPlayerNames')
def getFavPlayerNames():
    cnx = getConnection()
    userName = request.args['userName']
    args=[userName]
    cursor = cnx.cursor()
    cursor.callproc('getFavPlayerNames', args)
    toReturn = []
    for result in cursor.stored_results():
        toReturn.append(result.fetchall())
    cnx.commit()
    cnx.close()
    return jsonify(toReturn)

@app.route('/deleteFavPlayer')
def deleteFavPlayer():
    cnx = getConnection()
    userName = request.args['userName']
    playerName = request.args['playerName']
    args=[userName, playerName]
    cursor = cnx.cursor()
    data = cursor.callproc('deleteFavPlayer', args)
    cnx.commit()
    cnx.close()
    return "Deleted"


##########################################

if __name__ == "__main__":
    app.run()
