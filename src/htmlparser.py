

def gethtml():
    return """
    <html>
    <body>
    {content}
    </body>
    </html>
    """


def parse(msg):
    if not isinstance(msg, dict):
        return gethtml().format(content=msg)

    detailsform = """
    <details>
    <summary>{summary}</summary>
    {data}
    </details>
    """
    
    point = """
    <p>{text}</p>
    """

    content = "<h1>Logs</h1>"

    for keyname in msg:
        keydetail = ""
        item = msg[keyname]
        if isinstance(item, list):
            allpoints = ""
            for listitem in item:
                allpoints += point.format(text=listitem)
            keydetail = detailsform.format(summary=keyname, data=allpoints)
        content += keydetail
    return gethtml().format(content=content)

