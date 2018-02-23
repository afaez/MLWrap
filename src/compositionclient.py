import logging
import pase.marshal
import requests
import json
from pase.composition import Choreography
from pase.servicehandle import ServiceHandle
from pase.pase_dataobject import PASEDataObject

def forwardoperation(state, currentindex, choreography):
    """ Forwards the chorepgraphy to the next service.
    """
    choreography.currentindex = currentindex # the operation of the current execution
    maxindex = currentindex  # the maximum (noninclusive) index which has to be executed by another service. 
    # iterate over the rest of the operations:
    for operation in choreography.operation_list[currentindex:]:
        if not operation.canexecute(state):
            # cannot execute this operation
            maxindex += 1
        else:
            break # the rest will be executed on this server again.

    logging.info(f"Forwarding composition={choreography.originalstring} with currentindex={currentindex} and maxindex={maxindex} to the next service.")
    
    nextoperation = choreography.operation_list[currentindex]
    # try to find the hostname of the next operation:
    hostname = None
    if nextoperation.host != "$empty$":
        #operation has the url in itself
        hostname = nextoperation.host
    elif nextoperation.clazz in state:
        instance = state[nextoperation.clazz]
        if isinstance(instance, ServiceHandle) and instance.is_remote():
            # a service handle was defined that knows its host name:
            hostname = instance.host
        
    if hostname is None:     
        error = f"This {nextoperation} operation can't be executed on this server but it doesn't include any other server that can execute it either."
        logging.error(error)
        raise ValueError(error)

    url = "http://" + hostname + "/choreography"

    forwardedinputs = dict()

    for variablename in state:
        variable = state[variablename]
        if isinstance(variable, ServiceHandle):
            if not variable.is_remote():
                continue # dont pass local services
            if variable.host == hostname: 
                # if the host we are contacting is the owner of the service,
                #  rewrite host of the servicehandle as "local"
                forwardedinputs[variable] = variable.with_host("local")
        else:
            forwardedinputs[variablename] = variable
            
    logging.debug(f"forwarding to {hostname} with inputs fieldnames {[fieldname for fieldname in forwardedinputs]}")

    payload = to_bodystring(currentindex, maxindex, forwardedinputs, choreography.originalstring)
    url = "http://" + nextoperation.host + "/choreography"
    responsestring = requests.request("POST", url, data=payload, headers={}).text
    # logging.debug(f"Received a return from a forwarded call: {responsestring}")
    try:
        responsedict = json.loads(responsestring)
        # add the calculated variables to the current state:
        returnedBody = Choreography.fromdict(responsedict, remote_host=hostname)
        
        # TODO
        # if returnedBody.currentindex <= currentindex: 
        #     raise ValueError("The returned currentindex is equal or below the one we had before:{}".format(returnedBody.currentindex)) 
        # else:
        #     choreography.currentindex = returnedBody.currentindex

        for newvarname in returnedBody.input_dict:
            if newvarname in state:
                continue # dont add var names that were there before
            newvar = returnedBody.input_dict[newvarname]
            # logging.debug("adding to state: " + str(newvar))
            # if isinstance(newvar, PASEDataObject) and isinstance(newvar.data, ServiceHandle):
            #     newvar = newvar.data # unwrap the Servicehandle
            #     if not newvar.is_remote():
            #         newvar.host = hostname # translate the host: local to remote hostname
            state[newvarname] = newvar

    except Exception as ex:
        logging.error(ex, exc_info=True)
        
    # set the currentindex to the progress point made by the forward call:
    choreography.currentindex = maxindex # TODO:  set the current index by the value returned from the forwarded message.
    # now return to servicehandler to execute the rest


def to_bodystring(currentindex, maxindex, inputs, coreographystring):
    requestbody = Choreography.todict(composition = coreographystring, currentindex=currentindex, maxindex=maxindex, variables = inputs)

    # logging.debug("Sending body: " + str(requestbody))
    returnstring = json.dumps(requestbody)
    #f"currentindex={currentindex}&maxindex={maxindex}&coreography={coreographystring}"
    # for var in inputs:
    #     if var == "$arglist$":
    #         continue # don't parse arglist.
    #     try:
    #         stringencoded = pase.marshal.marshaldict(inputs[var])
    #         returnstring += f"&inputs[{var}]={stringencoded}"
    #     except Exception as ex:
    #         logging.error("Error when parsing state in composition client: " + ex)
    return returnstring

