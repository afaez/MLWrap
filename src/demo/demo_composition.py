import http.client
import json 

conn = http.client.HTTPConnection("localhost:5000")

payload = """
{
	"execute" : "f1 = plainlib.package1.b.B::__construct({a = 1, b = 2});f2 = f1::calc({c=3});f3 = plainlib.package1.b.B::random();",
	"return" : ["f1", "f2", "f3"]
}
"""

headers = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'postman-token': "c32198ed-e7af-6e58-05a7-b8694754284f"
    }

conn.request("POST", "/composition", payload, headers)

res = conn.getresponse()
data = res.read()
prettyprint = json.dumps(json.loads(data), indent=2)

print(prettyprint)

# Request with inputs:

payload = """
{
	"execute" : "f1 = plainlib.package1.b.B::__construct({a = in1, b = in2});f2 = f1::calc({c=3});",
	"return" : ["f1", "f2"],
    "input" : 
    {
        "in1" : 2,
        "in2" : 3
    }
}
"""
conn.request("POST", "/composition", payload, headers)
res = conn.getresponse()
data = res.read()
prettyprint = json.dumps(json.loads(data), indent=2)

print(prettyprint)