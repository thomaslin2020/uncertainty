import requests

url = 'http://thomaslin2020.pythonanywhere.com/'
data = {'method': 'simple', 'equation': 'U(3,1)-U(5,1)+23'}
x = requests.post(url, data=data)

print(x.text)
