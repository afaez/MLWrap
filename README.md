# Pase
Python API Service Envirenment. 
This project offers a web server which offers access to python libraries with communication through JSON. 

# Code Example
Take a look at the following peace of python code:
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

The same operation can be realised using a Pase-service.
Assume the server is accessible through `localhost:5000/`.

First create the `LinearRegression` object `reg = sklearn.linear_model.LinearRegression(normalize=True)` with the following the http request:

```
POST /sklearn.linear_model.LinearRegression HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{"normalize":true}
```

The server then returns this JSON-string: `{"id": "85F09D2E65", "class": "sklearn.linear_model.base.LinearRegression"}`

Now the client can access the `LinearRegression` instance's attributes and methods through this url:

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


