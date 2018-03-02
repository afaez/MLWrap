

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
    <ul>
    {data}
    </ul> 
    </details>
    """
    point = """
    <li><tt>{text}</tt></li>
    """

    content = "<h1>Logs</h1>"

    for keyname in msg:
        keydetail = ""
        item = msg[keyname]
        if isinstance(item, list):
            allpoints = ""
            for listitem in item:
                text = listitem
                if "ERROR" in listitem:
                    text = """<font color="darkred">{data}</font>""".format(data=listitem)
                elif "INFO" in listitem:
                    text = """<font color="darkgreen">{data}</font>""".format(data=listitem)
                else:
                    text = listitem
                allpoints += point.format(text=text)
            
            keydetail = detailsform.format(summary=keyname, data=allpoints)

        content += keydetail
    return gethtml().format(content=content)

