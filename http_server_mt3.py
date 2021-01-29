'''    Basic threaded http server implementation    '''
#!/usr/bin/env python3
import socketserver
import http.server
import sys
import time
import urllib
import json

#-------------sample functions--------------------
keyval={}
def kput(a,b):
    keyval[a]=b
    return json.dumps({a:b})

def kget(a):
    return keyval.get(a)

def add2numbers(a,b):
    return int(a)+int(b)

def handlejob(func_and_params):
    func=func_and_params[0]
    params=func_and_params[1:]
    if func=="add": return add2numbers(params[0],params[1])
    if func=="put": return kput(params[0],params[1])
    if func=="get": return kget(params[0])
    return "Unknown Command"
#-^-^--^-^-^-^sample functions-^-^-^-^-^-^-^-^-^-^-


class Handler(http.server.BaseHTTPRequestHandler):
    '''   use our own handlers functions '''

    def sendtextinfo(self, code, text):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        if type(text)==type([]):
            for lines in text:
                self.wfile.write((str(lines)+"\n").encode())
        else:
            self.wfile.write((str(text)+"\n").encode())

    def do_GET(self):
        '''   handle get   '''
        tnow = time.time()
        gnow = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(tnow)) #Formatted UTC time
        parsed_data = urllib.parse.urlparse(self.path)
        if parsed_data.geturl().lower() == "/time":
            message = gnow
        else : message="this is a test of the multithreaded webservice"
        self.sendtextinfo(200,message)

    def do_POST(self):
        '''   handle post like rest API   '''
        try: #try getting the bytestream of the request
            content_length = int(self.headers['Content-Length'])
        except Exception as err:
            print("malformed headers")
            self.sendtextinfo(200,str(err))
            return

        if content_length > 0:
            rawrequest = self.rfile.read(content_length).decode('utf-8')
            print("Received POST: {}".format(rawrequest))
            try:
                jrequest = json.loads(rawrequest)
            except BaseException as anError:
                self.sendtextinfo(200,"Error in JSON: {}".format(str(anError)))
                return

        if "cmd" in jrequest:
            commandandparams=jrequest['cmd']
            print("Command received: {}".format(commandandparams))
            result=handlejob(commandandparams)
            if result != None:
                self.sendtextinfo(200,result)
            else:
                self.sendtextinfo(200,"No Output")
        return


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    '''    Basic threaded server class    '''
    http.server.HTTPServer.request_queue_size = 128

if sys.argv[1:]:
    HTPORT = int(sys.argv[1])
else:
    HTPORT = 8000

HTSERVER = ThreadedHTTPServer(('', HTPORT), Handler)

try:
    while 1:
        sys.stdout.flush()
        HTSERVER.handle_request()
except KeyboardInterrupt:
    print("Server Stopped")
