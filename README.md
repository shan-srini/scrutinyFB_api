# scrutinyFB_api
API for ScrutinyFB to host on heroku

Python V: 2.7.17
Connector/Python V: 1.2
MySQL V: 5.1


# Paths
These are some REST API path examples
<br/>
To verify that user has been created & a player has been added/deleted to user's favorite list
scrutiny-fb-api.herokuapp.com/getFavPlayerNames?userName= USER NAME INPUT (example is Shan)

Get player info by player's name
scrutiny-fb-api.herokuapp.com/getPlayerByName?playerName= PLAYER NAME INPUT (example Tom Brady)

Get player's stats for home log by player ID
scrutiny-fb-api.herokuapp.com/getStatsById?playerID= PLAYER ID INPUT (example is /players/B/BarkSa00)

Get a list of all player's in the database
scrutiny-fb-api.herokuapp.com/getAllPlayerNames 
