import dns
import dns.name
import dns.query
import dns.resolver
import DomainInfo as DI

HOST_NAME = "SERVER_NAME"
NAME_SERVER = "NS"
HOST_ADDRESS = "A"
HOST6_ADDRESS = "AAAA"
TEXT_ENTRY = "TXT"
MAIL_EXCHANGER = "MX"
MISCONFIG = "MISCONFIG"

RESOLVER_ORIGIN = True


class MisconfigurationInfo:

    def __init__(self, domain):
        self.__domain = domain
        self.__domains = list()
        self.__default_server = dns.resolver.get_default_resolver()
        self.initDomains()

    def initDomains(self):
        subDomains = self.__domain.split('.')
        for i in range(len(subDomains), 0, -1):
            sub = '.'.join(subDomains[i - 1:])
            domainInfo = DI.DomainInfo(sub, self.__default_server)
            self.__domains.append(domainInfo)
