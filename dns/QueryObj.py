import dns
import dns.name
import dns.query
import dns.resolver

NAME_SERVER = "NS"
HOST_ADDRESS = "A"
HOST6_ADDRESS = "AAAA"
TEXT_ENTRY = "TXT"
MAIL_EXCHANGER = "MX"
SONS = "SONS"

RESOLVER_ORIGIN = True

class QueryObj:

    def __init__(self, domain):
        self.__domain = domain
        self.__origin = not RESOLVER_ORIGIN
        self.__host = None
        self.__name_servers = list()
        self.__ipv4_addresses = list()
        self.__ipv6_addresses = list()
        self.__mail_exchanger = None
        self.__text_entry = None

    def fillWithResolver(self):
        try:
            self.__origin = RESOLVER_ORIGIN
            self.__host = host
            self.__resolver = dns.resolver.Resolver()
            self.__name_servers = self.perform_query(NAME_SERVER)
            self.__ipv4_addresses = self.perform_query(HOST_ADDRESS)
            self.__mail_exchanger = self.perform_query(MAIL_EXCHANGER)
            self.__text_entry = self.perform_query(TEXT_ENTRY)
            self.__sons = self.get_sub_queries()
        except dns.resolver.NXDOMAIN:
            print("No such Domain")
        except dns.resolver.Timeout:
            print("Request timeout")
        except dns.exception.DNSException:
            print("Unhandled DNS exception")
        try:
            self.__ipv6_addresses = self.perform_query(HOST6_ADDRESS)
        except Exception:
            self.__ipv6_addresses = None

    def getNSByIP(self):
        myAnswers = list()
        response = None
        resolver = dns.resolver.Resolver()
        for address in self.__ipv4_addresses:
            resolver.nameservers.append(address)
            req = '.'.join(reversed(str(address).split("."))) + ".in-addr.arpa"

            # checks if the name received by the A response is different from PTR query response
            myAnswers.append(resolver.query(req, "PTR"))
            answerNS = myAnswers[0].response.answer[0].items[0].target
            if answerNS != self.__host:
                print("names are different")

            # queries the current name server for the name servers for this domain
            query = dns.message.make_query(self.__domain, dns.rdatatype.NS)
            response = dns.query.udp(query, str(address))

        self.__name_servers.extend(response.additional)

        print()


    def addRRData(self, rr):
        if rr.rdtype == dns.rdatatype.NS:
            self.__host = rr.target
            resolver = dns.resolver.get_default_resolver()
            for ip in resolver.query(rr.target).rrset:
                self.__ipv4_addresses.append(ip)

        else:
            if self.__host is None:
                self.__host = rr.name
        if rr.rdtype == dns.rdatatype.A:
            self.__ipv4_addresses.extend(rr.items)

        if rr.rdtype == dns.rdatatype.AAAA:
            self.__ipv6_addresses.extend(rr.items)

        # if rr.rdtype == dns.rdatatype.AAAA or rr.rdtype == dns.rdatatype.A:
        self.getNSByIP()


    def perform_query(self, type):
        try:
            query = self.__resolver.query(self.__domain, type)
        except dns.resolver.NXDOMAIN:
            print("No such Domain")
        except dns.resolver.Timeout:
            print("Request timeout")
        except dns.exception.DNSException:
            print("Unhandled DNS exception")

        return query

    def get_sub_queries(self):
        return dict

    def get_record_str(self, item):
        s = ""
        if(item):
            for rdata in item:
                s += str(rdata) +" "
        else: s+= " No information"
        s += "\n"
        return s

    def __str__(self):
        s = "DNS information\n"
        s += "Domain: " + str(self.__domain) + "\n"
        s += "IPv4 Addresses: " + self.get_record_str(self.__ipv4_addresses)
        s += "IPv6 Addresses :" + self.get_record_str(self.__ipv6_addresses)
        s += "Name Server: " + self.get_record_str(self.__name_servers)
        s += "Mail Exchanger: " + self.get_record_str(self.__mail_exchanger)
        return s

    def __getitem__(self, item):
        return {
            NAME_SERVER: self.__name_servers,
            HOST_ADDRESS: self.__ipv4_addresses,
            HOST6_ADDRESS: self.__ipv4_addresses,
            TEXT_ENTRY: self.__text_entry,
            MAIL_EXCHANGER: self.__mail_exchanger,
        }[item]

    def __repr__(self):
        return self.__str__()


    import sys

    def log(msg):
        print(msg)

