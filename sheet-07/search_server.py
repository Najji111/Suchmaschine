"""
Copyright 2019, University of Freiburg
Chair of Algorithms and Data Structures.
Hannah Bast <bast@cs.uni-freiburg.de>
Patrick Brosi <brosi@cs.uni-freiburg.de>
"""

import readline  # NOQA
import socket
import sys
import time
import mimetypes
import qgram_index
from pathlib import Path
from urllib.parse import unquote


class SearchServer:
    """
    A HTTP search server using a q gram index.
    """
    def __init__(self, port, qi):
        '''
        Inits a simple HTTP search server
        '''

        self.port = port
        self.qi = qi

    def run(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            server_address = ('0.0.0.0', self.port)
            sock.bind(server_address)
            sock.listen(1)

            while True:
                print("Waiting on port %i" % port)
                conn, client_address = sock.accept()
                # connection timeout 5 seconds
                conn.settimeout(5.0)
                try:
                    print("Client connected from %s" % client_address[0])

                    data = bytearray()
                    while True:
                        batch = conn.recv(32)

                        if batch:
                            data.extend(batch)
                            if data.find(b'\r\n\r\n') > -1:
                                break
                        else:
                            break

                    self.handle_request(conn, data[0:data.find(b'\r\n')])
                except socket.timeout:
                    print("(Timeout from %s)" % client_address[0])
                    pass
                finally:
                    conn.close()
        finally:
            print("Closing socket...")
            sock.close()

    def url_decode(self, str):
        '''
        Decode an URL-encoded UTF-8 string, as explained in the lecture.
        Don't forget to also decode a "+" (plus sign) to a space (" ")!

        >>> s = SearchServer(0, None)
        >>> s.url_decode("nirwana")
        'nirwana'
        >>> s.url_decode("the+m%C3%A4trix")
        'the mätrix'
        >>> s.url_decode("Mikr%C3%B6soft+Windos")
        'Mikrösoft Windos'
        >>> s.url_decode("The+hitschheiker%20guide")
        'The hitschheiker guide'
        '''
        res = unquote(str).replace("+", " ")
        return res

    def handle_search(self, filep, query):
        """ Searches for the query and returns a the result as a json.

        >>> q = qgram_index.QGramIndex(3, False)
        >>> q.build_from_file("wiki-test.tsv")
        >>> filep = Path(__file__).parent.absolute() / Path("./api")
        >>> ss = SearchServer(8081, q)
        >>> ss.handle_search(filep, "germany")
        ... # doctest: +NORMALIZE_WHITESPACE
        bytearray(b'{ "QUERY": "germany", "ENTITYS": [ { "ENTITY_NAME":
        "Germany", "ENTITY_SYNONYM": "Germany", "ENTITY_SCORE": "347",
        "ENTITY_PED": "0", "ENTITY_DESC": "country in central Europe",
        "ENTITY_IMG": "http//...", "ENTITY_WIKIDATA_URL":
        "https://www.wikidata.org/wiki/Q183", "ENTITY_WIKIPEDIA_URL":
        "https://..." }, { "ENTITY_NAME": "germania", "ENTITY_SYNONYM":
        "germania", "ENTITY_SCORE": "346", "ENTITY_PED": "1", "ENTITY_DESC":
        "country", "ENTITY_IMG": "http://...", "ENTITY_WIKIDATA_URL":
        "https://www.wikidata.org/wiki/Q142", "ENTITY_WIKIPEDIA_URL":
        "https://..." } ] }')
"""

        if filep.name != "api":
            # read request file as bytearray
            with filep.open("rb") as reqf:
                content = reqf.read()
        else:
            # handle searches

            # Process the keywords.
            delta = int(len(query) / 4)

            postings = self.qi.find_matches(query, delta)
            json = ""
            for p in self.qi.rank_matches(postings)[:5]:
                if json != "":
                    json += ","
                else:
                    json += "{ \"QUERY\": \"" + query
                    json += "\", \"ENTITYS\": ["

                json += " { \"ENTITY_NAME\": \"" + \
                    self.qi.entities[p[0] - 1][0]
                json += "\", \"ENTITY_SYNONYM\": \"" + self.qi.names[p[3] - 1]
                json += "\", \"ENTITY_SCORE\": \"" + str(p[2])
                json += "\", \"ENTITY_PED\": \"" + str(p[1])
                json += "\", \"ENTITY_DESC\": \"" + \
                    self.qi.entities[p[0] - 1][2]
                json += "\", \"ENTITY_IMG\": \"" + \
                    self.qi.entities[p[0] - 1][6][:-1]
                json += "\", \"ENTITY_WIKIDATA_URL\": \"" + \
                    ("https://www.wikidata.org/wiki/%s" %
                        self.qi.entities[p[0] - 1][4])
                json += "\", \"ENTITY_WIKIPEDIA_URL\": \"" + \
                    self.qi.entities[p[0] - 1][3]
                json += "\" }"
            json += " ] }"

            # prevent xss
            # regex = re.compile("<script>.*<script/>")
            # result = re.findall(regex, json)

            # back to bytearray
            content = bytearray(json, "utf-8")
        return content

    def handle_request(self, con, req):
        print("Handling request: %s" % req.decode("utf-8"))

        # we only support GET
        meth = req.split(b" ")[0].decode("utf-8")
        if meth != "GET":
            con.sendall(b'HTTP/1.1 405 Not Allowed\r\n'
                        b'Content-length: 12\r\n\r\nNot Allowed!')
            return

        path = req.split(b" ")[1].decode("utf-8")
        s = path.split("?")
        path = s[0]

        params = {}
        if len(s) > 1:
            params = dict([tuple(a.split("=")) for a in s[1].split("&")])

        # ensure path is relative to CWD/resources/
        filep = Path(__file__).parent.absolute() / Path("./resources/" + path)

        if filep.name != "api":
            # return 404 if file does not exist
            if not filep.exists():
                con.sendall(b'HTTP/1.1 404 Not found\r\n'
                            b'Content-length: 10\r\n\r\nNot found!')
                return

            # return 403 for dir requests
            if not filep.is_file():
                con.sendall(b'HTTP/1.1 403 Forbidden\r\n'
                            b'Content-length: 12\r\n\r\nNot allowed!')
                return

            # guess MIME type
            t = bytearray(mimetypes.guess_type(str(filep.resolve()))[0],
                          "utf-8")
            query = ""
        else:
            query = self.url_decode(params.get("q", ""))
            query = self.qi.normalize(query)
            # it is a query request
            t = "application/json"

        # return headers
        data = bytearray('HTTP/1.1 200 OK\r\nContent-type: %s\r\n' % t,
                         "utf-8")

        content = self.handle_search(filep, query)

        # we finally now the content length
        data.extend(b'Content-length: %i\r\n\r\n' % len(content))
        data.extend(content)
        # send answer
        con.sendall(data)


if __name__ == "__main__":
    # Parse the command line arguments.
    if len(sys.argv) < 3:
        print("Usage: python3 %s <file> <port> [--use-synonyms]" % sys.argv[0])
        sys.exit()

    file_name = sys.argv[1]
    port = int(sys.argv[2])

    use_synonyms = "--use-synonyms" in sys.argv

    print("Reading from file '%s'." % file_name)
    start = time.monotonic()
    q = qgram_index.QGramIndex(3, use_synonyms)
    q.build_from_file(file_name)
    print("Done, took %i ms." % ((time.monotonic() - start) * 1000))

    s = SearchServer(port, q)
    print("Starting server, go to http://localhost:%i/search.html ..." % port)
    s.run()
