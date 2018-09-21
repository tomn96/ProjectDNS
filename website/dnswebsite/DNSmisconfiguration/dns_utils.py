from . import DomainInfo as DI
from . import ServerInfo as SI
from .models import Server, AddressIPv4, AddressIPv6, KnownNameServer
import csv

GET_URL = 0


def getURLsFromCSV(file):
    """
    reads a csv file
    :returns: {generator} the raw data read from the given csv file
    """
    utf8 = (line.decode('utf-8') for line in file)
    file_reader = csv.reader(utf8)
    return file_reader


def getDNSData(servers_to_check, designated_domain):
    """
    stores information related to DNS protocol in static dictionaries
    :param servers_to_check: {list} servers to get information from
    :param designated_domain: {string} the domain for which the servers are queried
    """
    servers = set(servers_to_check)
    children_servers = set()

    for server in servers:
        answer = DI.get_NS_for_domain(server, designated_domain)
        if answer is not None:
            if (server, designated_domain) not in DI.DNS_dict:
                DI.DNS_dict[(server, designated_domain)] = answer
            for new_server in answer:
                children_servers.add(new_server)

    for child_server in children_servers:
        answer = DI.get_NS_for_domain(child_server, designated_domain)
        if answer is not None:
            DI.DNS_dict[(child_server, designated_domain)] = answer

    return children_servers


def getDataForURL(url_data):
    """
    starts collecting infomation about the domains related to the given URL
    :param url_data: {list} stores information related to the URL
    """
    obj = DI.DomainInfo(url_data[GET_URL])
    domains = obj.get_domains()
    servers = DI.root_servers  
    for i in range(len(domains)-1):
        servers = getDNSData(servers, domains[i])


def storeInServer():
    for k, v in DI.name_to_server_info_dict.items():
        server = Server.objects.create(host_name=v[SI.HOST_NAME], description=v[SI.DESCRIPTION], original_domain=v[SI.DOMAIN])
        for ipv4address in v[SI.HOST_ADDRESS]:
            server.addressipv4_set.create(ip_address=ipv4address)
        for ipv6address in v[SI.HOST6_ADDRESS]:
            server.addressipv6_set.create(ip_address=ipv6address)


def storeInKnownNameServer():
    for k, v in DI.DNS_dict.items():
        s = Server.objects.get(host_name=k[0])
        for known_server in v:
            KnownNameServer.objects.create(server=s, domain=k[1], known_server=known_server)


def initialize_domainInfo():
    DI.name_to_server_info_dict = dict()
    DI.root_servers = DI.build_root_servers_info_objects()
    DI.DNS_dict = dict()


def main_url(url):
    initialize_domainInfo()  # TODO - check if works

    getDataForURL([url])

    storeInServer()
    storeInKnownNameServer()


def main_csv(file):
    initialize_domainInfo()  # TODO - check if works

    url_list_generator = getURLsFromCSV(file)
    for url_data in url_list_generator:
        getDataForURL(url_data)

    storeInServer()
    storeInKnownNameServer()
