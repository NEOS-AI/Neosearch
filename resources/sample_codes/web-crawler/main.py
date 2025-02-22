#! handling for robots.txt
import requests
from bs4 import BeautifulSoup
from datetime import date as dt
from urllib.parse import urlparse
import datetime
import json
import os
import sqlite3
from sqlite3 import Error
from datetime import datetime as dt
import sys, select
import time as t
import random

blocked_domains = []
page_batch = 20
hourly_limit = page_batch
pages_per_hour = {'min':datetime.datetime.now().minute,'domain':{}}
THREAD_COUNT = 8
maxes = {}
'''
files:

links_to_pull: [link,link,link]
links_crawled: [[link,date],[link,date]]



Processes:
-Crawling-
	- pull a link from links_to_crawl. If not in links_crawled, execute code, else continue to next link and remove from list
	- Save HTML to .txt file in './to_parse/'
	- Eventually attempt only to visit https sites
	- If it ends in .jpg, .png, etc. don't crawl it
-Parsing-
	- Open file in './to_parse/'
	- Loop through all doc links. If not in links_to_pull, add to links_to_pull
	- Eventually check health of page. Is it written well, is it credible, backlinks? etc.
	- Create txt file from page text 
	- Move HTML file to parsed_docs and replace previous file
-Indexing-
	- dict of all search queries ever recieved (ordered by search volume?) i.e. index = {"term":{"site":score,"site":score,"site":score}}
	- regularly loop through dict and check each doc with text.count(query)
	- eventually create new index.json to speed up search speed. Only need to open one file instead of entire 
-Search-
	- open indexed query for quick comprehensive result
-Quick Index-
	- provides quick results for query that hasn't been indexed yet


TO DO
 - create 'broken_links' db


'''

#seed = 'https://en.wikipedia.org/wiki/Main_Page'





# set new requests session
sess = requests.Session() # should be reset after 100 requests
hourly_limit -= 1

def create_connection(db_file):
	''' create a database connection to a SQLite database '''
	try:
		connection = sqlite3.connect(db_file)
		print(sqlite3.version)
	except Error as e:
		print(e)
		if connection:
			connection.close()
		return None,None

	return connection,connection.cursor()


def multi_query(q,rows):
	try:
		cursor.executemany(q, rows)
		return True
	except Error as e:
		print(e)
		print('transaction failed')
		return False

def query(q,val=''):
	#if value is not None
	try:
		cursor.execute(q,val)
		return True
	except Error as e:
		print(e)
		print('transaction failed')
		return False

def visit_link(link, f_count): # visits links that have been gathered from crawled pages and download html
	url = 'https://'+link
	domain = link.split('/')[0]
	print(len(url))
	
	timeout = 30
	try:
		body = []
		start_time = t.time()
		r = sess.get(url,timeout=15,stream=True)
		for chunk in r.iter_content(1024):
			body.append(chunk)
			if t.time() > (start_time + timeout):
				print('Long timeout. Moved to failed_crawls')
				return False,4
		content = b''.join(body).decode('utf-8')
	except requests.exceptions.ConnectionError as e:
		blocked_domains.append(domain)
		print(e)
		#print(domain,' blocked you')
		return False,1
	except requests.exceptions.Timeout:
		print('Connection timeout. Will attempt to crawl at a later time')
		return False,0
	except UnicodeError:
		print('Unicode error: url too long or empty and all that jazz')
		return False,2
	except requests.exceptions.TooManyRedirects:
		print('Too many redirects')
		return False,3
	except:
		print('unknown error. Will attempt recrawl')
		return False, 0

	#Check if IP has been temporarily blocked due to too many requests
	if r.status_code != 200:
		print(f'Error {r.status_code} encountered for {link}','Continuing to next link. Will attempt again later')
		return False, r.status_code
		#kill program command should go here

	# create folders for new domain
	if f_count == 0:
		try:
			os.mkdir(f'parsed_html/{domain}/')
			os.mkdir(f'parsed_text/{domain}/')
		except Exception as e:
			if e is not FileExistsError:
				print('unknown error encountered')
			else:
				print(f'directory {domain} already existed')

	# save website HTML to txt file
	with open(f'to_parse/{domain}]and[{f_count}.txt', 'w') as f:
		f.write(content)

	return True, 1

def threaded_crawl(urls):
	pass

def parse(doc, domain): # pull links and text from crawled pages
	#! 2 queries for links pulled to check if they are in links_crawled, links_to crawl, and failed_links

	print(domain)
	soup = BeautifulSoup(doc, 'html.parser')

	l_l = [x.get('href') for x in soup.find_all('a') if x.get('href') is not None]

	parse_links(domain,l_l)

	# pull text from page
	#! find a use for page title
	text = soup.find_all(text=True)
	output = ''
	blacklist = [
		'[document]',
		'noscript',
		'header',
		'html',
		'meta',
		'head', 
		'input',
		'script',
		'style'
	]
	for t in text:
		if t.parent.name not in blacklist:
			output += '{} '.format(t)

	return output
	
	'''
	structured_data = {}
	for word in text:
		try: # avoids unecessary check if key exists. Maybe more efficient
			structured_data[word] += 1
		except:
			structured_data[word] = 1
	'''

def parse_links(domain, link_list):
	links_to_crawl = []
	i = 0

	for link in link_list: 
		# handle link variations you will encounter
		try:
			if not link: # remove empty links
				continue
		except:
			print('exception: ',link)
			print(link[0])
		# remove whitespace and http(s)
		link = link.replace('https://','').replace('http://','').replace(' ', '').replace('\t', '').replace('\n', '')
		# remove non html pages
		if link[-4:].lower() in ['.jpg','.png','.gif','.svg','.pdf']: # eventually use to save picture sites
			continue
		# standardize links that point to page element: '//site.domain/page:element'
		if link[:2] == '//':
			link = link.replace('//','').split(':')[0]
		elif link[:1] == '/': # handle links within domain: '/page/ref'
			link = domain+link
		# remove malformed urls
		if link.split('/')[0].replace('.','').replace('-','').isalnum() is False: # make sure domain 
			continue
		if link[0] in ('#','(','{','?','<','\\'):
			continue
		false_links = ('mailto:','javascript:','tel:','./') # links starting with '?' might need same handling as links starting with '/'
		for fals in false_links: # check for malformed links
			if link.lower().startswith(fals):
				continue

		# split domain name out from url
		dom = link.split('/')[0]
		# in the future ensure that domain is only made up of alphanumeric and '-'
		if len(dom.split('.')) < 2: # not a real link if domain is not at least domain.something
			continue
		#standardize links by removing final '/' -- if you add '/' instead, it will malform 'site.domain/page.htm'
		if link[-1] == '/':
			link = link[:-1]

		i += 1

		if (link,dom) not in links_to_crawl: # check if already in queue to crawl
			links_to_crawl.append((link,dom))


	# if no links pulled, make sure doc correctly parsed
	if len(links_to_crawl) < 1:
		print('No valuable links from ',domain)
		print('Do these values match?')
		print('links to crawl: ',len(links_to_crawl))
		print('links on page: ',i)
		return


	# split out links & domain names for validation & analysis
	doms = tuple([x[1] for x in links_to_crawl])
	links = tuple([x[0] for x in links_to_crawl])
	
	# check if site is bad
	print('checking for bad sites')
	query(f'SELECT domain FROM blacklisted_domains WHERE domain IN {doms}')
	vals = cursor.fetchall()
	if len(vals) > 0:
		print(f'avoided {len(vals)} bad page(s)')
		vals = [x[0] for x in vals]
		links_to_crawl[:] = [x for x in links_to_crawl if x[1] not in vals]

	# check if link has been crawled
	print('checking for duplicates 1 (pages_crawled)')
	query(f'SELECT url FROM pages_crawled WHERE url IN {links}')
	vals = cursor.fetchall()
	if len(vals) > 0:
		vals = [x[0] for x in vals]
		links_to_crawl[:] = [x for x in links_to_crawl if x[0] not in vals]

	# check if link has been attempted to be crawled and failed
	print('checking for duplicates 2 (failed_crawls)')
	query(f'SELECT url FROM failed_crawls WHERE url IN {links}')
	vals = cursor.fetchall()
	if len(vals) > 0:
		vals = [x[0] for x in vals]
		links_to_crawl[:] = [x for x in links_to_crawl if x[0] not in vals]


	# ________Pull domain_id and add new domains________
	doms = tuple([x[1] for x in links_to_crawl])
	print('adding new domains')
	
	# pull all domains that already exist in the domain table
	if query(f'SELECT DISTINCT domain_name FROM domains WHERE domain_name IN {doms}'):
		vals = [x[0] for x in cursor.fetchall()]
		# gather list of domains that aren't in the domain table
		d_to_add = []
		for x in doms:
			if x not in vals and (x,) not in d_to_add: # only append unique values. No duplicates
				d_to_add.append((x,))
		multi_query('INSERT INTO domains(domain_name) VALUES (?)',d_to_add)

		# pull domain_id for links to add to pages_to_crawl table
		query(f'SELECT DISTINCT domain_name, domain_id FROM domains WHERE domain_name IN {doms}')
		vals = {x[0]:x[1] for x in cursor.fetchall()}

		# update links to craw list
		links_to_crawl[:] = [(x[0],vals[x[1]]) for x in links_to_crawl if x[1] in vals]
		# add to DB
		if len(links_to_crawl) > 0:
			multi_query('''INSERT OR IGNORE INTO pages_to_crawl VALUES (?,?)''',links_to_crawl)
		conn.commit()


def quick_index(query): # if search query hasn't been indexed yet
	scores = [] # structured: [[url, score],[url, score]]

	for filename in os.listdir('./parsed_text/'): 
		with open(os.path.join('./parsed_text/', filename), 'r') as f:
			try: #! eventually flag exceptions w/ non unicode chars for redownload or removal
				text = f.read().lower() #! using lower every time may be processor heavy
			except:
				continue
		filename = filename.replace('.txt','')
		with open('fn_to_url.json','r') as f:
			filename_to_url = json.load(f)

		# check score of exact match and word matches
		text_len = len(text.split(' ')) # Ignores new lines. More accurate method: import re and then re.split('\n| ', string)
		exact_score = text.count(query)
		word_score = 0
		for word in query.split():
			word_score += text.count(word)
		word_score = word_score/text_len # makes score a ratio of how much a word shows up compared to how many words there are
		if word_score + exact_score > 0:
			full_score = (exact_score+1)*word_score # exact score is multiplier for semi
			scores.append([filename_to_url[filename], full_score])
	scores.sort(key=lambda x: x[1]) # sort scores list by first item in each sublist
	return scores

def search(query) -> list:
	query = query.lower() # non case sensative queries. #! eventually make bool for if case sensitive or not
	#c_query = clean(query) #! strip  unecessary characters: (' " ;) etc. replace ' ' with '_'
	with open('./query_index/index.json') as f: #! open indexed queries
		search_index = json.load(f)

	if query in search_index: # check if query has already been indexed
		return search_index[query]
	else: # provide quick index and save query for later indexing
		results = quick_index(query)
		#what to do with the search
		if len(results) < 1:
			results = ['No results match your search :(']
		for res in results:
			print(res)
		print(len(results))
		return results

def index():
	pass


################## Handles Parsing ##################
def parse_controller(): #! intermediary handler for saving progress and executing. Maybe do 10 at a time then save?
	# loop through every html file downloaded and parse
	for filename in os.listdir('./to_parse/'): 
		domain, f_count = filename.split(']and[')
		f_count = f_count[:-4]

		with open(os.path.join('./to_parse/', filename), 'r') as f: # open in readonly mode 
			doc_text = parse(f.read(), domain) # pulls links and raw text from html
		
		
		#handles if crawl() errored out and didn't add url to links_crawled.json
		if doc_text is None:
			os.remove('./to_parse/'+filename)
			continue
		
		os.rename(f'./to_parse/{filename}', f'./parsed_html/{domain}/{f_count}') # moves html doc from parse queue to completed
		print('parsed: ',domain,f_count)
		print()

################## Handles Crawling New Sites ##################
def crawl_controller(): #! intermediary handler for saving progress and executing. Maybe do 10 at a time then save? reset session after 100 requests
	rec_time = pages_per_hour['min']
	now = datetime.datetime.now().minute 

	if rec_time + 10 < now: # check if it's a new 10 min period
		pages_per_hour['min'] += 10
		pages_per_hour['domain'] = {}
	elif now < rec_time: # is it a new hour
		pages_per_hour['min'] = 0
		pages_per_hour['domain'] = {}

	# refresh session to wipe cookies
	global sess
	sess = requests.Session()

	to_skip = tuple([d for d in pages_per_hour['domain'] if pages_per_hour['domain'][d] > hourly_limit])
	
	# dirty way to handle a tuple with 1 value aka: (x,)
	if len(to_skip) == 1:
		to_skip = '(\''+str(to_skip[0])+'\')'
	# prevent from visiting domains that have blocked the IP
	blocked = tuple([dom for dom in blocked_domains])

	# batch of pages for each thread
	urls = []
	global maxes
	maxes = {}

	# pull links
	#for x in range(THREAD_COUNT):
	if query(f'SELECT ptc.* FROM pages_to_crawl ptc WHERE ptc.domain NOT IN {to_skip} LIMIT {page_batch}'):
		urls = cursor.fetchall()
	else:
		print('unsuccessful in fetching links to crawl :(')
		return
		

	# pull max f_count per domain #! eventually combine into query above ^
	domains = [x[1] for x in urls]
	#occupied_domains += domains

	if query(f'SELECT MAX(filename), domain FROM pages_crawled WHERE domain IN {tuple(domains)} GROUP BY domain'):
		local_maxes = cursor.fetchall()
	else:
		print('unsuccessful in fetching MAX filename :(')
		return

	for m in local_maxes:
		maxes[m[1]] = int(m[0])


	#catch errors and send to failure table
	completed_links = [[],[],[]]	# 0 - success, 1 - failure, 2 - to delete

	# use one el from url_chunks for each thread. Make sure to declare global completed_links within threaded_crawl()

	print(len(urls),' urls ready to visit')

	#threaded_crawl(urls)


	for u in urls:
		url = u[0]
		domain = u[1]

		# check if this domain is in DB already. If so, use next number. If not, start at 0
		if domain in maxes:
			f_count = maxes[domain]+1
		else:
			f_count = 0
		
		# limit requests on a given domain to 1k per hour
		if domain in pages_per_hour['domain']:
			if pages_per_hour['domain'][domain] > hourly_limit:
				continue
			else:
				pages_per_hour['domain'][domain] += 1
		else:
			pages_per_hour['domain'][domain] = 1

		# eventually use this to index picture pages 
		#____these checks should happen in parsing already____
		if url[-4:].lower() in ['.jpg','.png','.gif','.svg','.mov','.mp4','.pdf','.wav','.mp3']: 
			completed_links[2].append(url)
			continue
		elif 'mailto:' in url:
			completed_links[2].append(url)
			continue

		# visit page
		success,error = visit_link(url, f_count)
		
		# handle errors
		if success is False:
			#if error == 1:
				# unknown connection error
				# domain blocked us 
				# blocked_domains.append(domain)
			completed_links[1].append((url,domain,dt.today().__str__(),error))
			completed_links[2].append(url)
			print(url)
			continue
		# add data tuple to be inserted
		if '/' in url:
			completed_links[0].append((url,domain,url.split('/',1)[1],dt.today().__str__(),f_count,f'{domain}/{f_count}.txt'))
		else:
			completed_links[0].append((url,domain,'unknown',dt.today().__str__(),f_count,f'{domain}/{f_count}.txt'))
		completed_links[2].append(url)
		# adjusts value for next url
		maxes[domain] = f_count

		print(url)





	# add to links_crawled table
	ins = '''INSERT INTO pages_crawled VALUES (?,?,?,?,?,?)'''
	if multi_query(ins,completed_links[0]):
		print('Successfully added to pages_crawled')

	# add to links_failed table
	ins = '''INSERT INTO failed_crawls VALUES (?,?,?,?)'''
	if multi_query(ins,completed_links[1]):
		print('Successfully added to failed_crawls')

	dels = tuple(completed_links[2])
	# dirty way to handle a tuple with 1 value aka: (x,)
	if len(dels) == 1:
		dels = '(\''+dels[0]+'\')'

	if query(f'DELETE FROM pages_to_crawl WHERE url in {dels}'):
		print('Successfully deleted from pages_to_crawl')

	try:
		conn.commit()
	except:
		print('unable to commit changes')

	print()


# set DB connection as global variable
try:
	conn,cursor = create_connection('./data.db')
except:
	print('failed to connect to DB. Exiting program')
	exit()

def main():
	print('Beginning crawl. Press ENTER to exit')
	starttime = dt.today()
	counter = 0
	while True:
		crawl_controller() # crawls all links
		parse_controller() #parse all docs in parsing queue for new links
		i,o,e = select.select([sys.stdin],[],[],0.0001) # listen for "Enter" key press
		if i == [sys.stdin]: 
			print('Successfully exited crawl')
			break
		counter += 1
		if counter > 99:
			global conn, cursor
			conn.close()
			try: conn,cursor = create_connection('./data.db')
			except:
				print('failed to connect to DB. Exiting program')
				exit()
		if (dt.today()-starttime).seconds > 85000: break
	conn.close()
main()



################## Handles Indexing ##################


################## Handles Regular Recrawl ##################
