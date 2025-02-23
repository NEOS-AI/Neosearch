import json
import os

new_fn_key = {}

with open('url_filename_key.json','r') as f: # preserves url relation to filenames
	url_filename_key = json.load(f)

filenames = os.listdir('./parsed_html/')

domains = []

errcount = 0

for fn in filenames:
	try:
		url = url_filename_key[fn.replace('.txt','')]
	except:
		errcount += 1
		continue
	dom_name = url.split('/')[0]
	if dom_name not in domains:
		print('domain made')
		domains.append(dom_name)
		os.mkdir(f'parsed_html/{dom_name}/')
		os.mkdir(f'parsed_text/{dom_name}/')
		new_fn_key[dom_name] = {}

	# check how many files exist in this domain
	page_index = len(os.listdir(f'./parsed_html/{dom_name}/'))

	# add filename to key
	new_fn_key[dom_name][page_index] = url
	# move file to domain folder
	os.rename(f'./parsed_html/{fn}',f'./parsed_html/{dom_name}/{page_index}')
	os.rename(f'./parsed_text/{fn}',f'./parsed_text/{dom_name}/{page_index}')


with open('new_url_to_fn.json','w') as f:
	json.dump(new_fn_key,f)


print('old: ',len(url_filename_key))
print('new: ',len(new_fn_key))

print()
print('errors: ',errcount)