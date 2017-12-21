from http.client import HTTPConnection
import json

body = json.dumps({"a" : 5 , "b" = 20})
head = {'Content-type': 'application/json'}

h1 = HTTPConnection("localhost:5000")
h1.request("POST", "/plainlib.package1.b.B", body, head))

data = h1.getresponse().read()
print(data)

id_ = json.loads(data)["id"]

h1.request("GET", "/plainlib.package1.b.B/" + id_)
data = h1.getresponse().read()
print(data)


