# Pase

Python API Service Envirenment. 
This project offers a web server which offers access to python libraries with communication through JSON. 

# Code Example
Take a look at the following piece of python code:
```
>>> import sklearn.linear_model
>>> reg = sklearn.linear_model.LinearRegression(normalize=True)
>>> reg.fit(X = [[0,0], [1,1], [2,2]], y = [0,1,2])
LinearRegression(copy_X=True, fit_intercept=True, n_jobs=1, normalize=True)
>>> reg.coef_
array([ 0.5,  0.5])
>>> reg.predict(X = [[0.5, 1], [1, 0.5]])
array([ 0.75,  0.75])
```

The same operations can be realised using a Pase-service.
Assume the server is accessible through `localhost:5000/`.

First create the `LinearRegression` object `reg = sklearn.linear_model.LinearRegression(normalize=True)` with the following http request:

```
POST /sklearn.linear_model.LinearRegression HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{"normalize":true}
```

The server then returns this JSON-string: `{"id": "85F09D2E65", "class": "sklearn.linear_model.base.LinearRegression"}`

Now the client can access `LinearRegression` instance's attributes and methods through this url:

`localhost:5000/sklearn.linear_model.base.LinearRegression/85F09D2E65`

The equivalent of the `reg.fit(X = [[0,0],[1,1],[2,2]], y = [0,1,2])` line would be this http call:

```
POST /sklearn.linear_model.base.LinearRegression/85F09D2E65/fit HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{"X" : [[0,0],[1,1],[2,2]], "y" : [0,1,2]}
```

Retrieving the value of `reg.coef_` can be done with a `GET` request:
```
GET /sklearn.linear_model.base.LinearRegression/85F09D2E65/coef_ HTTP/1.1
Host: localhost:5000
```
Server response: `{"dtype": "float64", "values": [0.5, 0.5]}`

Returning the result of `reg.predict(X = [[0.5,1],[1,0.5]])` is done similarly to the `fit` call from before:
```
POST /sklearn.linear_model.base.LinearRegression/85F09D2E65/predict HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{"X" : [[0.5, 1], [1, 0.5]]}
```
Server response: `{"dtype": "float64", "values": [0.75, 0.75]}`

# Installation
To create a Pase-service clone this repository and run `bash service.sh`

The shell script resolves dependencies and checks if at least Python 3.6 is used. Afterwards it makes the server available on the port specified by the command line parameter. (e.g.: `bash service.sh 200`)

Make sure libraries that are used by the client are accessible by the server. To create the `LinearRegression` object from above the scikit-learn framework is needed. One option is to add install commands to the first bracket of `service.sh`. e.g. adding `pip install sklearn` makes the scikit-learn framework available.

# Configuration
`conf/whitelist.ini` contains constructors that are allowed to be created by clients.
To whitelist a constructor, add a new line consisting of the fully qualified constructor name followed by a equal sign followed by True.

If debug = True is specified in `whitelist.ini`, debug mode is enabled. Consequently:
* Flask is started in debug mode.
* No whitelist checks are made. Thus every constructor can be created through http calls.

# API Reference
Say `<host>` accesses the running pase server.

### Creation
Creating objects using constructor or class-methods:

method = `POST`

url = `<host>\<fully-qualified-contructor-name>`

body = JSON encoded parameters for the constructor. JSON variable names need to be identical to the parameter names in python.

returns = JSON with two values: "id", "class"

Use `<host>\<class>\<id>` to access the created object.

### State
Retrieving object state:

method = `GET`

url = `<host>\<class>\<id>`

returns = JSON encoded state of the object

### Attribute
Retrieve or set the value of a object's attribute (called `<attr>`):

method = `GET` (to retrieve value), `POST` (to retrieve or set value)

url = `<host>\<class>\<id>\<attr>`

body (if `POST`) = JSON encoded parameter. Map `"value"` to the expected value. e.g.: `{"value" : 10}`

returns = JSON encoded value of the accessed attribute (value after assignment)

### Function

Call a function called `<func>`:

method = `POST`

url = `<host>\<class>\<id>\<func>`

body = JSON encoded parameters for the function. JSON variable names need to be identical to the parameter names in python.

returns = JSON encoded return value of the function call

## Access modifiers

Access modifiers are url alterations that modify the server behaviour. Use access modifier names after `<class>` and before `<id>` in urls.

### Safe access modifier

To guarantee that the state of the object doesn't change after calling methods or accessing attributes  operate like above but use the following urls instead: 

`<host>\<class>\safe\<id>\<attr>`

`<host>\<class>\safe\<id>\<func>`

### Copy access modifier

Use 'copy' when you want to clone an instance:

`GET <host>\<class>\copy\<id>`

Use 'copy' while accessing an attribute or calling a method (the same way done above) to copy the (result)value to a new instance object:

`<host>\<class>\copy\<id>\<attr>`

`<host>\<class>\copy\<id>\<func>`

The response from a copy access is identical to the response from Creation.
