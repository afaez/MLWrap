
from flask import Flask
from flask import request
from pase import composition
import servicehandler
application = Flask(__name__)

#set up logging:
import logging
import datetime
now  = datetime.datetime.now()
logfilename = "paselog.log"#_{}.log".format(now.strftime("%Y-%m-%d_%H-%M-%S"))
logging.basicConfig(filename=logfilename,level=logging.DEBUG) # TODO get logging lvl from configuration


@application.route('/', defaults={'path': ''}, methods = ['POST', 'GET'])
@application.route('/<path:path>', methods=['POST', 'GET'])
def catch_all(path):
    # equivalent to 'handle' in pase
    logging.info(f"Request with url: {path}")
    logging.debug(f"---> Headers: {request.headers}\n")
    body = readhttpstream(request)
    #logging.debug(f"---> Body: {body}\n")
    choreo = composition.Choreography.fromstring(body)
    return servicehandler.execute_composition(choreo)

def readhttpstream(request):
    """ Reads the bytes in the http stream and returns the decoded string.
    """
    length = request.headers.get("Content-Length", type = int)
    data = bytearray()
    chunk_size = length
    while True:
        # Read chunk from the stream
        chunk = request.stream.read(chunk_size)
        if len(chunk) != 0:
            # put data into array
            data.extend(chunk)
        else :
            # chunk is empty
            break
    #print("---> Sream length: \n", len(data)) 
    # Decode data using utf-8 and replace.
    decodeddata = data.decode("utf-8", "replace")
    #print("---> Sream: \n", decodeddata[:])
    return decodeddata


if __name__ == '__main__':
    from werkzeug.serving import WSGIRequestHandler
    WSGIRequestHandler.protocol_version = "HTTP/1.1" # Set to http/1.1 to support 'keep-alive'
    application.run("localhost", port = 5000, debug = True)