#!/bin/python3
import asyncio, aiohttp, os, sys, json
from asyncio.base_events import time
from dotenv import load_dotenv
import argparse

BASE_URL = "https://discord.com/api/v9/"

def read_token():
    """
    Reads the user's Discord token from the environment file.
    File should be in the format: `DISCORD_TOKEN=<insert_discord_token_here>`.

    Returns:
        str: Discord token specified in environment file.
    """

    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        raise Exception("DISCORD_TOKEN environment variable is not set")

    return token

def split_channel_url(channel_url):
    """
        Split the channel URL into the guild ID and channel ID.
        Note that 'guild' is just Discord's internal name for 'server'.

        Args:
            channel_url (str): the channel URL.

        Returns:
            string: the guild ID.
            string: the channel ID.
    """

    split_string = channel_url.split("/")

    guild_id = split_string[-2]
    channel_id = split_string[-1]

    return guild_id, channel_id

def get_guild_url(guild_id, channel_id):
    """
    Get the guild URL based off the guild ID and channel ID.

    Args:
        guild_id (str): the guild ID.
        channel_id (str): the channel ID.

    Returns:
        str: the guild URL.
    """

    if (guild_id == "@me"):
        guild_url   = "https://discord.com/api/v9/channels/" + channel_id
    else: 
        guild_url   = "https://discord.com/api/v9/guilds/"   + guild_id

    return guild_url

def get_headers(token):
    """
    Returns a dictionary object containing the headers with which to make API requests, including the authorisation token.

    Args:
        token (string): the user's Discord token.

    Returns:
        dict: A dictionary containing the headers.
    """

    headers = {
        "authorization": token,
    }

    return headers

async def get_user_id(session, headers):
    """
    Fetches the Discord user ID of the user's whose Discord token has been supplied.

    Args:
        session (aiohttp.ClientSession): the session to make the request with.
        headers (dictionary): the headers with which to make the GET request.

    Returns:
        string: the (numerical) user ID of the Discord user.
    """

    async with session.request("GET", BASE_URL + "users/@me", headers=headers) as response:
        user_id = (await response.json())["id"]

    return user_id

async def get_all_messages(session, headers, guild_url, user_id):
    """
    Get a list of all of the user's messages in the guild.

    Args:
        session (aiohttp.ClientSession): the session to make the requests with.
        headers (dictionary): the headers with which to make the requests.
        guild_url (str): the URL of the guild from which to fetch all the messages.
        user_id (str): the ID of the user's whose messages are being fetched.

    Returns:
        list: a list of all the user's messages in the guild.
    """

    messages = []

    # The Discord API returns messages in batches of 25, so an offset is used to define from which starting point to return the previous 25 messages.
    offset = 0

    while True:
        request_url = guild_url + "/messages/search?author_id=" + user_id + "&offset=" + str(offset)

        async with session.request("GET", request_url, headers=headers) as response:

            # If the channel is not yet indexed, may be asked to try again later, so loop until messages are returned.
            while True:

                # Break if the request returned a list (empty or otherwise) of messages.
                if "messages" in (await response.json()):
                    batch = (await response.json())["messages"]
                    break 

                else:
                    try:
                        # Assuming that a "Try again later" message was received if no message list was returned
                        time_to_wait = (await response.json())["retry_after"]

                        print("Channel is not yet indexed. Waiting for " + str(time_to_wait) + "s as requested by the Discord API")
                        await asyncio.sleep(time_to_wait)

                    except KeyError:
                        # If some other message was received and no interval was specified in the response, throw an exception.
                        raise Exception("Unexpected JSON response received from Discord after trying to search for messages. Actual JSON response: " + json.dumps(await response.json(), indent=4))

        # If the batch is not empty, add the messages in batch to the list of messages.
        if batch:
            messages += batch
            offset += 25

        # if the batch is empty, there are no more messages to be added to the to_delete list so breaking out of the search loop
        else:
            break

    return messages

async def delete_messages(session, headers, messages):
    """
    Iterates over a list of messages and deletes them.

    Args:
        session (aiohttp.ClientSession): the session to make the requests with.
        headers (dictionary): the headers with which to make the requests.
        messages (list): a list of Discord messages.

    Returns:
        None
    """

    print("Deleting " + str(len(messages)) + " message(s)")

    num_deleted = 0 # The number of messages that have been deleted.

    for message in messages:
        message_url = BASE_URL + "channels/" + message[0]["channel_id"] + "/messages/" + message[0]["id"]

        # Do nothing if the message is a system message (has type = 1).
        if message[0]["type"] == 1:
            break

        # Discord may reject a DELETE request and say to try again, so loop until the message is successfully deleted (or until a break due to a forbidden message).
        while True:

            async with session.request("DELETE", message_url, headers=headers) as response:

                # If successful status code returned, printing success message and breaking out of loop
                if 200 <= response.status <= 299:
                    num_deleted += 1
                    print("Successfully deleted message " + str(num_deleted) + " of " + str(len(messages)))
                    break;

                # Else if "forbidden" status returned, giving up on that message and continuing.
                elif response.status == 403:
                    print("Failed to delete message: Error 403 – " + (await response.json())["message"])
                    break

                # Else if "Too many requests" status returned, waiting for the amount of time specified.
                elif response.status == 429:
                    retry_after = (await response.json())["retry_after"]

                    print("Rate limited by Discord. Waiting for " + str(retry_after) + "s")
                    await asyncio.sleep(retry_after)

                    # Otherwise, printing out JSON response and throwing an exception
                else:
                    print(response.status)
                    raise Exception("Unexpected HTTP status code received. Actual response: " + json.dumps(await response.json(), indent=4))

async def main():
    parser = argparse.ArgumentParser(description="Script to delete all a user's messages in a given Discord server")
    parser.add_argument("-u", "--channel-url", type=str, help="URL of a channel in the server", required=True)
    args=parser.parse_args()

    token = read_token()
    headers = get_headers(token)

    guild_id, channel_id = split_channel_url(args.channel_url)
    guild_url = get_guild_url(guild_id, channel_id)

    # starting asynchronous context manager to keep all HTTP requests in the one session
    async with aiohttp.ClientSession() as session:
        user_id = await get_user_id(session, headers)
        to_delete = await (get_all_messages(session, headers, guild_url, user_id))
        await delete_messages(session, headers, to_delete)


if __name__ == "__main__":
    asyncio.run(main())
