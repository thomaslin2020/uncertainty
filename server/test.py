import requests

url = 'http://localhost:5001/'
data = {'method': 'simple', 'equation': 'ln(arctan(U(3,5)-log(U(2.4,6))))+pi'}
x = requests.post(url, data=data)

print(x.text)
