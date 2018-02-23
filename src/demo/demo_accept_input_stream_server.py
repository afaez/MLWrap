
from flask import Flask
from flask import request
application = Flask(__name__)
from werkzeug.serving import WSGIRequestHandler
WSGIRequestHandler.protocol_version = "HTTP/1.1"

@application.route('/', defaults={'path': ''}, methods = ['POST', 'GET'])
@application.route('/<path:path>', methods=['POST', 'GET'])
def catch_all(path):
    request.environ['wsgi.input_terminated'] = True
    # print("PATH: ", path)
    print("---> Headers: \n", request.headers)
    # body = request.get_json(force = True, silent = True) 
    # print("---> Body: \n", body)
    data = bytearray()
    chunk_size = 4096
    # stream = request.environ['input']
    while True:
        chunk = request.stream.read(chunk_size)
        print("read stream : {}".format(len(chunk)))
        if len(chunk) == 0:
            break
        else :
            data.extend(chunk)


    print("---> Sream length: \n", len(data)) 
    decodeddata = data.decode()
    # print("---> Sream: \n", decodeddata)

    return "success"

if __name__ == '__main__':
    application.run("000.000.000.000", port = 5000, debug = True)