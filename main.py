import discord
import sys
import asyncio

client = discord.Client()


@client.event
async def on_ready():
    """Print a startup message."""
    print(str(client.user) + ' is online.')  # Prints operational message.


@client.event
async def on_message_edit(before, after):
    """Main function for handling message edit events."""
    x = await client.pins_from(before.channel)
    pinned_ids = [message.id for message in x]
    attachments = before.attachments

    if len(pinned_ids) == 50:
        oldest_pin = await client.get_message(before.channel, pinned_ids[-1])
        await client.unpin_message(oldest_pin)

    if before.author != client.user and before.id in pinned_ids  \
            and before.author.bot is False and before.content != '':
        name = before.author.display_name
        avatar = before.author.avatar_url
        pin_content = before.content

        emb = discord.Embed(
            description=pin_content,
            color=0xcf1c43)  # Initalizes embed with description pin_content.
        emb.set_author(
            name=name,
            icon_url=avatar,
            url='https://discordapp.com/channels/{0}/{1}/{2}'.format(
                '260272353118912522', before.channel.id, before.id)
        )  # Sets author and avatar url of the author of pinned message.

        # Set attachemnt image url as embed image if it exists
        if attachments:
            img_url = attachments[0]['url']
            emb.set_image(url=img_url)

        # Sets footer as the channel the message was sent and pinned in.
        emb.set_footer(text='Sent in #{}'.format(before.channel))

        # Finally send the message to the pin archiving channel.
        await client.send_message(
            discord.Object(id='538545784497504276'), embed=emb)


@client.event
async def on_reaction_add(reaction, user):
    if reaction.emoji == '📌':
        if reaction.count == 7:
            try:
                await client.pin_message(reaction.message)
            # This exception thrown when pins are full, usually
            except discord.errors.HTTPException:
                x = await client.pins_from(reaction.message.channel)
                pinned_ids = [message.id for message in x]
                oldest_pin = await client.get_message(reaction.message.channel,
                                                      pinned_ids[-1])
                await client.unpin_message(oldest_pin)
                await client.pin_message(reaction.message)


@client.event
async def on_message(message):
    """Handle commands."""
    # FIXME: remove the bare except
    try:
        user_roles = [role.name for role in message.author.roles]
    except:  # NOQA
        pass

    # If the message is not from a bot, the following code is executed.
    if message.author != client.user:
        if message.content.startswith('+lastpin'):
            x = await client.pins_from(message.channel)
            pinned_names = [message.author.display_name for message in x]
            pinned_avatars = [message.author.avatar_url for message in x]
            pinned_content = [message.content for message in x]
            attachments = [message.attachments for message in x]

            # Description is the contents of the first pinned message
            emb = discord.Embed(description=pinned_content[0], color=0xcf1c43)
            # Match author information from pinned message
            emb.set_author(
                name=pinned_names[0],
                icon_url=pinned_avatars[0],
                url='https://discordapp.com/channels/{0}/{1}/{2}'.format(
                    '260272353118912522', x[0].channel.id, x[0].id))

            # Handle attachments in pins
            if attachments[0]:
                img_content = attachments[0][0]['url']
                emb.set_image(url=img_content)

            await client.send_message(message.channel, embed=emb)

        if message.content == '+status':
            emb = discord.Embed(description='Online.', color=0xcf1c43)
            await client.send_message(message.channel, embed=emb)

        if message.content.startswith('+del'):
            # Only allow Administrators, Moderators, and bot author to delete
            if ('Administrator' in user_roles or 'Moderator' in user_roles
                    or message.author.id == '357652932377837589'):
                # Fetch the last message in the channel #pin-archive and delete
                async for message in client.logs_from(
                        discord.Object(id='538545784497504276'), limit=1):
                    last_message = message
                await client.delete_message(last_message)

        if message.content.startswith('+archive'):
            # See above
            if ('Administrator' in user_roles or 'Moderator' in user_roles
                    or message.author.id == '357652932377837589'):
                try:
                    # Extract the message ID
                    id_to_archive = message.content.replace('+archive ', '')
                    msg = await client.get_message(message.channel,
                                                   id_to_archive)
                    attachments = msg.attachments

                    name = msg.author.display_name
                    avatar = msg.author.avatar_url
                    pin_content = msg.content
                    message_channel = msg.channel

                    emb = discord.Embed(
                        description=pin_content, color=0xcf1c43)
                    emb.set_author(
                        name=name,
                        icon_url=avatar,
                        url='https://discordapp.com/channels/{0}/{1}/{2}'.
                        format('260272353118912522', msg.channel.id, msg.id))

                    # Handle attachments
                    if attachments:
                        img_content = attachments[0]['url']
                        emb.set_image(url=img_content)

                    emb.set_footer(text='Sent in #{}'.format(message_channel))
                    await client.send_message(
                        discord.Object(id='538545784497504276'), embed=emb)
                    await asyncio.sleep(10)
                    await client.delete_message(message)
                    # Deletes the initial command message.

                # If this exception is thrown, it usually means we had an
                # invalid message ID.
                except discord.errors.HTTPException:
                    emb = discord.Embed(
                        description='Error: Message not found, try again.',
                        color=0xcf1c43)
                    await client.send_message(message.channel, embed=emb)

        if message.content.startswith('+help'):
            help_message = '''
       __**Information**__:

        This bot was made by @Nitr0us#5090, if you have any questions or require support please contact him.

       __**Features**__:

        **1)** Last Pinned Message:
        Usage: +lastpin
        Purpose: Displays the last pinned message of the current channel.

        **2)** Archive Pinned Messages (Automatic):
        Usage: Automatic
        Usage Alternate: Culminate 7 pin reactions on a message.
        Purpose: To archive all pinned messages to #pin-archive.

        **3)** Archive Messages (Manual)
        Usage: +archive <messageid>
        Permission: Administrators & Moderators
        Purpose: To archive a message to #pin-archive, regardless whether the message is pinned.

        **4)** Status:
        Usage: +status
        Purpose: Notifies you if the bot is online.

        **5)** Delete:
        Usage: +del
        Permission: Administrators & Moderators
        Purpose: To delete the last pinned message in #pin-archive.
      '''
            emb = discord.Embed(description=help_message, color=0xcf1c43)
            await client.send_message(message.channel, embed=emb)


client.run(sys.argv[1])  # Runs bot with token as system argument.
client.close()
