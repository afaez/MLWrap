
from flask import Flask
from flask import request
application = Flask(__name__)

@application.route('/', defaults={'path': ''}, methods = ['POST', 'GET'])
@application.route('/<path:path>', methods=['POST', 'GET'])
def catch_all(path):
    print("PATH: ", path)
    print("---> Headers: \n", request.headers)
    # print("---> Body: \n", request.data)
    data = bytearray()
    chunk_size = 4096
    while True:
        chunk = request.stream.read(chunk_size)
        print("read stream : {}".format(chunk))
        if len(chunk) == 0:
            break
        else :
            data.extend(chunk)


    print("---> Sream length: \n", len(data)) 
    decodeddata = data.decode()
    print("---> Sream: \n", decodeddata)

    return "success"

if __name__ == '__main__':
    from werkzeug.serving import WSGIRequestHandler
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    application.run("localhost", port = 5000, debug = True)