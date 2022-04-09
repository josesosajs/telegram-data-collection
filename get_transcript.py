import wave, math, contextlib
import speech_recognition as sr
from moviepy.editor import AudioFileClip
import os
from os import walk
import sys

def create_audio_file(audio_file, video_name):
	audioclip = AudioFileClip(video_name)
	audioclip.write_audiofile(audio_file)

def get_audio_duration(audio_file):
	with contextlib.closing(wave.open(audio_file,'r')) as f:
		frames = f.getnframes()
		rate = f.getframerate()
		duration = frames / float(rate)

	return math.ceil(duration / 60)

def get_transcript_file(audio_file, total_duration, transcript_path):
	r = sr.Recognizer()
	for i in range(0, total_duration):
		with sr.AudioFile(audio_file) as source:
			audio = r.record(source, offset=i*60, duration=60)
		
		f = open(transcript_path, "a")
		f.write(r.recognize_google(audio))
		f.write(" ")
	f.close()

def check_valid_video_file(video_file):
	file_size = os.path.getsize(video_file)

	return False if file_size == 0 else True

if __name__ == "__main__":
	yesterday = str(sys.argv[1])
	root_path = "data/{}/media/videos/".format(yesterday)
	filenames = next(walk(root_path), (None, None, []))[2]
	print(filenames)

	for file in filenames:
		audio_file = '{}{}'.format(root_path, "transcribed_speech.wav")
		video_file = '{}{}'.format(root_path, file)
		transcript_path = '{}{}'.format(root_path, file.replace('mp4', 'txt'))

		size = check_valid_video_file(video_file)

		if check_valid_video_file(video_file):	

			try: 
				create_audio_file(audio_file, video_file)
				audio = True
			except: audio = None

			if audio is not None:
				try:
					duration = get_audio_duration(audio_file)
					get_transcript_file(audio_file, duration, transcript_path)
				except: 
					print('Could not create transcript :c')
					pass
		
		else: print('Video file not valid')
