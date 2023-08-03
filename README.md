# ClanBot
## A Discord bot to manage clans on a Discord Server. 
Created by [EllipsiaLePoulet](https://github.com/QGavoille)

### Pre-requisites
- Python 3.6 or higher (https://www.python.org/downloads/)
- dotenv (`pip install python-dotenv`) (https://pypi.org/project/python-dotenv/)
- discord.py (`pip install discord.py`) and its dependencies (https://pypi.org/project/discord.py/)
- A Discord bot token (https://discordpy.readthedocs.io/en/latest/discord.html)
- A Discord server (https://discord.com/) and its ID (https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-)

### Setup
1. Clone this repository
2. Create a file called `.env` in the root directory of the repository based on the `.env-minimal` file
3. Fill in the values in the `.env` file
    - 'TOKEN' is the Discord bot token (see above)
    - 'GUILD_ID' is the ID of the Discord server (see above)
4. Run `python3 src/main.py` in the root directory of the repository
5. Invite the bot to your server (https://discordpy.readthedocs.io/en/latest/discord.html#inviting-your-bot)

### Usage
All commands and context menus content is written in French. If you want to use this bot in another language, you will have to change the content of the `src/bot.py` file.
#### Commands
- `/newclan <clan name>`: Creates a new clan with the given name (only works if you are a server administrator)
- `/deleteclan <clan name>`: Deletes the clan with the given name (only works if you are a server administrator or on of the clan leaders)
- `/leaveclan <clan name>`: Removes you from the clan with the given name

#### Context Menus
- Clan join: Send an invite to the selected user to join the clan
- Clan promote: Promote the selected user to clan leader

### License
This project is licensed under the GNU GPLv3 license. See the LICENSE file for more information.

### Contact
If you have any questions, feel free to contact me on Discord: `captain_jack_sparrow`
