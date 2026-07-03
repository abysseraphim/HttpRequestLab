def parse_request(raw_request):
    lines = raw_request.split('\n')
    requestLine = lines[0]
    requestLineParts = requestLine.split(" ")
    
    reqMethod = requestLineParts[0]
    reqPathQuery = requestLineParts[1]
    reqHttpVer = requestLineParts[2]

    headers = dict()
    headersStart = lines[1:]
    for line in headersStart:
        if line:
            header, value = line.split(":", 1)
            headers[header.strip()] = value.strip()
        else:
            break

    body_start = None

    for i, line in enumerate(lines):
        if line == "":
            body_start = i + 1
            break

    requestBody = "\n".join(lines[body_start:])

    return {
        "method" : reqMethod,
        "path" : reqPathQuery,
        "version" : reqHttpVer,
        "headers" : headers,
        "body" : requestBody
    }