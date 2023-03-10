import json
import requests

#Add your Microsoft Account Key to a file called bing.key
def read_bing_key():
	"""
	reads the BING API key from a file called 'bing.key'
	returns: a string which is either None, i.e no key found, or with a key 
	remember to put bing.key in your .gitignore file to avoid committing it.
	
	See Python Anti-Patterns - it is an awesome resource to improve your python code
	Here we using "with" when opening documents
	http://bit.ly/twd-antipattern-open-files    
	"""
	bing_api_key = None
	try:
		with open('bing.key','r') as f:
			bing_api_key = f.readline().strip()
	except:
		try:
			with open('../bing.key') as f:
				bing_api_key = f.readline().strip()
		except:
			raise IOError('bing.key file not found')
		
	if not bing_api_key:
			raise KeyError('Bing key not found')
	return bing_api_key


def run_query(search_terms):
	"""
	See the Microsoft's documentation on the other parameters that you can set.
	http://bit.ly/twd-bing-api
	"""
	try:
		bing_key = read_bing_key()
		search_url = 'https://api.bing.microsoft.com/'
		headers = {'Ocp-Apim-Subscription-Key': bing_key}
		params = {'q': search_terms, 'textDecorations': True, 'textFormat':' HTML'}

		#Issue the request, given the details above.
		response = requests.get(search_url, headers=headers, params=params)
		response.raise_for_status()
		search_results = response.json()

		#With the response now in play, build up a python list.
		results = []
		for result in search_results['webPages']['value']:
			results.append({
				'title': result['name'],
				'link': result['url'],
				'summary': result['snippet']
			})
		return results
	except requests.exceptions.RequestException as e:
		print("An error occurred while making the request:", e)


def main():
	#Insert your code here. What will you write?
	search_items = input("What are you looing for?")
	run_query(search_items)


if __name__ == '__main__':
	main()