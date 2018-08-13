#VoteBot v1.0

import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import time
import json

token = "TOKEN"


server_id = "468124255545196545"

voting_channel_id = "478700629590802442"
results_channel_id = "474000090290323456"

storage_server_id = "478225989785223177"
storage_channel_id = "478358905240551424"


admin_role_ids = ["478605537362182145"]

maximum_bills_per_member = 1
bill_duration = 20		#in seconds
voting_roles_dict = {"477082018031861762": 1, "477082082007318528": 1.5, "477082152819752971": 2}		#edit role IDs and voting power here. format is:   "role_id": voting_power   (each one is separated by a comma)





async def get_latest_bot_message(storage_channel_object):

	message_object_found = False
	async for message_object in bot.logs_from(storage_channel_object):
		if message_object.author.id == bot.user.id:
			message_object_found = True
			return message_object
			break
	if not message_object_found:
		return None

async def save_data(data_to_save):

	global storage_server_id
	global storage_channel_id

	storage_server_object = bot.get_server(storage_server_id)
	storage_channel_object = storage_server_object.get_channel(storage_channel_id)

	message_object = await get_latest_bot_message(storage_channel_object)

	data_to_save = json.dumps(data_to_save)

	if message_object == None:
		await bot.send_message(storage_channel_object, data_to_save)
	else:
		await bot.edit_message(message_object, new_content=data_to_save)

async def load_data():

	global storage_server_id
	global storage_channel_id

	storage_server_object = bot.get_server(storage_server_id)
	storage_channel_object = storage_server_object.get_channel(storage_channel_id)

	message_object = await get_latest_bot_message(storage_channel_object)

	if message_object == None:
		return None
	else:
		loaded_data = json.loads(message_object.content)
		return loaded_data





async def vote_timer():
	await bot.wait_until_ready()

	while not bot.is_closed:
		await asyncio.sleep(2)

		for key in current_bills:
			if (current_bills[key]["time_created"] + bill_duration) <= time.time():

				#vote_ends

				results_channel_object = bot.get_server(server_id).get_channel(results_channel_id)

				if current_bills[key]["yes_votes"] <= current_bills[key]["no_votes"]:
					bill_result = "Failure"
					bill_colour = 0xd20f0f
				else:
					bill_result = "Success"
					bill_colour = 0x27da07

				embed=discord.Embed(title="[{0}] Vote finished!\nResult: {1}".format(str(key), bill_result), description=current_bills[key]["bill"], color=bill_colour)
				embed.add_field(name="Ayes", value=str(current_bills[key]["yes_votes"]), inline=True)
				embed.add_field(name="Nays", value=str(current_bills[key]["no_votes"]), inline=True)
				embed.set_footer(text="Vote by: {0}".format(current_bills[key]["member_name"]))
				await bot.send_message(results_channel_object, embed=embed)

				del current_bills[key]
				all_data["current_bills"] = current_bills
				await save_data(all_data)

				break





bot = discord.Client()


@bot.event
async def on_ready():

	global server_id
	global commands_channel_id

	global votes_awaiting_confirmation
	global current_bills
	global current_vote_number
	global members_bill_count
	global all_data


	await bot.wait_until_ready()
	print (bot.user.name + " is ready")
	print ("ID: " + bot.user.id)

	await bot.change_presence(game=discord.Game(name="Under Development"))

	all_data = await load_data()
	if all_data == None:
		all_data = {
			"current_bills" : {},
			"current_vote_number" : 0,
			"members_bill_count" : {}
		}

	votes_awaiting_confirmation = {}
	current_bills = all_data["current_bills"]
	current_vote_number = all_data["current_vote_number"]
	members_bill_count = all_data["members_bill_count"]



@bot.event
async def on_message(message):

	global votes_awaiting_confirmation
	global current_bills
	global current_vote_number
	global members_bill_count
	global all_data



	voting_channel_object = bot.get_server(server_id).get_channel(voting_channel_id)



	message_command = message.content.strip().lower()

	if message.author.id != bot.user.id:



		if (message_command[:12] == "!list roles ") or (message_command == "!list roles"):
			list_sender = ""
			for role_object in message.server.roles:
				if not (role_object.is_everyone):
					list_sender = list_sender + "\n{0} ({1})".format(role_object.name, role_object.id)
			await bot.send_message(message.channel, list_sender)



		elif (message_command[:12] == "!start vote ") or (message_command == "!start vote"):

			if not (message.author.id in votes_awaiting_confirmation):

				if message.author.id in members_bill_count:
					temp_member_bill_count = members_bill_count[message.author.id]
				else:
					temp_member_bill_count = 0

				if temp_member_bill_count < maximum_bills_per_member:

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
					await bot.send_message(message.channel, "You have reached your maximum bill count of {0}!".format(str(maximum_bills_per_member)))

			else:
				await bot.send_message(message.channel, "You have already started a vote that is awaiting confirmation!")



		elif (message_command[:9] == "!confirm ") or (message_command == "!confirm"):
			if message.author.id in votes_awaiting_confirmation:
				if votes_awaiting_confirmation[message.author.id]["channel_id"] == message.channel.id:

					current_vote_number += 1
					all_data["current_vote_number"] = current_vote_number
					await save_data(all_data)
					current_bills[current_vote_number] = {"member_id" : message.author.id, "member_name" : ("{0}#{1}".format(message.author.name, message.author.discriminator)), "bill" : votes_awaiting_confirmation[message.author.id]["bill"], "time_created" : time.time(), "yes_votes" : 0.0, "no_votes": 0.0, "members_voted": {}}
					all_data["current_bills"] = current_bills
					await save_data(all_data)

					if message.author.id in members_bill_count:
						members_bill_count[message.author.id] += 1
					else:
						members_bill_count[message.author.id] = 1
					all_data["members_bill_count"] = members_bill_count
					await save_data(all_data)



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



		elif (message_command[:10] == "!vote aye ") or (message_command == "!vote aye") or (message_command[:10] == "!vote nay ") or (message_command == "!vote nay"):
			is_integer = True
			try:
				bill_number_chosen = int(message.content[10:])
			except Exception:
				is_integer = False

			if ((message_command != "!vote aye") or (message_command != "!vote nay")) and (is_integer):
				if bill_number_chosen in current_bills:


					member_can_vote_bool = True
					member_has_voted_bool = False
					if message.author.id in current_bills[bill_number_chosen]["members_voted"]:
						member_has_voted_bool = True
						if (message_command[:10] == "!vote aye ") and (current_bills[bill_number_chosen]["members_voted"][message.author.id]["vote"] == "aye"):
							member_can_vote_bool = False
						elif (message_command[:10] == "!vote nay ") and (current_bills[bill_number_chosen]["members_voted"][message.author.id]["vote"] == "nay"):
							member_can_vote_bool = False


					if member_can_vote_bool:
						vote_role_count = 0
						for role_object in message.author.roles:
							if role_object.id in voting_roles_dict:
								vote_role_count += 1
						if vote_role_count == 1:
							for role_object in message.author.roles:
								if role_object.id in voting_roles_dict:
									if message_command[:10] == "!vote aye ":
										if member_has_voted_bool:
											current_bills[bill_number_chosen]["no_votes"] -= float(current_bills[bill_number_chosen]["members_voted"][message.author.id]["vote_weight"])
										current_bills[bill_number_chosen]["yes_votes"] += float(voting_roles_dict[role_object.id])
										current_bills[bill_number_chosen]["members_voted"][message.author.id] = {"vote": "aye", "vote_weight": voting_roles_dict[role_object.id]}
										all_data["current_bills"] = current_bills
										await save_data(all_data)
										if member_has_voted_bool:
											await bot.send_message(message.channel, "You changed your vote to aye on bill number {0}:\n*{1}*".format(str(bill_number_chosen), current_bills[bill_number_chosen]["bill"]))
										else:
											await bot.send_message(message.channel, "You voted aye on bill number {0}:\n*{1}*".format(str(bill_number_chosen), current_bills[bill_number_chosen]["bill"]))
									elif message_command[:10] == "!vote nay ":
										if member_has_voted_bool:
											current_bills[bill_number_chosen]["yes_votes"] -= float(current_bills[bill_number_chosen]["members_voted"][message.author.id]["vote_weight"])
										current_bills[bill_number_chosen]["no_votes"] += float(voting_roles_dict[role_object.id])
										current_bills[bill_number_chosen]["members_voted"][message.author.id] = {"vote": "nay", "vote_weight": voting_roles_dict[role_object.id]}
										all_data["current_bills"] = current_bills
										await save_data(all_data)
										if member_has_voted_bool:
											await bot.send_message(message.channel, "You changed your vote to nay on bill number {0}:\n*{1}*".format(str(bill_number_chosen), current_bills[bill_number_chosen]["bill"]))
										else:
											await bot.send_message(message.channel, "You voted nay on bill number {0}:\n*{1}*".format(str(bill_number_chosen), current_bills[bill_number_chosen]["bill"]))

						elif vote_role_count == 0:
							await bot.send_message(message.channel, "You cannot vote without a voting role!")
						else:
							await bot.send_message(message.channel, "You have too many voting roles, you can only vote when you have one voting role!")

					else:

						await bot.send_message(message.channel, "You already voted {0} for bill number {1}:\n*{2}*".format(current_bills[bill_number_chosen]["members_voted"][message.author.id]["vote"], str(bill_number_chosen), current_bills[bill_number_chosen]["bill"]))

				else:
					await bot.send_message(message.channel, "Invalid bill number - not an active bill")
			else:
				list_sender = "You must specify which bill you want to vote for by it's number -> *!vote aye [number]*\nCurrent bills:\n"
				if len(current_bills) > 0:
					for existing_bill_number in current_bills:
						list_sender = list_sender + "\n[{0}] {1}".format(str(existing_bill_number), current_bills[existing_bill_number]["bill"])
					await bot.send_message(message.channel, list_sender)
				else:
					list_sender = list_sender + "\nThere are currently no bills!"
					await bot.send_message(message.channel, list_sender)



		elif (message_command[:8] == "!status ") or (message_command == "!status"):
			if not (message_command == "!status"):
				if int(message.content[8:]) in current_bills:
					await bot.send_message(message.channel, "Bill [{0}] has:\n{1} Ayes\n{2} Nays".format(str(message.content[8:]), current_bills[int(message.content[8:])]["yes_votes"], current_bills[int(message.content[8:])]["no_votes"]))
				else:
					await bot.send_message(message.channel, "Invalid bill number - not an active bill")
			else:
				await bot.send_message(message.channel, "You need to specify which bill by it's number -> *!status [bill number]*")



		elif (message_command[:12] == "!list roles ") or (message_command == "!list roles"):
			list_sender = ""
			for role_object in message.server.roles:
				if not (role_object.is_everyone):
					list_sender = list_sender + "\n{0} ({1})".format(role_object.name, role_object.id)
			await bot.send_message(message.channel, list_sender)



		elif (message_command[:6] == "!help ") or (message_command == "!help"):
			embed=discord.Embed(title="Current commands:", color=0x2f25e9)
			embed.add_field(name="!start vote *[bill]*", value="Starts a vote", inline=False)
			await bot.send_message(message.channel, embed=embed)



		if any(role_id in admin_role_ids for role_id in (role_object.id for role_object in message.author.roles)):



			if (message_command[:12] == "!clearbills ") or (message_command == "!clearbills"):
				if not (message_command == "!clearbills"):
					if message.content[12:] in (member_object.mention for member_object in message.server.members):
						member_object = message.server.get_member((message.content[12:])[2:20])
						if member_object.id in members_bill_count:
							del members_bill_count[member_object.id]
							all_data["members_bill_count"] = members_bill_count
							await save_data(all_data)
						await bot.send_message(message.channel, "Bill number for user {0}#{1} has been reset!".format(member_object.name, member_object.discriminator))
					else:
						await bot.send_message(message.channel, "Not a valid member!")
				else:
					await bot.send_message(message.channel, "You need to specify which member you want to clear! -> *!clearbills @member*")



bot.loop.create_task(vote_timer())
bot.run(token)
