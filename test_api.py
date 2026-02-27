import requests

API_KEY = 'AIzaSyAkwXwDtQSHOiJoxw8UJIcFuZlYHzqb1Bw'

# Test the API key
url = f'https://generativelanguage.googleapis.com/v1/models?key={API_KEY}'

response = requests.get(url)
print('Status:', response.status_code)
print('Response:', response.json())