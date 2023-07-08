# DISCLAIMER 
**The author of this script takes ABSOLUTELY NO RESPONSIBILITY for your own actions or usage of the script, and if you do choose to use this script, you do so ENTIRELY AT YOUR OWN RISK.**

This script uses Discord's undocumented user API, which has no official public documentation and is not intended to be used by anyone other than Discord's own internal developers. It is a *self-botting* script, meaning that it automates actions acting as though the user themselves were performing them manually. 

**Self-botting is explicitly forbidden by the Discord Trust & Safety Team and can result in an account termination if found**. Therefore, it's not unlikely that **using this script may incur a ban on your account.** Discord's explicit condemnation of self-botting can be found [here](https://support.discord.com/hc/en-us/articles/115002192352-Automated-user-accounts-self-bots-)

# Usage 
## Pre-requisites 
- `python-3.7` or later
- Python libraries:
    - `asyncio`
    - `aiohttp` 
    - `os`
    - `sys`
    - `json`
    - `dotenv`

You will also need to know to your **Discord token**. The steps to find this can be found [here](https://www.howtogeek.com/879956/what-is-a-discord-token-and-how-do-you-get-one/). Note that your Discord token gives anyone who has it access to your account, so ensure that you **do not share your Discord token with anyone, under any circumstances.**

## Setup
1. Clone this repository. 
```
git clone https://github.com/0hAodha/purge_discord
```
2. Navigate to the newly created `purge_discord` directory on your machine. 
3. Edit the `.env` file and replace the `DISCORD_TOKEN` placeholder value with your actual Discord token. It should look something like the following: 
```dotenv
DISCORD_TOKEN=AAAAAAAAAAAAAAAAAAAAAAAAAA.BBBBBB.CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
```

