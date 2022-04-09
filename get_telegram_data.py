from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.types import PeerChannel
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
import telethon.sync
import yaml
from telegram_classes import *
from utils import save_line_to_json, read_txt_file, save_line_txt_file
import json
import inspect
import datetime
from datetime import date
import numpy as np
import base64
import time
import os
import random

def load_config_variables():
	with open('config.yaml') as f:
		config = yaml.load(f, Loader=yaml.FullLoader)

	return config

def make_folders(config):
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    yesterday = yesterday.strftime("%Y-%m-%d")

    root_path = '{}{}'.format(config['root_path'], yesterday)
    root_path_media = '{}{}/{}'.format(config['root_path'], yesterday, 'media')

    if os.path.isdir(root_path): print('Folder already exists, adding data...')
    else: os.mkdir(root_path)

    #Create folder for media files
    if os.path.isdir(root_path_media): print('Folder already exists, adding data...')
    else: os.mkdir(root_path_media)

    f_users  = os.path.join(root_path, 'telegram_users.json')
    f_messages  = os.path.join(root_path, 'telegram_messages.json')
    f_channels  = os.path.join(root_path, 'telegram_channels.json')
    f_media  = os.path.join(root_path, 'telegram_messages_media.json')
    
    return f_users, f_messages, f_channels, f_media, root_path_media

def connect_telegram_client(config):
	client = TelegramClient(config['user'], config['api_id'], config['api_hash'])
	client.start()
	print("Client Created")

	if not client.is_user_authorized():
		client.send_code_request(config['phone'])
		try: client.sign_in(config['phone'], input('Enter the code: '))
		except SessionPasswordNeededError: client.sign_in(password=input('Password: '))

	return client

def get_channel(client, channel_id):
	entity = PeerChannel(channel_id) if channel_id.isdigit() else channel_id
	
	return client.get_entity(entity)

def get_channel_participants(client, channel):
	offset = 0
	limit = 100
	all_participants = []

	while True:
		participants = client(GetParticipantsRequest(
						channel, ChannelParticipantsSearch(''),
						offset, limit, hash=0))
	  
		if not participants.users: break
		
		all_participants.extend(participants.users)
		offset += len(participants.users)

	return all_participants

def format_item(item):
	item_dict = {}

	for key, value in item.__dict__.items():
		
		if isinstance(value, datetime.datetime):
			item_dict[key] = value.strftime("%Y-%m-%d")
		else:
			item_dict[key] = value.__dict__ if hasattr(value, '__dict__') else value

		try: json.dumps(item_dict[key])
		except: 
			for key_e, value_e in item_dict[key].items():
				if isinstance(value_e, datetime.datetime):
					item_dict[key][key_e] = value_e.strftime("%Y-%m-%d")
				else:
					try: json.dumps(item_dict[key][key_e])
					except: item_dict[key][key_e] = item_dict[key][key_e].decode('UTF-8','ignore')
				
	return item_dict

def get_channel_messages(channel, date_obj, client):
	offset_id = 0
	limit = 100
	all_messages = []
	all_messages_objects = []
	total_messages = 0
	total_count_limit = 0
	
	while True:
		print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
		history = client(GetHistoryRequest(peer=channel, offset_id=offset_id,
											offset_date=datetime.date.today(), add_offset=0,
											limit=limit, max_id=0, min_id=0,
											hash=0))
		
		if not history.messages: break
		messages = history.messages
		
		for message in messages:
			if str(message.date.strftime("%Y-%m-%d")) == str(date_obj):
				all_messages.append(message.to_dict())
				all_messages_objects.append(message)
			else: return all_messages, all_messages_objects

		offset_id = messages[len(messages) - 1].id
		total_messages = len(all_messages)

	return None, None

def validate_data(item_dict, updated_dict):
	for key, value in item_dict.items():
		if isinstance(value, list): updated_dict[key] = check_list_item(value)
		elif isinstance(value, bytes): updated_dict[key] = base64.b64encode(value).decode('utf-8')
		elif isinstance(value, datetime.datetime): updated_dict[key] = value.strftime("%Y-%m-%d")
		elif isinstance(value, dict):
			updated_dict[key] = value
			validate_data(value, updated_dict[key])
		else: updated_dict[key] = value
	
	return updated_dict

def check_list_item(list_item):
	clear_items = list()

	for item in list_item:
		if isinstance(item, dict):
			for key, value in item.items():
				if isinstance(value, bytes):
					item[key] = base64.b64encode(value).decode('utf-8')
				elif isinstance(value, datetime.datetime):
					item[key] = value.strftime("%Y-%m-%d")
				elif isinstance(value, dict):
					item[key] = validate_data(value, {})
				elif isinstance(value, list):
					check_list_item(value)
			clear_items.append(item)
		else:
			clear_items.append(item)

	return clear_items

def format_message_item(media_item):
	item_dict = {}
	
	if isinstance(media_item, dict): validate_data(media_item, item_dict)
	else: validate_data(media_item.__dict__, item_dict)
	
	return item_dict

def save_message_media(message, f_media):
	media = Message_media(**message)
	media_dict = format_message_item(media.__dict__)
	save_line_to_json(media_dict, f_media)

	return media.internal_id

def dowload_media(client, messages, media_folder):
	for message in messages:
		try :
			attrs = dir(message.media)
			if 'photo' in attrs: filename = message.media.photo.id
			if 'document' in attrs: filename = message.media.document.id
			if 'webpage' in attrs: filename = message.media.webpage.id

			client.download_media(message.media, '{}/{}-{}'.format(media_folder, message.id, filename))
		except: continue

def save_messages(channel, date_obj, f_messages, f_media, media_folder, client):
	messages, messages_objects = get_channel_messages(channel, date_obj, client)
	if messages is None: return []
	for message in messages:
		if message['_'] == 'Message':
			del message['_']
			
			if 'media' in message:
				if message['media'] is not None:
					media_internal_id = save_message_media(message['media'], f_media)
					del message['media']
					message['media'] = media_internal_id
			
			else: message['media'] = None 

			message_dict = format_message_item(message)
			msg = Message(**message_dict)

			try:
				msg.user_id = msg.from_id['user_id']
				del msg.from_id
			except: pass	

			try: 
				msg.channel_id = msg.peer_id['channel_id']
				del msg.peer_id
			except: pass
			
			
			save_line_to_json(msg.__dict__, f_messages)

	return messages_objects

def save_message(message, f_messages, f_media):
	if message['_'] == 'Message':
		del message['_']
			
		if 'media' in message:
			if message['media'] is not None:
				media_internal_id = save_message_media(message['media'], f_media)
				del message['media']
				message['media'] = media_internal_id
			
		else: message['media'] = None 

		message_dict = format_message_item(message)
		msg = Message(**message_dict)

		try:
			msg.user_id = msg.from_id['user_id']
			del msg.from_id
		except: pass	

		try: 
			msg.channel_id = msg.peer_id['channel_id']
			del msg.peer_id
		except: pass
			
			
		save_line_to_json(msg.__dict__, f_messages)

def save_channel(channel, f_channels):
	try: channel_dict = format_item(channel)
	except: return None

	channel_obj = Channel(**channel_dict)
	save_line_to_json(channel_obj.__dict__, f_channels)

	return channel_obj.id
	
def save_channel_users(client, channel, channelid, f_users):
	
	try: 
		participants = get_channel_participants(client, channel)

		for item in participants:
			user_dict = format_item(item) 
			user = User(**user_dict)
			user.channel_id = channelid
			save_line_to_json(user.__dict__, f_users)
	except: print('Could not get any participans')

def get_new_channels(messages, client):
	new_channels = []
	
	for message in messages:
		for msg in message:
			try:
				channel_obj = client.get_entity(PeerChannel(msg.fwd_from.from_id.channel_id))
				new_channels.append(channel_obj.username)
			except: pass

	return new_channels

def save_new_channels(messages, old_channels, client, config):
	new_channels = list(set(get_new_channels(messages, client)))

	for channel in new_channels:
		if channel not in old_channels:
			save_line_txt_file(config['channels_file'], channel)

if __name__ == "__main__":
	config = load_config_variables()
	f_users, f_messages, f_channels, f_media, media_folder = make_folders(config)
	yesterday = datetime.date.today() - datetime.timedelta(days=1)

	channels = [item.replace('\n', '') for item in read_txt_file(config['channels_file'])]

	client = connect_telegram_client(config)
	all_messages_objects = []

	for ch in channels:
		channel_id = 'https://t.me/{}'.format(ch)
	
		try: channel = get_channel(client, channel_id)
		except: channel = None

		if channel is not None:
			id = save_channel(channel, f_channels)

			if id is not None:
				save_channel_users(client, channel, id, f_users)
				msg_objects = save_messages(channel, yesterday, f_messages, f_media, media_folder, client)
				all_messages_objects.append(msg_objects)
			else: print('Could not format channel properly...')

	print('Saving channels.................')
	save_new_channels(all_messages_objects, channels, client, config)
	
	print('Getting media.........')
	print(len(all_messages_objects))
	
	for obj in all_messages_objects: 
		print(len(obj))
		dowload_media(client, obj, media_folder)