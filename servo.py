#coding: utf-8
import datetime
import pandas as pd
import subprocess
import re
import sys
import os
import tweepy
import RPi.GPIO as GPIO
import time
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

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

def tweet(user):
	#ログ書き込み
	f = open("key.log", "a")
	time = datetime.datetime.today()
	time.strftime
	tweet = str(time.strftime("%Y-%m-%d %H:%M:%S")) + "\n" + user + "\n#olurikey"
	f.write(str(time) + " " + user + " | ID/PASS\n")
	#print(tweet)
	api.update_status(tweet)
	f.close()

#ID入力
def idn():
	#subprocess.call('clear')
	while True:	#ID入力は無限ループ
		idname = input("IDを入力してください\nID > ")	#ID入力
		if idname.isdigit() == False:
			continue
		if idname == "":
			subprocess.call('clear')
			continue
		name_id = re.split(" +", str(member[member[1] == int(idname)]))	#入力されたIDがcsvファイルに存在するか検索
		if name_id[0] == "Empty":	#存在しない場合はスルー
			subprocess.call('clear')
			print("そのIDは登録されていません\n")
			subprocess.call("aplay ./sound/voice/id.wav", shell=True)
		else:
			subprocess.call('clear')
			user = member[member[1] == int(idname)].iloc[0,0]
			return user
			break

#パスワード入力
def unlock(user):
	subprocess.call("aplay ./sound/voice/pass.wav", shell=True)
	subprocess.call('clear')
	#パスワード生成
	key_t = "232522" #guest
	today = datetime.datetime.today()	#日付時刻を取得
	print (today)
	n = 0
	while n < 5:	#パスワード入力はIDが入力されてから5回まで受け付ける
		first = str(today.hour + today.day)
		second = str(today.minute)
		if len(first) == 1: #01~09時のとき
			first = str("0") + first #時の前に"0"を入れる
		if len(second) == 1:	#01〜09分のとき
			second = str("0") + second	#分の前に"0"を入れる
		key = first + second	#日と時の和と分を繋げる
		print (key)
		password = input("password > ")	#パスワード入力
		if password.isdigit() == False:
			continue
		if str(password) == key:	#入力された文字と生成されたパスワードが同じのとき
			servo(12.0)
			subprocess.call('clear')
			try:
				tweet(user + "さんが解錠しました")
				#print(user + "さんが解錠しました")
			except:
				print ("解錠ツイートに失敗しました")
			path = "aplay ./sound/voice/" + user + ".wav"
			subprocess.call(path, shell=True)
			break
		elif str(password) == key_t:	#入力された文字と生成されたパスワードが同じのとき
			servo(12.0)
			subprocess.call('clear')
			try:
				tweet(user + "さんが解錠しました")
				#print(user + "さんが解錠しました")
			except:
				print ("ゲストの解錠の際にツイートが失敗しました")
			path = "aplay ./sound/voice/" + user + ".wav"
			subprocess.call(path, shell=True)
			break
		else:	#パスワードが違うときはスルー
			subprocess.call('clear')
			subprocess.call("aplay ./sound/voice/pass_another.wav", shell=True)
			n += 1
			print(str(n) + "回目 パスワードが違います")
			if n == 5:
				return n

#---------------------------------
#施錠
def lock(user):
	#subprocess.call('clear')
	servo(6.5)
	subprocess.call("aplay ./sound/voice/otu.wav", shell=True)
	try:
		tweet(user + "さんが施錠しました")
		#print(user + "さんが施錠しました")
	except:
		print ("施錠ツイートに失敗しました")

#---------------------------------

if __name__ == "__main__":
	while True:
		try:
			user = idn()
			with open('status','r') as f:
				try:
					status = int(f.readline())
				except:
					with open('status','w') as f:
						f.write('0')
						subprocess.call("aplay ./sound/voice/id.wav", shell=True)
					continue
			with open('status','w') as f:
				if status == 0:
					if unlock(user) == 5:
						subprocess.call("aplay ./sound/voice/miss.wav", shell=True)
						continue
					f.write('1')
				elif status == 1:
					lock(user)
					f.write('0')
		except:
			time = datetime.datetime.today()
			time.strftime
			print ("\nエラーが発生しました")
			print (sys.exc_info())
			print (str(time.strftime("%Y-%m-%d %H:%M:%S")))			