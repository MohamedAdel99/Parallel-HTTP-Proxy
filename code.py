# Don't forget to change this file's name before submission.
import sys
import os
import enum
import socket,threading

class HttpRequestInfo(object):
    """
    Represents a HTTP request information

    Since you'll need to standardize all requests you get
    as specified by the document, after you parse the
    request from the TCP packet put the information you
    get in this object.

    To send the request to the remote server, call to_http_string
    on this object, convert that string to bytes then send it in
    the socket.

    client_address_info: address of the client;
    the client of the proxy, which sent the HTTP request.

    requested_host: the requested website, the remote website
    we want to visit.

    requested_port: port of the webserver we want to visit.

    requested_path: path of the requested resource, without
    including the website name.

    NOTE: you need to implement to_http_string() for this class.
    """

    def __init__(self, client_info, method: str, requested_host: str,
                 requested_port: int,
                 requested_path: str,
                 headers: list):
        self.method = method
        self.client_address_info = client_info
        self.requested_host = requested_host
        self.requested_port = requested_port
        self.requested_path = requested_path
        # Headers will be represented as a list of lists
        # for example ["Host", "www.google.com"]
        # if you get a header as:
        # "Host: www.google.com:80"
        # convert it to ["Host", "www.google.com"] note that the
        # port is removed (because it goes into the request_port variable)
        self.headers = headers

    def to_http_string(self):
        """
        TO THE BASE FORM
        GET path version
        host:
        headers.....\r\n
        """
        request_line=self.method+" "+self.requested_path+" HTTP/1.0\r\n"
        y=[]
        for i in self.headers:
            y.append(': '.join(i))
        pass
        mylist = list(dict.fromkeys(y))
        fullheaders='\r\n'.join(mylist)
        Fullstring=request_line+fullheaders+'\r\n'+'\r\n'
        return Fullstring

    def to_byte_array(self, http_string):
        """
        Converts an HTTP string to a byte array.
        """
        return bytes(http_string, "UTF-8")

    def display(self):
        print(f"Client:", self.client_address_info)
        print(f"Method:", self.method)
        print(f"Host:", self.requested_host)
        print(f"Port:", self.requested_port)
        stringified = [": ".join([k, v]) for (k, v) in self.headers]
        print("Headers:\n", "\n".join(stringified))


class HttpErrorResponse(object):
    """
    Represents a proxy-error-response.
    """

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def ERRORstring(self):
        msg = "HTTP/1.0" +" "+ str(self.code) +" , "+ self.message +"\r\n\r\n"
        return msg
        

    def to_byte_array(self, http_string):
        """
        Converts an HTTP string to a byte array.
        """
        return bytes(http_string, "UTF-8")

    def display(self):
        print(self.ERRORstring())


class HttpRequestState(enum.Enum):
    """
    The values here have nothing to do with
    response values i.e. 400, 502, ..etc.

    Leave this as is, feel free to add yours.
    """
    INVALID_INPUT = 0
    NOT_SUPPORTED = 1
    GOOD = 2
    PLACEHOLDER = -1


def entry_point(proxy_port_number):
    """
    Entry point, start your code here.

    Please don't delete this function,
    but feel free to modify the code
    inside it.
    """
    setup_sockets(proxy_port_number)
    return None


def setup_sockets(proxy_port_number):
    """
    SOCKET START
    """
    print("Starting HTTP proxy on port:", proxy_port_number)
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',int(proxy_port_number)))
    s.listen(10)
    while True:
       connection, address = s.accept()
       threading._start_new_thread(do_socket_logic,(s,connection,address))
    pass


def do_socket_logic(sock,clientc,address):
    print('** PROXY RUNNING **')
    st=''
    cache={}
    while True:
        if(st.endswith('\r\n')):
            sock.close
            break
        else:
            DATA=clientc.recv(1024).decode("utf-8")
            st=DATA            
    Process=http_request_pipeline(address,DATA)
    msg,reqparsed=Process
    clientc.send(msg)
    if reqparsed == '':
        sys.exit
        sock.close
    else:    
        w=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host_ip =socket.gethostbyname(reqparsed.requested_host) 
        port = reqparsed.requested_port
        bytereq=reqparsed.to_byte_array(reqparsed.to_http_string())
        if(bytereq in cache): #caching
            resp=cache[bytereq]
            clientc.send(resp)
        else:    
            w.connect((host_ip, port)) #remote host connect
            w.send(bytereq)   
            while True:
                response=w.recv(1024) 
                cache[bytereq]=response             
                clientc.send(response) 
        w.close               
pass


def http_request_pipeline(source_addr, http_raw_data):
    """
    validate and then
    Here we test and check if BAD or NI request 
    then parse
    sanitize
    returnes error message , sanitzed form
    """
    # Parse HTTP request
    validity = check_http_request_validity(http_raw_data)
    if validity == HttpRequestState.INVALID_INPUT:
        print("invalid")
        emsg=HttpErrorResponse(400,'Bad request')
        emsg2=emsg.to_byte_array(emsg.ERRORstring())
        sanitized=''
    elif validity == HttpRequestState.NOT_SUPPORTED:
         print("invalid")
         emsg=HttpErrorResponse(501,'Not Implemented')
         emsg2=emsg.to_byte_array(emsg.ERRORstring())
         sanitized=''
    else:
         emsg2=b''
         parsed=parse_http_request(source_addr,http_raw_data)
         sanitized=sanitize_http_request(parsed) 
    return emsg2,sanitized


def parse_http_request(source_addr, http_raw_data):
    """
    This function parses a "valid" HTTP request into an HttpRequestInfo
    object.
    """
    # Replace this line with the correct values.
    c = http_raw_data.split("\r\n")
    method = c[0].split(' ')[0]
    if c[0].split(' ')[1][0]=='/': #relative form
       host=c[1].split(':')[1][1:]
       if '/' in host[7:] :
         path="/"+host[7:].split('/')[1]
       else:
          path=c[0].split(' ')[1] 
       pass  
       if ':' in c[1].split(':')[1]: #port splitting
          res = [int(i) for i in c[0].split(' ')[1].split(":")[1] if  i.isdigit()]
          port = int("".join(map(str, res)))
          host=host.split(':')[0]
       else:
          port=80   
    elif c[0].split(' ')[1][0]!='/': #absloute form
       if(c[0].split(' ')[1][0]=='h'):
           host=c[0].split(' ')[1].split('://')[1]
           path=host
       else:  
          host=c[0].split(' ')[1] 
          path=host
       if ':' in host:
          res = [int(i) for i in host.split(":")[1] if  i.isdigit()]
          port = int("".join(map(str, res)))
          host=host.split(':')[0]
          path=host
       else:
          port=80   
    pass 
    header=[]
    for i in c[1:]:
        if(i!=''):
         x=i.split(': ')
         header.append(x)
        else:
         break
    pass
    ret = HttpRequestInfo(source_addr, method, host,port, path, header)
    return ret


def check_http_request_validity(http_raw_data) -> HttpRequestState:
    """
    all test cases passed
    """
    c = http_raw_data.split("\r\n")
    if c[0].split(" ")[0] not in ['GET','HEAD','POST','PUT'] or len(c[0].split(" ") )< 3 :
       return HttpRequestState.INVALID_INPUT 
    elif c[0].split(" ")[1][0] =='/' and c[1].split(":")[0]!='Host':
        return HttpRequestState.INVALID_INPUT 
    elif c[1]!='' and c[0].split(" ")[1][0] =='w' and ':' not in c[1] or c[0].split(" ")[2] not in ['HTTP/1.0','HTTP/1.1','HTTP/2.0']:
        return HttpRequestState.INVALID_INPUT    
    elif c[0].split(" ")[0] in ['HEAD','POST','PUT']:
       return HttpRequestState.NOT_SUPPORTED
    else:
      return HttpRequestState.GOOD
    pass   


def sanitize_http_request(request_info: HttpRequestInfo):
    """
    Puts an HTTP request on the sanitized (standard) form
    by modifying the input request_info object.

    for example, expand a full URL to relative path + Host header.

    returns:
    nothing, but modifies the input object
    """
    if request_info.requested_path==request_info.requested_host:
       hosthead="Host:"+request_info.requested_host.split('/')[0]
       z=hosthead.split(":")
       request_info.headers.insert(0,z)    
       if(len(request_info.requested_path.split('/'))>1):
            request_info.requested_path=request_info.requested_host[len(request_info.requested_host.split('/')[0]):]
       else:
          request_info.requested_path='/'
       pass    
    pass
    if(len(request_info.requested_host.split('/')[0])>1):
        request_info.requested_host=request_info.requested_host.split('/')[0]
    return request_info

#######################################
# Leave the code below as is.
#######################################


def get_arg(param_index, default=None):
    """
        Gets a command line argument by index (note: index starts from 1)
        If the argument is not supplies, it tries to use a default value.

        If a default value isn't supplied, an error message is printed
        and terminates the program.
    """
    try:
        return sys.argv[param_index]
    except IndexError as e:
        if default:
            return default
        else:
            print(e)
            print(
                f"[FATAL] The comand-line argument #[{param_index}] is missing")
            exit(-1)    # Program execution failed.


def check_file_name():
    """
    Checks if this file has a valid name for *submission*

    leave this function and as and don't use it. it's just
    to notify you if you're submitting a file with a correct
    name.
    """
    script_name = os.path.basename(__file__)
    import re
    matches = re.findall(r"(\d{4}_){,2}lab2\.py", script_name)
    if not matches:
        print(f"[WARN] File name is invalid [{script_name}]")
    else:
        print(f"[LOG] File name is correct.")


def main():
    """
    Please leave the code in this function as is.

    To add code that uses sockets, feel free to add functions
    above main and outside the classes.
    """
    print("\n\n")
    print("*" * 50)
    print(f"[LOG] Printing command line arguments [{', '.join(sys.argv)}]")
    check_file_name()
    print("*" * 50)

    # This argument is optional, defaults to 18888
    proxy_port_number = get_arg(1, 18888)
    entry_point(proxy_port_number)


if __name__ == "__main__":
    main()
