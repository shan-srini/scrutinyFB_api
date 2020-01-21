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
    playerID1 = "'" + request.args['playerId'] + "'"
    query = "SELECT * from playerInfo WHERE player_id = %s" % (playerID1)
    df = pd.read_sql(query,cnx)
    cnx.commit()
    cnx.close()
    return jsonify(df.to_json(orient='records')[1:-1])
    
    
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
    
#Get Stats refined, abstracted used for production
@app.route('/getStats', methods=['POST'])
def getStats():
    cnx = getConnection()
    cursor = cnx.cursor()
    playerID = formatString(request.form.get("playerID"))
    home_or_away = request.form.get("home_or_away")
    dateLikeFormat = '%{}%'
    year = formatString(dateLikeFormat.format(request.form.get("year")))
    if(home_or_away == "full"):
        query = "SELECT * FROM playerStats WHERE player_id = %s AND Date LIKE %s" % (playerID, year)
    elif(home_or_away == "away"):
        query = "SELECT * FROM playerStats WHERE player_id = %s AND home_or_away = '@' AND Date LIKE %s" % (playerID, year)
    else:
        query = "SELECT * FROM playerStats WHERE player_id = %s AND NOT home_or_away = '@' AND Date LIKE %s" % (playerID, year)
    df = pd.read_sql(query, cnx)
    cnx.commit()
    cnx.close()
    return jsonify(df.to_json(orient='records'))

#Player splits gets it by using playerNames, keeping integrity using inner join
@app.route('/getSplits', methods=['POST'])
def getSplits():
    cnx1 = getConnection()
    cnx2 = getConnection()
    cursor1 = cnx1.cursor()
    cursor2 = cnx2.cursor()
    playerName = formatString(request.form.get("playerName"))
    splitPlayerName = formatString(request.form.get("splitPlayerName"))
    home_or_away = request.form.get("home_or_away")
    dateLikeFormat = '%{}%'
    year = formatString(dateLikeFormat.format(request.form.get("year")))
    if (home_or_away == "full"):
        querySplitsWithout = """SELECT * FROM playerStats JOIN playerInfo USING(player_id) WHERE player_name = %s AND Date LIKE %s
        AND Date NOT IN
        (SELECT Date FROM playerStats JOIN playerInfo USING(player_id) WHERE player_name = %s)""" % (playerName, year, splitPlayerName)
        dfPlayerSplitsWithout = pd.read_sql(querySplitsWithout, cnx1)
        querySplitsWith = """SELECT * FROM playerStats JOIN playerInfo USING(player_id) WHERE player_name = %s AND Date LIKE %s
        AND Date IN
        (SELECT Date FROM playerStats JOIN playerInfo USING(player_id) WHERE player_name = %s)""" % (playerName, year, splitPlayerName)
        dfPlayerSplitsWith = pd.read_sql(querySplitsWith, cnx2)
    elif (home_or_away == "home"):
        querySplitsWithout = """SELECT * FROM playerStats JOIN playerInfo USING(player_id) WHERE player_name = %s
        AND NOT home_or_away = '@' AND Date LIKE %s
        AND Date NOT IN
        (SELECT Date FROM playerStats JOIN playerInfo USING(player_id) WHERE player_name = %s)""" % (playerName, year, splitPlayerName)
        dfPlayerSplitsWithout = pd.read_sql(querySplitsWithout, cnx1)
        querySplitsWith = """SELECT * FROM playerStats JOIN playerInfo USING(player_id) WHERE player_name = %s
        AND NOT home_or_away = '@' AND Date LIKE %s
        AND Date IN
        (SELECT Date FROM playerStats JOIN playerInfo USING(player_id) WHERE player_name = %s)""" % (playerName, year, splitPlayerName)
        dfPlayerSplitsWith = pd.read_sql(querySplitsWith, cnx2)
    #away
    else:
        querySplitsWithout = """SELECT * FROM playerStats JOIN playerInfo USING(player_id) WHERE player_name = %s
        AND home_or_away = '@' AND Date LIKE %s
        AND Date NOT IN
        (SELECT Date FROM playerStats JOIN playerInfo USING(player_id) WHERE player_name = %s)""" % (playerName, year, splitPlayerName)
        dfPlayerSplitsWithout = pd.read_sql(querySplitsWithout, cnx1)
        querySplitsWith = """SELECT * FROM playerStats JOIN playerInfo USING(player_id) WHERE player_name = %s
        AND home_or_away = '@' AND Date LIKE %s
        AND Date IN
        (SELECT Date FROM playerStats JOIN playerInfo USING(player_id) WHERE player_name = %s)""" % (playerName, year, splitPlayerName)
        dfPlayerSplitsWith = pd.read_sql(querySplitsWith, cnx2)
    cnx1.commit()
    cnx1.close()
    cnx2.commit()
    cnx2.close()
    toReturn = {
    "splitsWithout" : dfPlayerSplitsWithout.to_json(orient='records'),
    "splitsWith" : dfPlayerSplitsWith.to_json(orient='records')
    }
    return jsonify(toReturn)

##########################################
# LOGIN TO THE favUser SCREEN
# error handling in here as well as in sql procedure
@app.route('/login', methods=['POST'])
def login():
    cnx = getConnection()
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
    args=[username, password]
    cursor = cnx.cursor()
    cursor.callproc('loginAttempt', args)
    data = cursor.stored_results()
    try:
        if (next(data).fetchall()[0][0] == 1):
            cnx.commit()
            cnx.close()
            return "success"
        else:
            cnx.commit()
            cnx.close()
            return "wrong password"
    except:
        cnx.commit()
        cnx.close()
        return "User added"

# add player to users favorites
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

# get this users favorite players
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

# delete this player from the users favorites list
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
    
# update password for user
@app.route('/updatePass', methods=['POST'])
def updatePass():
    cnx = getConnection()
    cursor = cnx.cursor()
    args = [request.form.get("username"), request.form.get("password"), request.form.get("newPassword")]
    cursor.callproc('updatePass', args)
    cnx.commit()
    cnx.close()
    return "Procedure call complete"


##########################################

if __name__ == "__main__":
    app.run()
