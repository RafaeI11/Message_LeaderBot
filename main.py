from asyncio import events
import discord
import json

client = discord.Client()
minimum = {"value": 20000}  # no idea why this is a dictionary but to lazy to change

try:
    with open("messages.json", "r") as a:
        msg_dic = json.loads(a.read())
except:
    msg_dic = {}


def update_json():
    msg_json = json.dumps(msg_dic, indent=1)
    with open("messages.json", "w") as c:
        c.write(msg_json)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # adds a point to the author everytime a message is sent
    if message.content.startswith(""):
        if str(message.author.id) not in msg_dic:
            msg_dic[str(message.author.id)] = 1
        else:
            msg_dic[str(message.author.id)] += 1

    if message.author.guild_permissions.manage_channels:
        # command to add/update new entries to the leaderboard
        if message.content.startswith("-edit"):
            edit_content = message.content.split()
            try:
                if not edit_content[1].isdigit() or not edit_content[2].isdigit():
                    await message.channel.send("Error: invalid id/number")
                else:
                    msg_dic[edit_content[1]] = int(edit_content[2])
                    update_json()
                    await message.channel.send(
                        f"{edit_content[1]} was saved with {edit_content[2]} messages"
                    )
            except:
                await message.channel.send(
                    "Error: you must input an id and a number of messages"
                )

        # command to delete entries from the leaderboard
        if message.content.startswith("-delete"):
            del_content = message.content.split()
            try:
                msg_dic.pop(del_content[1])
                update_json()
                await message.channel.send(f"{del_content[1]} was deleted")
            except:
                await message.channel.send("Error: invalid id")

        # command to change the minimum amount of messages necessary to appear on the leaderboard
        if message.content.startswith("-minimum"):
            try:
                minimum["value"] = int(message.content.split()[1])
                await message.channel.send(
                    f"Every user with more than {message.content.split()[1]} message will now be displayed on the leadeboard"
                )
            except:
                await message.channel.send("Error: invalid value")

    # help command
    if message.content.startswith("-help"):
        await message.channel.send(
            "`-msglb`: sends the message leaderboard\n`-edit [user_id] [message_number]`: update a user's message number\n`-delete [user_id]`: delete a user from the leaderboard\n`-minimum [value]`: change the minimum amount of messages necessary to appear on the leaderboard (defaults to 20000)\n`-minfo`: shows the current minimum value to appear on the leaderboard"
        )

    # command to print the source link
    if message.content.startswith("-source"):
        await message.channel.send("https://github.com/RafaeI11/Message_LeaderBot")

    # command to print the current value of minimum
    if message.content.startswith("-minfo"):
        await message.channel.send(
            f"The current minimum is {minimum['value']} messages"
        )

    # command to print the message leaderboard
    if message.content.startswith("-msglb"):
        update_json()
        msg_lb = ""
        # sorts the leaderboard by most messages in probably the ugliest way possible
        almost_sorted_msg_dic = sorted(
            msg_dic.items(), key=lambda x: x[1], reverse=True
        )
        sorted_msg_dic = {}

        for item in almost_sorted_msg_dic:
            sorted_msg_dic[str(item[0])] = int(item[1])

        # restricts the leaderboard to only users with more than 20k messages
        for user in sorted_msg_dic:
            if int(sorted_msg_dic[user]) >= minimum["value"]:
                msg_lb += f"{msg_dic[user]}: <@{user}>\n"

        embed = discord.Embed(
            title="Message Leaderboard", color=7419530, description=msg_lb
        )
        await message.channel.send(embed=embed)


@client.event
async def on_message_delete(message):
    msg_dic[str(message.author.id)] -= 1
