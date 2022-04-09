from os import walk
import os
from utils import load_json_data, read_txt_file
from get_transcript import check_valid_video_file
import re
import pandas as pd
import json
import sys

def clean_message(message):
	message = message.replace('\n', '')
	message = message.lower()
	message = message.strip()
	
	emoji_pattern = re.compile("["
		u"\U0001F600-\U0001F64F"  # emoticons
		u"\U0001F300-\U0001F5FF"  # symbols & pictographs
		u"\U0001F680-\U0001F6FF"  # transport & map symbols
		u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
		u"\U00002500-\U00002BEF"  # chinese char
		u"\U00002702-\U000027B0"
		u"\U00002702-\U000027B0"
		u"\U000024C2-\U0001F251"
		u"\U0001f926-\U0001f937"
		u"\U00010000-\U0010ffff"
		u"\u2640-\u2642" 
		u"\u2600-\u2B55"
		u"\u200d"
		u"\u23cf"
		u"\u23e9"
		u"\u231a"
		u"\ufe0f"  # dingbats
		u"\u3030"
					  "]+", re.UNICODE)
	message = emoji_pattern.sub(r'', message)
	return message

if __name__ == '__main__':
	yesterday = str(sys.argv[1])
	root_path = 'data/{}/'.format(yesterday)
	transcripts_folder = '{}{}'.format(root_path, 'media/transcripts')
	meesages_data = load_json_data('{}{}'.format(root_path,'telegram_messages.json'))
	channels_data = load_json_data('{}{}'.format(root_path,'telegram_channels.json'))


	filenames = next(walk(transcripts_folder), (None, None, []))[2]
	all_messages = []
	data_transcripts = []
	
	for file in filenames:
		messages_data = {}
		transcript_path  = '{}/{}'.format(transcripts_folder, file)
		if check_valid_video_file(transcript_path): 
			messages_data['message_id'] = file.split('-')[0]
			trans = read_txt_file(transcript_path)
			messages_data['message_txt'] = clean_message(trans[0])
			messages_data['transcript_file'] = file
			messages_data['video_file'] = file.replace('txt', 'mp4')
			all_messages.append(messages_data)

	
	for message in meesages_data:
		message_item = {}
		ids = [item['message_id'] for item in all_messages]
		if str(message['id']) in ids:
			trans_item  = [item for item in all_messages if item['message_id'] == str(message['id'])]
			message_item['id'] = message['id']
			message_item['channel_id'] = message['channel_id']
			
			channels = [item for item in channels_data if str(item['id']) == str(message['channel_id'])]
			
			message_item['channel_title'] = channels[0]['title']
			message_item['channel_username'] = channels[0]['username']
			message_item['post_author'] = message['post_author']
			message_item['message'] = clean_message(message['message'])
			message_item['transcript'] = trans_item[0]['message_txt']
			message_item['transcript_file'] = trans_item[0]['transcript_file']
			message_item['video_file'] = trans_item[0]['video_file']
			
			data_transcripts.append(message_item)

	trans_data_df = pd.DataFrame.from_dict(data_transcripts, orient='columns')
	with pd.ExcelWriter('{}video_transcript_stats_{}.xlsx'.format(root_path, yesterday)) as writer:
		trans_data_df.to_excel(writer, sheet_name='video-transcript-info')
