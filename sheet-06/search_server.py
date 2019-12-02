"""
Copyright 2019, University of Freiburg,
Chair of Algorithms and Data Structures.
Author: Hannah Bast <bast@cs.uni-freiburg.de>
"""

import socket
import sys
from qgram_index import QGramIndex
import re

class SearchServer:
    """
    A HTTP search server using a q gram index.

    No pre-defined tests are required this time. However, if you add new
    non-trivial methods, you should of course write tests for them.

    Your server should behave like explained in the lecture. For a given
    URL of the form http://<host>:<port>/search.html?q=<query>, your server
    should return a (static) HTML page that displays (1) an input field and a
    search button as shown in the lecture, (2) the query without any URL
    encoding characters and (3) the top-5 entities returned by your q-gram
    index (from exercise sheet 5) for the query.

    In the following, you will find some example URLs, each given with the
    expected query (%QUERY%) and the expected entities (%RESULT%, each in the
    format "<name>;<score>;<description>") that should be displayed by the
    HTML page returned by your server when calling the URL. Note that, as
    usual, the contents of the test cases is important, but not the exact
    syntax. In particular, there is no HTML markup given, as the layout of
    the HTML pages and the presentation of the entities is up to you. Please
    make sure that the HTML page displays at least the given query and the
    names, scores and descriptions of the given entities in the given order
    (descending sorted by scores).

     URL:
      http://<host>:<port>/search.html?q=angel
     RESPONSE:
      %QUERY%:
        angel
      %RESULT%:
       ["Angela Merkel;180;Chancellor of Germany",
        "Angelina Jolie;137;American actress, film director, and screenwriter",
        "angel;122;supernatural being or spirit in certain religions and\
                mythologies",
        "Angel Falls;76;waterfall in Venezuela",
        "Angels & Demons;54;thriller book written by Dan Brown"
       ]

     URL:
      http://<host>:<port>/search.html?q=eyjaffjala
     RESPONSE:
      %QUERY%:
        eyjaffjala
      %RESULT%:
       ["Eyjafjallajökull;82;glacier and volcano in Iceland",
        "Eyjafjallajökull;7;2013 film by Alexandre Coffre"
       ]

     URL:
      http://<host>:<port>/search.html?q=The+hitschheiker+guide
     RESPONSE:
      %QUERY%:
       The hitschheiker guide
      %RESULT%:
       ["The Hitchhiker's Guide to the Galaxy;41;1979 book by Douglas Adams",
        "The Hitchhiker's Guide to the Galaxy pentalogy;38;1979-1992 series\
                of five books by Douglas Adams",
        "The Hitchhiker's Guide to the Galaxy;32;2005 British-American comic\
                science fiction film",
        "The Hitchhiker's Guide to the Galaxy;8;BBC television series",
        "The Hitchhiker's Guide to the Galaxy;7;interactive fiction video game"
       ]
    """

    def __init__(self, port):
        """ Initialize with given port. """
        self.port = port
        self.max_num_byte = 1024

    def qgram_build_from_file(self, file_name, q = 3, use_syns = False):
        """ build qgram index from file.

        >>> ss = SearchServer(8080)
        >>> ss.qgram_build_from_file("test.tsv")
        >>> sorted(ss.qg.idx.items())
        ... # doctest: +NORMALIZE_WHITESPACE
        [('$$b', [(2, 1)]), ('$$f', [(1, 1)]), ('$br', [(2, 1)]),
         ('$fr', [(1, 1)]), ('bre', [(2, 1)]), ('fre', [(1, 1)]),
         ('rei', [(1, 1), (2, 1)])]
        """   

        self.qg = QGramIndex(q, use_syns)    
        self.qg.build_from_file(file_name)

    def handle_query(self, query):
        """ compute query
        
        >>> ss = SearchServer(8080)
        >>> ss.qgram_build_from_file("test.tsv")
        >>> ss.handle_query("frei")
        ... # doctest: +NORMALIZE_WHITESPACE
        b"<p><b>frei</b> score=3, ped=0, via 'frei': a word</p>
         <p><b>brei</b> score=2, ped=1, via 'brei': another word</p>"
        """
        res = self.qg.normalize(query)
        res = self.qg.find_matches(res, int(len(res) / 4))
       
        # top 5 results
        res_top = ""
        for ent in self.qg.rank_matches(res)[:5]:
            res_top += "<p>" + ("<b>%s</b> score=%s, ped=%s, via '%s': %s" % (
                self.qg.entities[ent[0] - 1][0], ent[2], ent[1], self.qg.names[ent[3] - 1],
                self.qg.entities[ent[0] - 1][2][:-1])) + "</p>" 

#        print(res_top.encode("utf-8"))
        return res_top.encode("utf-8")

    def handle_http(self, code, content = "", c_type = "text/html"):
        """ creat header for html text messages. 
        
        >>> TODO
        """

        # code and msg
        if code == 200:
           code_msg = "OK" 
        if code == 403:
            code_msg = "Forbidden"
        if code == 404:
            code_msg = "Not Found"
        if code == 418:
            code_msg = "I'm a teapot"

        if code >= 400:
            content = code_msg.encode("utf-8")

        header = "HTTP/1.1 %d %s\r\n" \
            "Content-Length: %d\r\n" \
            "Content-Type: %s\r\n" \
            "\r\n" \
            % (code, code_msg, len(content), c_type)
        
        return header.encode("utf-8") + content


    def run(self):
        """ Run the server loop: create a socket, and then, in an infinite loop,
        wait for requsts and do something with them. """ 

        # Create server socket using IPv4 addresses and TCP.
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow reuse of port if we start program again after a crash.
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Say on which machine and port we want to listen for connections.
        server_address = ("0.0.0.0", self.port)
        server_socket.bind(server_address)
        # Start listening
        server_socket.listen()

        while True:
            # wait for connections
            print("waiting for connection...")
            sys.stdout.flush()
            con, client = server_socket.accept()
            
            # read request
            requ_b = con.recv(self.max_num_byte)
            requ = requ_b.decode("utf-8")  
            
            if requ.startswith("GET "):
                # parse request
                #expected input: GET /search.html[?q=<qury>] HTTP/1.1
                requ_query = requ[5:].split(" HTTP/1.1\r\n", 1)[0].split("?q=",1)
                    
                if requ_query[0].find("/") > 0:
                    # Permission denied
                   
                    # send response and colse connection
                    con.sendall(self.handle_http(403))
                    con.close()
                    continue

                try:
                    # response with file content
                    with open(requ_query[0], "rb") as f:
                        resp = f.read() 
                except:
                    con.sendall(self.handle_http(404))
                    con.close()
                    continue


                if len(requ_query) > 1:
                    # handle query
                    res = self.handle_query(requ_query[1])
                    print(resp)
                    resp = resp.replace(b"%query%",
                    requ_query[1].encode("utf-8"))
                    resp = resp.replace(b"%result%", res)
                else:
                    # nothing to handle
                    resp = resp.replace(b"%query%", b"")
                    resp = resp.replace(b"%result%", b"")


                # content type
                if requ_query[0].endswith(".css"):
                    c_type = "text/css"
                elif requ_query[0].endswith(".html"):
                    c_type = "text/html" 
                    
                # send resp            
                con.sendall(self.handle_http(200, resp, c_type))
                con.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 %s <file> <port> [--use-synonyms]" % sys.argv[0])
        sys.exit(1)
    
    use_syns = len(sys.argv) > 3
    port = int(sys.argv[2])
    server = SearchServer(port)

    server.qgram_build_from_file(sys.argv[1], 3, use_syns)

    server.run()
