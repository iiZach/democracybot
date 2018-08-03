import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio

token = "TOKEN"


server_id = "474307455837536286"

commands_channel_id = "474307489542963201"
voting_channel_id = "474325498994884610"


votes_awaiting_confirmation = {}
current_votes = {}
current_vote_number = 0


Client = discord.Client()
bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
	await bot.wait_until_ready()
	print (bot.user.name + " is ready")
	print ("ID: " + bot.user.id)
	
	await bot.change_presence(game=discord.Game(name="Under Development"))
	
@bot.event
async def on_message(message):

	global votes_awaiting_confirmation
	global current_votes
	global current_vote_number
	


  voting_channel_object = bot.get_server(server_id).get_channel(voting_channel_id)


	message_command = message.content.strip().lower()

	if message.author.id != bot.user.id:
		
		
			
		if (message_command[:12] == "!start vote ") or (message_command == "!start vote"):
		
			if not (message.author.id in votes_awaiting_confirmation):
		
				if message_command != "!start vote":
					votes_awaiting_confirmation[message.author.id] = {"channel_id" : message.channel.id, "bill" : message.content[12:]}
					embed=discord.Embed(title="Vote started by {0}!".format(message.author.display_name), description=message.content[12:], color=0x3aed21)
					embed.set_author(name="{0}#{1}".format(message.author.name, message.author.discriminator), icon_url=message.author.avatar_url)
					list_sender = "Type *!confirm* to confirm or *!cancel* to cancel the vote.\nIf you don't type either the vote will automatically be cancelled in 60 seconds.\nThe vote will look like this:"
					await bot.send_message(message.channel, list_sender, embed=embed)
					
					await asyncio.sleep(60)
					
					if message.author.id in votes_awaiting_confirmation:
						del votes_awaiting_confirmation[message.author.id]
					
				else:
					await bot.send_message(message.channel, "You can't have a blank bill! Command usage -> *!start vote [bill]*")
			
			else:
				await bot.send_message(message.channel, "You have already started a vote that is awaiting confirmation!")
			
	
			
		elif (message_command[:9] == "!confirm ") or (message_command == "!confirm"):
			if message.author.id in votes_awaiting_confirmation:
				if votes_awaiting_confirmation[message.author.id]["channel_id"] == message.channel.id:
					
					current_vote_number += 1
					current_votes[current_vote_number] = {"member_id" : message.author.id, "bill" : votes_awaiting_confirmation[message.author.id]["bill"], "yes_votes" : 0, "no_votes" : 0}
					
					await bot.send_message(message.channel, "Vote confirmed!")
					
					embed=discord.Embed(title="[{0}] Vote started by {1}!".format(str(current_vote_number), message.author.display_name), description=votes_awaiting_confirmation[message.author.id]["bill"], color=0x3aed21)
					embed.set_author(name="{0}#{1}".format(message.author.name, message.author.discriminator), icon_url=message.author.avatar_url)
					await bot.send_message(voting_channel_object, embed=embed)
					del votes_awaiting_confirmation[message.author.id]
		
		
		
		elif (message_command[:8] == "!cancel ") or (message_command == "!cancel"): 
			if message.author.id in votes_awaiting_confirmation:
				if votes_awaiting_confirmation[message.author.id]["channel_id"] == message.channel.id:
					await bot.send_message(message.channel, "Vote cancelled!")
				
					del votes_awaiting_confirmation[message.author.id]
			
			
			
		elif (message_command[:6] == "!help ") or (message_command == "!help"):
			embed=discord.Embed(title="Current commands:", color=0x2f25e9)
			embed.add_field(name="!start vote *[bill]*", value="Starts a vote", inline=False)
			await bot.send_message(message.channel, embed=embed)
			
			

bot.run(token)
