import requests, urllib
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer


APP_ACCESS_TOKEN = '1411901019.4095b8d.2f1700e3bbe6476885d62c6711ef96f6'
BASE_URL = 'https://api.instagram.com/v1/'



def self_info():
	request_url = (BASE_URL + 'users/self/?access_token=%s') % (APP_ACCESS_TOKEN)
	print 'GET request url : %s' % (request_url)
	user_info = requests.get(request_url).json()

	if user_info['meta']['code'] == 200:
		if 'data' in user_info:
			print 'Username: %s' % (user_info['data']['username'])
			print 'No. of followers: %s' % (user_info['data']['counts']['followed_by'])
			print 'No. of people you are following: %s' % (user_info['data']['counts']['follows'])
			print 'No. of posts: %s' % (user_info['data']['counts']['media'])
	else:
		print 'Status code other than 200 received!'


def get_user_id(insta_username):
	request_url = (BASE_URL + "users/search?q=%s&access_token=%s") % (insta_username, APP_ACCESS_TOKEN)

	print 'GET request url : %s' % (request_url)

	user_info = requests.get(request_url).json()

	if user_info['meta']['code'] == 200:
		if len(user_info['data']):
			return user_info['data'][0]['id']
		else:
			return None
	else:
		print 'Status code other than 200 received!'
		exit()


def get_user_info(insta_username):
	user_id = get_user_id(insta_username)
	if user_id == None:
		print 'User does not exist!'
		exit()
	request_url = (BASE_URL + 'users/%s?access_token=%s') % (user_id, APP_ACCESS_TOKEN)
	print 'GET request url : %s' % (request_url)
	user_info = requests.get(request_url).json()

	if user_info['meta']['code'] == 200:
		if len(user_info['data']):
			print 'Username: %s' % (user_info['data']['username'])
			print 'No. of followers: %s' % (user_info['data']['counts']['followed_by'])
			print 'No. of people you are following: %s' % (user_info['data']['counts']['follows'])
			print 'No. of posts: %s' % (user_info['data']['counts']['media'])
		else:
			print 'There is no data for this user!'
	else:
		print 'Status code other than 200 received!'


def get_own_post():
	request_url = (BASE_URL + 'users/self/media/recent/?access_token=%s') % (APP_ACCESS_TOKEN)
	print 'GET request url : %s' % (request_url)
	own_media = requests.get(request_url).json()

	if own_media['meta']['code'] == 200:
		if len(own_media['data']) > 0:
			return own_media['data'][0]['id']
		else:
			print 'Post does not exist!'
	else:
		print 'Status code other than 200 received!'


def get_user_post(insta_username):
	user_id = get_user_id(insta_username)

	if user_id == None:
		print 'User does not exist!'
		exit()

	request_url = (BASE_URL + 'users/%s/media/recent/?access_token=%s') % (user_id, APP_ACCESS_TOKEN)
	print 'GET request url : %s' % (request_url)
	user_media = requests.get(request_url).json()

	if user_media['meta']['code'] == 200:
		if len(user_media['data']) > 0:
			image_name = user_media['data'][0]['id'] + '.jpeg'
			image_url = user_media['data'][0]['images']['standard_resolution']['url']
			urllib.urlretrieve(image_url, image_name)
			print 'Your image has been downloaded!'
			return user_media['data'][0]['id']
		else:
			print "There is no recent post!"
	else:
		print "Status code other than 200 received!"
		return None


def like_a_post(insta_username):
	media_id = get_user_post(insta_username)

	request_url = (BASE_URL + 'media/%s/likes') % (media_id)
	payload = {"access_token": APP_ACCESS_TOKEN}
	print 'POST request url : %s' % (request_url)
	post_a_like = requests.post(request_url, payload).json()

	if post_a_like['meta']['code'] == 200:
		print 'Like was successful!'
	else:
		print 'Your like was unsuccessful. Try again!'


def delete_negative_comment(insta_username):
	media_id = get_user_post(insta_username)
	request_url = (BASE_URL + 'media/%s/comments/?access_token=%s') % (media_id, APP_ACCESS_TOKEN)
	print 'GET request url : %s' % (request_url)
	comment_info = requests.get(request_url).json()

	if comment_info['meta']['code'] == 200:
		# Check if we have comments on the post
		if len(comment_info['data']) > 0:
			# And then read them one by one
			for comment in comment_info['data']:
				comment_text = comment['text']
				blob = TextBlob(comment_text, analyzer=NaiveBayesAnalyzer())

				if blob.sentiment.p_neg > blob.sentiment.p_pos:
					comment_id = comment['id']
					delete_url = (BASE_URL + 'media/%s/comments/%s/?access_token=%s') % (
						media_id, comment_id, APP_ACCESS_TOKEN)
					print 'DELETE request url : %s' % (delete_url)

					delete_info = requests.delete(delete_url).json()


					if delete_info['meta']['code'] == 200:
						print 'Comment successfully deleted!'
					else:
						print 'Could not delete the comment'

		else:
			print 'No comments there !'
	else:
		print 'Status code other than 200 received!'


def start_bot():
	while True:
		print '\n'
		print 'Hey! Welcome to instaBot!'
		print 'Here are your menu options:'
		print "a.Get your own details\n"
		print "b.Get details of a user by username\n"
		print "c.Get your own recent post\n"
		print "d.Get the recent post of a user by username\n"
		print "e.Like recent post of a user\n"
		print "f.Delete negative comment for a user\n"
		print "j.Exit"

		choice = raw_input("Enter you choice: ")
		if choice.lower() == "a":
			self_info()
		elif choice.lower() == "b":
			insta_username = raw_input("Enter the username of the user: ")
			get_user_info(insta_username)
		elif choice.lower() == "c":
			get_own_post()
		elif choice.lower() == "d":
			insta_username = raw_input("Enter the username of the user: ")
			get_user_post(insta_username)
		elif choice.lower() == "e":
			insta_username = raw_input("Enter the username of the user: ")
			like_a_post(insta_username)
		elif choice.lower() == "f":
			insta_username = raw_input("Enter the username of the user: ")
			delete_negative_comment(insta_username)
		elif choice.lower() == "j":
			exit()
		else:
			print "wrong choice"


start_bot()
