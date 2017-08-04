# -*-coding:utf-8-*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from requests_oauthlib.oauth1_session import OAuth1Session
import requests
import logging
import json

if __name__ == '__main__':
	pass

_logger = logging.getLogger(__name__)
	
from requests_oauthlib import OAuth1;

def reply_to_question(base_url, consumer_key, consumer_secret, access_key, access_secret, listing_id, question_id, answer) :
	validate(base_url,"Base URL");
	validate(consumer_key,"Consumer Key");
	validate(consumer_secret,"Consumer Secret");
	validate(access_key,"Access Key");
	validate(access_secret,"Access Secret");
	base_url = base_url.strip('/')
	url = str.format("{0}/v1/Listings/{1}/questions/{2}/answerquestion.json", base_url, listing_id,question_id );
	base_url = base_url.strip('/')
	headeroauth = OAuth1(consumer_key, consumer_secret, access_key, access_secret, signature_type='auth_header')
	payload = { "answer" : answer } ;
	headers = {'Content-Type': 'application/json'}
#	_logger.error(" content: "+json.dumps(payload))
#	print payload
	response = requests.post(url, json.dumps(payload), auth=headeroauth, headers=headers)
	data =parse_response(response, url);
#	print data;
	return;

def fetch_member_id(base_url, consumer_key, consumer_secret, access_key, access_secret) :
	member, nick = fetch_member_id_and_nick(base_url, consumer_key, consumer_secret, access_key, access_secret)
	return member;
	
def fetch_member_id_and_nick(base_url, consumer_key, consumer_secret, access_key, access_secret) :
	validate(base_url,"Base URL");
	validate(consumer_key,"Consumer Key");
	validate(consumer_secret,"Consumer Secret");
	validate(access_key,"Access Key");
	validate(access_secret,"Access Secret");
	
	base_url = base_url.strip('/')
	url = base_url + "/v1/MyTradeMe/Summary.json"
	headeroauth = OAuth1(consumer_key, consumer_secret, access_key, access_secret, signature_type='auth_header')
#	ses = OAuth1Session(consumer_key, consumer_secret, access_key, access_secret, signature_type='auth_header')
#	response = ses.get(url)
	response = requests.get(url, auth=headeroauth)
	data  = parse_response(response, url);
	member_id = data.get("MemberId");
	Nickname= data.get("Nickname");
	return member_id,Nickname ;

def validate(value, error):
	if(value is None):
		raise Exception(error+" cannot be null or empty.")
	if (isinstance(value, str) and value=='' ):
		raise Exception(error+" cannot be null or empty.")
	if isinstance(value, int) and value==0:
		raise Exception(error+" cannot be zero.")


def parse_response(response, url):
	if response.status_code != 200:
		error = ""
		try:
			data  = response.json();
		except ValueError as ex:
			pass
		if data is not None :
			error = data.get("ErrorDescription")

		if response.status_code == 401:
			raise Exception("Unable to execute request '"+url+"': "+response.reason +" : "+str(response.status_code) +", Error:"+error +". Please validate that the Application is enabled as well as consumer key, consumer secret, access key , access secret are valid.");
		else:
			raise Exception("Unable to execute request '"+url+"': "+response.reason +" : "+str(response.status_code) +", Error:"+error);
	try:
		data  = response.json();
	except ValueError as ex:
		raise Exception("Unable to parse JSON response for url "+url+", Error \n"+ex.message+", Response:"+response.content, ex)
	return data;
	
def fetch_members_listing(base_url, consumer_key, consumer_secret, access_key, access_secret, member_id) :
	
	validate(base_url,"Base URL");
	validate(consumer_key,"Consumer Key");
	validate(consumer_secret,"Consumer Secret");
	validate(access_key,"Access Key");
	validate(access_secret,"Access Secret");
	validate(member_id,"Member Id");

	base_url = base_url.strip('/')
	url = base_url + "/v1/Search/General.json"
	headeroauth = OAuth1(consumer_key, consumer_secret, access_key, access_secret, signature_type='auth_header')
#	ses = OAuth1Session(consumer_key, consumer_secret, access_key, access_secret, signature_type='auth_header')
	page_size = 500;
	page=1;
	currentPageResult = page_size;
	newList = []
	while(currentPageResult==page_size):
		print str.format("Fetching the data for page {0}, rows {1}", page, page_size);
		payload = {'member_listing': member_id,'rows':str(page_size), 'page':page}
#		response = ses.get(url, params = payload)
		response = requests.get(url, auth=headeroauth, params = payload)
		data = parse_response(response, url);
		newList.extend(data.get('List'))
		currentPageResult = data.get("PageSize")
		print str.format("Total items found {0}", currentPageResult);
		page+=1;
	return newList;

def fetch_all_unanswered_questions_for_listing(base_url, consumer_key, consumer_secret, access_key, access_secret, listingId):
	validate(base_url,"Base URL");
	validate(consumer_key,"Consumer Key");
	validate(consumer_secret,"Consumer Secret");
	validate(access_key,"Access Key");
	validate(access_secret,"Access Secret");
	validate(listingId,"Listing Id");

	base_url = base_url.strip('/')
	url = str.format("{0}/v1/Listings/{1}/questions/unansweredquestions.json", base_url, listingId);
	print str.format('Getting unanswered questions for listing {0}', listingId) 
	headeroauth = OAuth1(consumer_key, consumer_secret, access_key, access_secret, signature_type='auth_header')
#	ses = OAuth1Session(consumer_key, consumer_secret, access_key, access_secret, signature_type='auth_header')

	page_size = 500;
	page=1;
	currentPageResult = page_size;
	newList = []
	while(currentPageResult==page_size):
		print str.format("Fetching the data for page {0}, rows {1}", page, page_size);
		payload = {'rows':str(page_size), 'page':page}
#		response = ses.get(url, params=payload)
		response = requests.get(url, auth=headeroauth, params=payload)
		data = parse_response(response, url);
		newList.extend(data.get('List'))
		currentPageResult = data.get("PageSize")
		print str.format("Total items found {0}", currentPageResult);
		page+=1;
	return newList;

def fetch_all_unanswered_questions(base_url, consumer_key, consumer_secret, access_key, access_secret):
	validate(base_url,"Base URL");
	validate(consumer_key,"Consumer Key");
	validate(consumer_secret,"Consumer Secret");
	validate(access_key,"Access Key");
	validate(access_secret,"Access Secret");

	base_url = base_url.strip('/')
	url = str.format("{0}/v1/Listings/questions/unansweredquestions.json", base_url);
	print str.format('Getting unanswered questions for all listings') 
	headeroauth = OAuth1(consumer_key, consumer_secret, access_key, access_secret, signature_type='auth_header')
#	ses = OAuth1Session(consumer_key, consumer_secret, access_key, access_secret, signature_type='auth_header')

	page_size = 500;
	page=1;
	currentPageResult = page_size;
	newList = []
	while(currentPageResult==page_size):
		print str.format("Fetching the data for page {0}, rows {1}", page, page_size);
		payload = {'rows':str(page_size), 'page':page}
#		response = ses.get(url, params=payload)
		response = requests.get(url, auth=headeroauth, params=payload)
		data = parse_response(response, url);
		newList.extend(data.get('List'))
		currentPageResult = data.get("PageSize")
		print str.format("Total items found {0}", currentPageResult);
		page+=1;
	return newList;
