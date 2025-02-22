import sqlite3
from sqlite3 import Error
import json
import os


'''
#with open('fn_to_url.json') as f:
#	fn_to_url = json.load(f)
#with open('links_crawled.json') as f:
#	links_crawled = json.load(f)
with open('links_to_crawl.json') as f:
	links_to_crawl = json.load(f)

rows = []


for row in links_to_crawl:
	domain = row.split('/')[0]
	domain = domain.replace('https://','').replace('http://','')
	rows.append((row, domain))

#(url, domain, page, date_accessed, filename, relative_path)
'''

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

def query(q,val=''):
	try:
		cursor.execute(q,val)
	except Error as e:
		print(e)


conn,cursor = create_connection('./data.db')


'''
page_batch = 10
query(f'SELECT ptc.* FROM pages_to_crawl ptc LEFT JOIN pages_visited pv ON ptc.url = pv.url AND pv.url IS NULL LIMIT {page_batch}')

resp = cursor.fetchall()
for r in resp:
	print(r)

domains = tuple([x[1] for x in resp])

query(f'SELECT MAX(filename), domain FROM pages_visited WHERE domain IN {domains} GROUP BY domain')
maxes = cursor.fetchall()
print(maxes)


query('SELECT url, count(*) FROM failed_crawls GROUP BY url HAVING count(*) > 1')
vals = cursor.fetchall()

print(vals)
'''






with open('domains','r') as f:
	dom = f.readlines()
dom[:] = [(x,) for x in dom]

print(len(dom))

cursor.executemany("INSERT INTO blacklisted_domains VALUES (?)",dom)
conn.commit()

"""

table_create2 = '''
CREATE TABLE pages_to_crawl
(url, domain)
'''

table_create3 = '''
CREATE TABLE failed_crawls
(url, domain, date_attempted, error)
'''


rows = ''''''
insert = '''
INSERT INTO pages_to_crawl VALUES (?,?)
'''

try:
	cursor.executemany(insert, rows)
except Error as e:
	print(e)
	print('insert didnt work')
"""
#query(cursor, table_create)
#query(cursor, table_create2)
#query(cursor, table_create3)
#query(cursor, insert)

try:
	conn.commit()
except:
	print('unable to commit changes')


conn.close()
print('connection has been closed')


