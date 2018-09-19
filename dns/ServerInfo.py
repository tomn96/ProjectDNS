import dns
import dns.name
import dns.query
import dns.resolver

HOST_NAME = "SERVER_NAME"
NAME_SERVER = "NS"
HOST_ADDRESS = "A"
HOST6_ADDRESS = "AAAA"
TEXT_ENTRY = "TXT"
DESCRIPTION = "DESC"
MAIL_EXCHANGER = "MX"

HOST_INDEX = 0
IPV4_INDEX = 1
IPV6_INDEX = 2
DESCRIPTION_INDEX = 3
DOMAIN = 4

RESOLVER_ORIGIN = True

class ServerInfo:

    def __init__(self, data):
        """
        initializes a ServerInfo from given data list
        :param data: {list} a list that stores data related to the server in the following format:
        [0] = server's host name
        [1] = server's ip4 addresses
        [2] = server's ip6 addresses
        [3] = server's description
        [4] = server's original domain
        """
        self.__ipv4_addresses = list()
        self.__ipv6_addresses = list()

        self.__domain = data[DOMAIN]
        self.__host = data[HOST_INDEX]
        self.__ipv4_addresses.extend(data[IPV4_INDEX])
        self.__ipv6_addresses.extend(data[IPV6_INDEX])
        self.__description = data[DESCRIPTION_INDEX]

    def extend_addresses_no_duplicates(self, rr):
        """
        extends the first_list with foreign elements from second_list
        :param rr: {DNS response record} the response from which information is updated
        """
        in_second = set()
        for rr_data in rr.items:
            in_second.add(rr_data.address)

        list_to_extend = self.__ipv4_addresses if rr.rdtype == dns.rdatatype.A else self.__ipv6_addresses
        new_items = in_second - set(list_to_extend)
        list_to_extend.extend(list(new_items))


    def add_rr_data(self, rr):
        """
        updates the server information with information received in the DNS response record
        :param rr: {DNS response record} the response from which information is updated
        """
        if rr.rdtype == dns.rdatatype.NS and self.__host is None:
            self.__host = rr.target

        else:
            if self.__host is None:
                self.__host = rr.name

        if rr.rdtype == dns.rdatatype.A or rr.rdtype == dns.rdatatype.AAAA:
            self.extend_addresses_no_duplicates(rr)


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
        s += "Host: " + str(self.__host) + "\n"
        s += "IPv4 Addresses: " + self.get_record_str(self.__ipv4_addresses)
        s += "IPv6 Addresses :" + self.get_record_str(self.__ipv6_addresses)
        s += "Description: " + self.__description
        # s += "Mail Exchanger: " + self.get_record_str(self.__mail_exchanger)
        return s

    def __getitem__(self, item):
        return {
            HOST_NAME: self.__host,
            HOST_ADDRESS: self.__ipv4_addresses,
            HOST6_ADDRESS: self.__ipv4_addresses,
            DESCRIPTION: self.__description,
            # TEXT_ENTRY: self.__text_entry,
            # MAIL_EXCHANGER: self.__mail_exchanger,
        }[item]

    def __repr__(self):
        return self.__str__()

    def __le__(self, other):
        return self.__host < other.__host
