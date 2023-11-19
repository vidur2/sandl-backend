# Sandl Backend
In order to query the backend with the requests library do the following

If account exists:
```python
import requests
res = requests.post("http://localhost:3000/login", json={"email": "<email here>", "password": "<password>"})
res = requests.post("http://localhost:3000/get_intent", json={"jwt": res.json()["jwt"], "prompt": "Hello World"})
value = res.json()["certaintyValue"]
```
or to sign up
```python
import requests
res = requests.post("http://localhost:3000/sign_up", json={"email": "<email here>", "password": "<password>"})
res = requests.post("http://localhost:3000/get_intent", json={"jwt": res.json()["jwt"], "prompt": "Hello World"})
value = res.json()["certaintyValue"]
```