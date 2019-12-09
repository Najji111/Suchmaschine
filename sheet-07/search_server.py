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
        except:
          raise
        finally:
          conn.close()
    finally:
      print("Closing socket...")
        sock.close()
  
  def handle_search(self, query):
      """# handle searches
      content = content.decode()
      with open("resources/entity.pattern.html", "r") as patf:
        pattern = patf.read()

      query = self.qi.normalize(params.get("q", ""))

      start = time.monotonic()

      # Process the keywords.
      delta = int(len(query) / 4)

      postings = self.qi.find_matches(query, delta)

      html = ""
      for p in q.rank_matches(postings)[:5]:
        html += pattern
        html = html.replace("%ENTITY_NAME%", (q.entities[p[0] - 1][0]))
        html = html.replace("%ENTITY_SYNONYM%", (q.names[p[3] - 1]))
        html = html.replace("%ENTITY_SCORE%", (str(p[2])))
        html = html.replace("%ENTITY_PED%", (str(p[1])))
        html = html.replace("%ENTITY_DESC%", (q.entities[p[0] - 1][2]))
        html = html.replace("%ENTITY_IMG%", (q.entities[p[0] - 1][6]))
        html = html.replace("%ENTITY_WIKIDATA_URL%",
                  ("https://www.wikidata.org/wiki/%s"
                   % q.entities[p[0] - 1][4]))
        html = html.replace("%ENTITY_WIKIPEDIA_URL%",
                  (q.entities[p[0] - 1][3]))

      content = content.replace(
        "%RESULT_HEADER%",
        "Got %i result(s), merged %i lists with %i elements"
        "(%i ms), %i ped calculations (%i ms), took %i ms total."
        % (len(postings), q.merges[0], q.merges[1], q.merge_time,
          q.ped_calcs[0], q.ped_time,
          (time.monotonic() - start) * 1000))
      content = content.replace("%QUERY%", query)
      content = content.replace("%RESULT%", html)

      # back to bytearray
      content = bytearray(content, "utf-8")
    """
    
    
  def handle_request(self, con, req):
     print("Handling request: %s" % req.decode("utf-8"))
    
    # we only support GET
    meth = req.split(b" ")[0].decode("utf-8")
    if meth != "GET":
        con.sendall(b'HTTP/1.1 405 Not Allowed\r\n'
            b'Content-length: 12\r\n\r\nNot Allowed!')
      return

    path = req.split(b" ")[1].decode("utf-8")
    s = path.split("/api?")
    path = s[0]

    params = {}
    if len(s) > 1:
      params = dict([tuple(a.split("=")) for a in s[1].split("&")])

    # ensure path is relative to CWD/resources/
    filep = Path(__file__).parent.absolute() / Path("./resources/" + path)

    print(path)
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
    t = bytearray(mimetypes.guess_type(str(filep.resolve()))[0], "utf-8")

    # return headers
    data = bytearray('HTTP/1.1 200 OK\r\nContent-type: %s\r\n' % t,
             "utf-8")

    # read request file as bytearray
    with filep.open("rb") as reqf:
      content = reqf.read()

    if filep.name == "search.html":
         
      """# handle searches
      content = content.decode()
      with open("resources/entity.pattern.html", "r") as patf:
        pattern = patf.read()

      query = self.qi.normalize(params.get("q", ""))

      start = time.monotonic()

      # Process the keywords.
      delta = int(len(query) / 4)

      postings = self.qi.find_matches(query, delta)

      html = ""
      for p in q.rank_matches(postings)[:5]:
        html += pattern
        html = html.replace("%ENTITY_NAME%", (q.entities[p[0] - 1][0]))
        html = html.replace("%ENTITY_SYNONYM%", (q.names[p[3] - 1]))
        html = html.replace("%ENTITY_SCORE%", (str(p[2])))
        html = html.replace("%ENTITY_PED%", (str(p[1])))
        html = html.replace("%ENTITY_DESC%", (q.entities[p[0] - 1][2]))
        html = html.replace("%ENTITY_IMG%", (q.entities[p[0] - 1][6]))
        html = html.replace("%ENTITY_WIKIDATA_URL%",
                  ("https://www.wikidata.org/wiki/%s"
                   % q.entities[p[0] - 1][4]))
        html = html.replace("%ENTITY_WIKIPEDIA_URL%",
                  (q.entities[p[0] - 1][3]))

      content = content.replace(
        "%RESULT_HEADER%",
        "Got %i result(s), merged %i lists with %i elements"
        "(%i ms), %i ped calculations (%i ms), took %i ms total."
        % (len(postings), q.merges[0], q.merges[1], q.merge_time,
          q.ped_calcs[0], q.ped_time,
          (time.monotonic() - start) * 1000))
      content = content.replace("%QUERY%", query)
      content = content.replace("%RESULT%", html)

      # back to bytearray
      content = bytearray(content, "utf-8")
    """
      content =   

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
