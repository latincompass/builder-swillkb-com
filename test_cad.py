import requests
import json

data = {
    'switch-type': '0',
    'stab-type': '0',
    'case-type': '',
    'layout': '[["Num Lock","/","*","-"],["7\\nHome","8\\n↑","9\\nPgUp",{"h":2},"+"],["4\\n←","5","6\\n→"],["1\\nEnd","2\\n↓","3\\nPgDn",{"h":2},"Enter"],[{"w":2},"0\\nIns",".\\nDel"]]'
}

response = requests.post('http://localhost:8888/', data=json.dumps(data), headers={'Content-Type': 'application/json'})
print('Status:', response.status_code)
print('Response:', response.text[:2000])
