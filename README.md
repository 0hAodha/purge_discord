# DISCLAIMER 
**The author of this script takes ABSOLUTELY NO RESPONSIBILITY for your own actions or usage of the script, and if you do choose to use this script, you do so ENTIRELY AT YOUR OWN RISK.**

This script uses Discord's undocumented user API, which has no official public documentation and is not intended to be used by anyone other than Discord's own internal developers. It is a *self-botting* script, meaning that it automates actions acting as though the user themselves were performing them manually. 

**Self-botting is explicitly forbidden by the Discord Trust & Safety Team and can result in an account termination if found**. Therefore, it's not unlikely that **using this script may incur a ban on your account.** Discord's explicit condemnation of self-botting can be found [here](https://support.discord.com/hc/en-us/articles/115002192352-Automated-user-accounts-self-bots-)

# About
`purge_discord.py` is a Discord self-botting Python script that allows the user to programmatically mass-delete all of the messages that they sent in a given Discord channel, including servers, DMs, & group chats via the Discord user API. It is primarily designed to be ran from a command-line, with the URL or ID of a channel being passed to the script as arguments. 

The purpose of the script is to enhance the user's control over their private information on Discord. Discord is not a social media platform with strong privacy practices, and I firmly believe that an individual should have the right to remove their data from any given platform quickly & easily at will. At present, there is no way to delete all of your messages from Discord. Not even deleting your account will remove your messages from the platform, and they will still be visible permanently. Deleting your account is in this sense worse for your privacy, as you lose control over your messages; Once you delete your account, you will permanently lose the ability to delete any of your messages, meaning that any information you revealed in those messages is now permanently public information. 

The URL feature was added to make it easy for me to embed the functionality of this script into my browser of choice, [qutebrowser](https://qutebrowser.org/) via a keybinding, as I use Discord almost exclusively from my browser. When I press the keybinding `,p`, qutebrowser runs the script, passing the URL of the webpage that I'm currently as an argument.

# Usage 
## Pre-requisites 
- `python-3.7` or later
- Python libraries:
    - `asyncio`
    - `aiohttp` 
    - `dotenv`

You will also need to know to your **Discord token**. The steps to find this can be found [here](https://www.howtogeek.com/879956/what-is-a-discord-token-and-how-do-you-get-one/). Note that your Discord token gives anyone who has it access to your account, so ensure that you **do not share your Discord token with anyone, under any circumstances.**

## Setup
1. Clone this repository. 
```bash
git clone https://github.com/0hAodha/purge_discord
```
2. Navigate to the newly created `purge_discord` directory on your machine. 
3. Edit the `.env` file with your text editor of choice and replace the placeholder value of the `DISCORD_TOKEN` variable with your actual Discord token. It should look something like the following: 
```dotenv
DISCORD_TOKEN=AAAAAAAAAAAAAAAAAAAAAAAAAA.BBBBBB.CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
```

## Running the Script
To get usage information, you can run the script with no arguments. The usage information will be displayed every time that the script is called with valid number of arguments or with unknown flags. 
```bash
./purge_discord.py 
```
The output should be as follows:
```
Usage: ./purge_discord.py [OPTION]... [ARGUMENT]...
Delete all the user's messages in the given Discord channel.
The channel may be specified using one of the following options:
	-i, --channel-id        delete messages in the channel corresponding to the supplied ID
	-u, --channel-url       delete messages in the channel corresponding to the supplied URL
```
The script can be ran either by supplying the channel ID or the channel URL. To get the ID of a channel, right-click on it in Discord and click the "Copy channel ID" option in the context menu. The ID can then be passed to the script as follows:
```bash
./purge_discord.py -i 1234567890123456789
```
Alternatively, the script can be ran by supplying the channel URL. This is simply the URL that is shown in the address bar of your browser when you navigate to that channel in the web version of the Discord application. The URL can be passed to the script as follows:
```bash
./purge_discord.py -u https://discord.com/channels/@me/1234567890123456789
```
