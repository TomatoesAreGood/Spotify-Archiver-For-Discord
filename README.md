# Spotify Archiver For Discord
 A Discord bot which tracks users' Spotify listening activity, and compiles the songs into a Spotify playlist.

## Features
- Record songs from selected users, and create custom Spotify playlists based on users' Spotify listening activity --> Spotify activity must be enabled on Discord
- Able to keep track of multiple users at any point in time
- Custom playlist covers (the user's profile picture) which are downloaded and uploaded to Spotify

## Steps to use
1. Clone this Git repository into a file of your choice. Enter `pip install -r requirements.txt` in the command line or terminal to install the needed dependancies to run this bot.
2. Create a new file called '.env' and keep it in the background so that you can progressively fill it out with more information. 
3. Open Discord, go into settings and enable developer mode --> needed for retrieving server and user ID's. 
4. Log into the [Discord Developer's Portal](https://discord.com/developers/applications) and create a new application. Choose a name of your choice: it will be displayed in the server.
5. Navigate to the 'URL generator' tab which is underneath the 'OAuth2' section. Select 'bot' for scopes and 'Administrator' for bot permissions. Admin permissions are needed to read text messages in channels and send Spotify URLs.
6. Generate the client secret, and declare it as 'DISCORD_TOKEN' in the .env file. For now, the .env file should look like: 'DISCORD_TOKEN = (your client secret)'
7. Open up and log into the [Spotify Developer's Portal](https://developer.spotify.com/).  You should create a new, free spotify account to store all the playlists generated by the bot. Navigate to the application dashboard in the top right, and create a new app. Fill out information about the bot, but set the redirect URL to 'http://localhost:8888/callback'.
8. Once a Spotify app has been created, retreive the Spotify Client ID and Client Secret. Create and put them the fields 'SPOTIPY_CLIENT_SECRET', and 'SPOTIFY_CLIENT_ID'. 
9. Only 2 more fields to go for the .env file. Create the field 'SPOTIFY_USER_ID' and give it the Spotify ID of the account that you created the app with. To get the Spotify ID, go to the account page on Spotify, and everything after the /user/ is the user ID.
10. The last field in the .env file is the 'PRIVATE_CHANNEL_ID'. Since you probably don't want your bot to be called in every single server channel, the bot will only respond to pings if it is in a specific channel. Navigate to the channel which you want the bot commands to be called. Copy the channel ID by right clicked it, and insert it into the field.
11. The final .env file should look like:
```
#.env
DISCORD_TOKEN = (your Discord client secret)
SPOTIPY_CLIENT_SECRET = (your Spotify client secret)
SPOTIFY_CLIENT_ID = (your Spotify client ID)
SPOTIFY_USER_ID = (user ID of the Spotify account which playlists will be created)
PRIVATE_CHANNEL_ID = (channel ID which the bot responds to)
```
12. Run the bot in the terminal through 'python bot.py'
