import os, sys, time
from thrift.transport import THttpClient
from thrift.protocol import TCompactProtocol

from ..Gen import LineService
from ..Gen.ttypes import *

class Poll:

  client = None

  auth_query_path = "/api/v4/TalkService.do";
  http_query_path = "/S4";
  polling_path = "/P4";
  host = "gd2.line.naver.jp";
  port = 443;

  UA = "Line/6.0.0 iPad4,1 9.0.2"
  LA = "IOSIPAD 6.0.0 iPhone OS 9.0.2"

  rev = 0

  def __init__(self, authToken):
    self.transport = THttpClient.THttpClient(self.host, self.port, self.http_query_path)
    self.transport.setCustomHeaders({
      "User-Agent" : self.UA,
      "X-Line-Application" : self.LA,
      "X-Line-Access": authToken
    });
    self.protocol = TCompactProtocol.TCompactProtocol(self.transport);
    self.client = LineService.Client(self.protocol)
    self.rev = self.client.getLastOpRevision()
    self.transport.path = self.polling_path
    self.transport.open()

  def stream(self, sleep=50000):
    #usleep = lambda x: time.sleep(x/1000000.0)
    while True:
      try:
        Ops = self.client.fetchOps(self.rev, 5)
      except EOFError:
        raise Exception("It might be wrong revision\n" + str(self.rev))

      for Op in Ops:
          # print Op.type
        if (Op.type != OpType.END_OF_OPERATION):
          self.rev = max(self.rev, Op.revision)
          return Op

      #usleep(sleep)
