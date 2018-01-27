import logging
import pase.marshal
import requests
import json

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

    logging.info("Forwarding composition to the next service.")
    
    nextoperation = choreography.operation_list[currentindex]
    if nextoperation.host == "$empty$":
        error = f"This {nextoperation} operation can't be executed on this server but it doesn't include any other server that can execute it either."
        logging.debug(error)
        raise ValueError(error)
    
    payload = to_bodystring(currentindex, maxindex, state, choreography.originalstring)
    url = "http://" + nextoperation.host + "/choreography"
    responsestring = requests.request("POST", url, data=payload, headers={}).text
    logging.info(f"Received a return from a forwarded call")
    try:
        responsedict = json.loads(responsestring)
        # add the calculated variables to the current state:
        for newvar in responsedict:
            if newvar not in state:
                state[newvar] = responsedict[newvar]
    except Exception as ex:
        logging.error(ex, exc_info=True)
        
    # set the currentindex to the progress point made by the forward call:
    choreography.currentindex = maxindex
    # now return to servicehandler to execute the rest


def to_bodystring(currentindex, maxindex, inputs, coreographystring):
    returnstring = f"currentindex={currentindex}&maxindex={maxindex}&coreography={coreographystring}"
    for var in inputs:
        if var == "$arglist$":
            continue # don't parse arglist.
        stringencoded = pase.marshal.marshal(inputs[var])
        returnstring += f"&inputs[{var}]={stringencoded}"
    return returnstring

