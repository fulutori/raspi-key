#coding: utf-8
import nfc
import datetime
import pandas as pd
import subprocess
import re
import sys
import os
import datetime
import tweepy
import RPi.GPIO as GPIO
import time

#csvファイル読み込み
member = pd.read_csv("member.csv", header=None)

#print(member)
#subprocess.call('clear')

#twitterのAPIとか
consumer_key = "xxxxxxxxxxxxxxxxxxxxxxxxx"
consumer_secret = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
access_token = "xxxxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
access_secret = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

#servo_setting
def servo(turn):
	GPIO.setmode(GPIO.BCM)
	gp_out = 4
	GPIO.setup(gp_out, GPIO.OUT)
	servo = GPIO.PWM(gp_out, 50)
	servo.start(0.0)
	servo.ChangeDutyCycle(turn)
	time.sleep(0.3)
	GPIO.cleanup()

#鍵の開閉状況を初期化(施錠された状態)
#servo(6.5)

def tweet(user):
	#ログファイル
	f = open("key.log", "a")
	time = datetime.datetime.today()
	time.strftime
	tweet = str(time.strftime("%Y-%m-%d %H:%M:%S")) + "\n" + user + "\n#olurikey"
	f.write(str(time) + " " + user + " | NFC\n")
	#print(tweet)
	api.update_status(tweet)
	f.close()

def unlock(user):
	servo(12.0)
	try:
		tweet(user + "さんが解錠しました")
		#print((user + "さんが解錠しました"))
	except:
		print ("解錠ツイートに失敗しました")
	path = "aplay ./sound/voice/" + user + ".wav"
	subprocess.call(path, shell=True)

def lock(user):
	servo(6.5)
	try:
		tweet(user + "さんが施錠しました")
		#print(user + "さんが施錠しました")
	except:
		print ("施錠ツイートに失敗しました")
	subprocess.call("aplay ./sound/voice/otu.wav", shell=True)

def startup(targets):
	print "waiting for new NFC tags..."
	return targets


def connected(tag):
	#print(tag)
	try:
		idm = str(tag).split(' ')[4][3:]
	except:
		subprocess.call("aplay ./sound/voice/miss-nfc.wav", shell=True)
		return True
	print (idm)
	name_id = re.split(" +", str(member[member[2] == idm]))
	if name_id[0] == "Empty":	#存在しない場合はスルー
		#subprocess.call('clear')
		print("そのIDは登録されていません")
		subprocess.call("aplay ./sound/voice/id.wav", shell=True)
		return True
	else:
		#subprocess.call('clear')
		user = member[member[2] == idm].iloc[0,0]
	with open('status','r') as f:
		status = int(f.readline())
	with open('status','w') as f:
		if status == 0:
			unlock(user)
			f.write('1')
		elif status == 1:
			lock(user)
			f.write('0')
	return True


def released(tag):
	print("released:")


clf = nfc.ContactlessFrontend('usb')
print(clf)
if clf:
	while clf.connect(rdwr={
		'on-startup': startup,
		'on-connect': connected,
		'on-release': released,
	}):
		pass