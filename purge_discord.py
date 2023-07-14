#!/bin/python3
import asyncio, aiohttp, os, sys, json
from dotenv import load_dotenv


# method to print out the usage instructions if the program was called incorrectly
def usage():
    sys.exit("Usage: ./purge_discord.py [OPTION]... [ARGUMENT]...\n"
             "Delete all the user's messages in the given Discord channel.\n"
             "The channel may be specified using one of the following options:\n"
             "\t-i, --channel-id        delete messages in the channel corresponding to the supplied ID\n"
             "\t-u, --channel-url       delete messages in the channel corresponding to the supplied URL")


async def main():
    # parsing command-line arguments
    if len(sys.argv) == 3:
        if sys.argv[1] == "-i" or sys.argv[1] == "--channel-id":
            channel = sys.argv[2]
        elif sys.argv[1] == "-u" or sys.argv[1] ==  "--channel-url":
            channel = sys.argv[2].split("/")[-1]    # parsing the channel ID from the URL by splitting it on `/` and taking the last segment
        else:
            usage()
    else:
        usage()

    # reading Discord token from the .env file. should be in the format `DISCORD_TOKEN=<insert_discord_token_here>`
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        sys.exit("DISCORD_TOKEN environment variable is not set")

    host = "https://discord.com/api/v10"
    headers = {"authorization": token}
    offset = 0      # messages are received from the API in batches of 25, so need to keep track of the offset when requesting to make sure no old messages are received
    to_delete = []  # list of messages to be deleted 

    # starting asynchronous context manager to keep all HTTP requests in the one session
    async with aiohttp.ClientSession() as session:
        # getting the user ID pertaining to the Discord token that the script is using
        async with session.request("GET", host + "/users/@me", headers=headers) as response:
            try:    
                user = (await response.json())["id"]
            except KeyError: 
                sys.exit("User ID not found in JSON response. Actual JSON response: " + await response.json())

        # looping to fill up list of messages by requesting batches of messages from the API and adding them to the list
        while True:
            # searching for the next 25 messages from the user in question from the Discord API (Discord returns search results in batches of 25)
            async with session.request("GET", host + "/channels/" + str(channel) + "/messages/search?author_id=" + str(user) + "&offset=" + str(offset), headers=headers) as response:

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
                            print("Channel is not yet indexed. Waiting for " + str((await response.json())["retry_after"]) + "s as requested by the Discord API")
                            await asyncio.sleep((await response.json())["retry_after"])
                        except KeyError:
                            sys.exit("Unexpected JSON response received from Discord. Actual JSON response: " + await response.json())

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

            # looping infinitely until message is successfully deleted
            while True:
                async with session.request("DELETE", host + "/channels/" + channel + "/messages/" + message[0]["id"], headers=headers) as response:
                    # if successful status returned, printing success message and breaking out of loop
                    if 200 <= response.status <= 299:
                        deleted_messages += 1
                        print("Successfully deleted message " + str(deleted_messages) + " of " + str(len(to_delete)))
                        break;

                    # else if "Too many requests" status returned, waiting for the amount of time specified
                    elif response.status == 429:
                        print("Rate limited by Discord. Waiting for " + str((await response.json())["retry_after"]) + "s")
                        await asyncio.sleep((await response.json())["retry_after"])

                    # otherwise, printing out json response and aborting
                    else:
                        sys.exit("Unexpected HTTP status code received. Actual response: " + json.dumps(response.json()))


if __name__ == "__main__":
    asyncio.run(main())
