#!/bin/python3
import asyncio, aiohttp, os, sys, json
from dotenv import load_dotenv
import argparse

async def main():
    parser = argparse.ArgumentParser(description="Script to delete all a user's messages in a given Discord server")
    parser.add_argument("-u", "--channel-url", type=str, help="URL of a channel in the server", required=True)
    args=parser.parse_args()

    # reading Discord token from the .env file. should be in the format `DISCORD_TOKEN=<insert_discord_token_here>`
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        raise Exception("DISCORD_TOKEN environment variable is not set")

    guild = args.channel_url.split("/")[-2] # "guild" is discord's internal name for servers
    channel = args.channel_url.split("/")[-1]

    # setting host URL based on whether the channel is in @me or in a guild/server
    if (guild == "@me"):
        guild_url   = "https://discord.com/api/v9/channels/" + channel
        channel_url = guild_url
    else: 
        guild_url   = "https://discord.com/api/v9/guilds/"   + guild
        channel_url = "https://discord.com/api/v9/channels/" + channel

    headers = {
        "accept": "*/*",
        "accept-language": "en-GB,en;q=0.8",
        "authorization": token,
        "origin": "https://discord.com",
        "priority": "u=1, i",
        "referer": "https://discord.com/channels/" + guild + "/" + channel,
    }

    offset = 0      # messages are received from the API in batches of 25, so need to keep track of the offset when requesting to make sure no old messages are received
    to_delete = []  # list of messages to be deleted 

    # starting asynchronous context manager to keep all HTTP requests in the one session
    async with aiohttp.ClientSession() as session:
        # getting the user ID pertaining to the Discord token that the script is using
        async with session.request("GET", "https://discord.com/api/v9/users/@me", headers=headers) as response:
            try:
                user = (await response.json())["id"]
            except KeyError: 
                raise Exception("User ID not found in JSON response. Actual JSON response: " + json.dumps(await response.json(), indent=4))

        # looping to fill up list of messages by requesting batches of messages from the API and adding them to the list
        while True:
            # searching for the next 25 messages from the user in question from the Discord API (Discord returns search results in batches of 25)
            async with session.request("GET", guild_url + "/messages/search?author_id=" + str(user) + "&offset=" + str(offset), headers=headers) as response:

                # if the channel is not yet indexed, looping until Discord indexes it
                while True:
                    # if the search returned an array (empty or otherwise) of messages, breaking
                    if "messages" in (await response.json()):
                        batch = (await response.json())["messages"]
                        break 
                    # assuming that a "Try again later" message was received if not messages, so trying to wait the requested interval.
                    # if some other message was received and no interval was in the response, exiting with an error message
                    else:
                        try:
                            print(json.dumps(await response.json(), indent=4))
                            print("Channel is not yet indexed. Waiting for " + str((await response.json())["retry_after"]) + "s as requested by the Discord API")
                            await asyncio.sleep((await response.json())["retry_after"])
                        except KeyError:
                            raise Exception("Unexpected JSON response received from Discord after trying to search for messages. Actual JSON response: " + json.dumps(await response.json(), indent=4))

            # if the batch is not empty, adding the messages in batch to the list of messages to be deleted
            if batch:
                to_delete += batch
                offset += 25

            # if the batch is empty, there are no more messages to be added to the to_delete list so breaking out of the search loop
            else: break

        deleted_messages = 0    # count of the number of messages that have been deleted
        print("Deleting " + str(len(to_delete)) + " message(s)")
        # looping through messages in to_delete list and sending the request to delete them one by one
        for message in to_delete:
            # if message is a system message
            if message[0]["type"] == 1:
                break

            # looping infinitely until message is successfully deleted
            while True:
                async with session.request("DELETE", "https://discord.com/api/v9/channels/" + message[0]["channel_id"] + "/messages/" + message[0]["id"], headers=headers) as response:
                    # if successful status returned, printing success message and breaking out of loop
                    if 200 <= response.status <= 299:
                        deleted_messages += 1
                        print("Successfully deleted message " + str(deleted_messages) + " of " + str(len(to_delete)))
                        break;

                    # else if "forbidden" status returned, continuing
                    elif response.status == 403:
                        print("Failed to delete message: Error 403 – " + (await response.json())["message"])
                        # deleted_messages += 1
                        break

                    # else if "Too many requests" status returned, waiting for the amount of time specified
                    elif response.status == 429:
                        print("Rate limited by Discord. Waiting for " + str((await response.json())["retry_after"]) + "s")
                        await asyncio.sleep((await response.json())["retry_after"])

                    # otherwise, printing out json response and aborting
                    else:
                        print(response.status)
                        raise Exception("Unexpected HTTP status code received. Actual response: " + json.dumps(await response.json(), indent=4))


if __name__ == "__main__":
    asyncio.run(main())
