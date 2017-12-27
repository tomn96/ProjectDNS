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


class QueryObj:

    def __init__(self, host):
        self.__resolver = dns.resolver.Resolver()
        self.__host = host
        try:
            self.__name_server = self.perform_query(NAME_SERVER)
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

        try:
            self.__authorative = self.get_authoritative_nameserver()
        except Exception:
            self.__authorative = None


    def perform_query(self, type):
        try:
            query = self.__resolver.query(self.__host, type)
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
        s += "Host: " + str(self.__host) + "\n"
        s += "IPv4 Addresses: " + self.get_record_str(self.__ipv4_addresses)
        s += "IPv6 Addresses :" + self.get_record_str(self.__ipv6_addresses)
        s += "Name Server: " + self.get_record_str(self.__name_server)
        s += "Mail Exchanger: " + self.get_record_str(self.__mail_exchanger)
        return s

    def __getitem__(self, item):
        return {
            NAME_SERVER: self.__name_server,
            HOST_ADDRESS: self.__ipv4_addresses,
            HOST6_ADDRESS: self.__ipv4_addresses,
            TEXT_ENTRY: self.__text_entry,
            MAIL_EXCHANGER: self.__mail_exchanger,
            SONS: self.__sons
        }[item]

    def __repr__(self):
        return self.__str__()

    def get_authoritative_nameserver(domain, log=lambda msg: None):
        n = dns.name.from_text(domain)

        depth = 2
        default = dns.resolver.get_default_resolver()
        nameserver = default.nameservers[0]

        last = False
        while not last:
            s = n.split(depth)

            last = s[0].to_unicode() == u'@'
            sub = s[1]

            log('Looking up %s on %s' % (sub, nameserver))
            query = dns.message.make_query(sub, dns.rdatatype.NS)
            response = dns.query.udp(query, nameserver)

            rcode = response.rcode()
            if rcode != dns.rcode.NOERROR:
                if rcode == dns.rcode.NXDOMAIN:
                    raise Exception('%s does not exist.' % sub)
                else:
                    raise Exception('Error %s' % dns.rcode.to_text(rcode))

            rrset = None
            if len(response.authority) > 0:
                rrset = response.authority[0]
            else:
                rrset = response.answer[0]

            rr = rrset[0]
            if rr.rdtype == dns.rdatatype.SOA:
                log('Same server is authoritative for %s' % sub)
            else:
                authority = rr.target
                log('%s is authoritative for %s' % (authority, sub))
                nameserver = default.query(authority).rrset[0].to_text()

            depth += 1

        return nameserver

    import sys

    def log(msg):
        print(msg)

