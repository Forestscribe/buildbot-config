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
    overrides = {}
    for var in ['MARATHON_APP_ID','MESOS_TASK_ID','HOST','MARATHON_APP_VERSION','MARATHON_APP_DOCKER_IMAGE']:
        overrides[var] = os.environ.get(var, 'unset')
    host, port = url.netloc.split(":")
    protocol = None
    if url.scheme == "udp":
        protocol = udp.UDPGelfProtocol
    elif url.scheme == "tcp":
        protocol = tcp.TCPGelfProtocol
    else:
        print("invalid GELF_URL, using stdout logging")
    if protocol is not None:
        observer = GraylogObserver(protocol, host, int(port))
        protocol.parameter_override = overrides

application.setComponent(ILogObserver, observer.emit)
m = BuildMaster(basedir, configfile, umask=None)
m.setServiceParent(application)
