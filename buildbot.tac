import os
import sys

from twisted.application import service
from twisted.python.log import FileLogObserver, ILogObserver

from buildbot.master import BuildMaster

basedir = os.path.abspath(os.path.dirname(__file__))
configfile = 'master.cfg'

# note: this line is matched against to check that this is a buildmaster
# directory; do not edit it.
application = service.Application('buildmaster')

GELF_URL = os.environ.get("GELF_URL")
observer = FileLogObserver(sys.stdout)

if GELF_URL is not None:
    from txgraylog.protocol import udp, tcp
    from txgraylog.observer import GraylogObserver
    from future.moves.urllib.parse import urlparse
    url = urlparse(GELF_URL)
    host, port = url.netloc.split(":")
    if url.scheme == "udp":
        observer = GraylogObserver(udp.UDPGelfProtocol, host, int(port))
    elif url.scheme == "tcp":
        observer = GraylogObserver(tcp.TCPGelfProtocol, host, int(port))
    else:
        print "invalid GELF_URL, using stdout logging"

m = BuildMaster(basedir, configfile, umask=None)
m.setServiceParent(application)
