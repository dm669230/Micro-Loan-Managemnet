def HttpResponseFormatter(data = None, response_code = 200, error_message = None, message = None ):
    if response_code == 200:
        return  {
                'status_code': 200, 
                'message':"Response Recieved Successfully" if message is None else message,
                'data' : data
                }
    else:
        return  {
                'status_code': 400, 
                'message':f"Unable to get the response : {error_message}" if message is None else message,
                'data' : []
                }
