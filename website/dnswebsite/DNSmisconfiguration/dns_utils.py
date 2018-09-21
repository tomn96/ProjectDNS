from . import DomainInfo as DI
from . import ServerInfo as SI
from .models import Server, AddressIPv4, AddressIPv6, KnownNameServer
import csv


class MisconfigurationResult:

    def __init__(self):
        self.misconfiguration_dict = dict()
        self.misconfiguration_count_dict = dict()


class MisconfigurationInfo:

    def __init__(self, server1, server2, foreign_to_server_1, foreign_to_server_2, domain):
        self.__foreign_to_server_1 = foreign_to_server_1
        self.__foreign_to_server_2 = foreign_to_server_2
        self.__domain = domain
        self.__server1 = server1
        self.__server2 = server2

    def __str__(self):
        s = "Misconfiguration information\n"
        s += "Domain: " + str(self.__domain) + "\n"
        s += "Host1: " + str(self.__server1) + "\n"
        s += "Host2: " + str(self.__server2) + "\n"
        f1 = "" if len(self.__foreign_to_server_1) == 0 else str(self.__foreign_to_server_1)
        f2 = "" if len(self.__foreign_to_server_2) == 0 else str(self.__foreign_to_server_2)
        s += "NS known to host1 and not known to host2: " + f2 + "\n"
        s += "NS known to host2 and not known to host1: " + f1 + "\n"
        return s


GET_URL = 0


def getURLsFromCSV(file):
    """
    reads a csv file
    :returns: {generator} the raw data read from the given csv file
    """
    utf8 = (line.decode('utf-8') for line in file)
    file_reader = csv.reader(utf8)
    return file_reader


def getDNSData(servers_to_check, designated_domain, dns_worker):
    """
    stores information related to DNS protocol in static dictionaries
    :param servers_to_check: {list} servers to get information from
    :param designated_domain: {string} the domain for which the servers are queried
    """
    servers = set(servers_to_check)
    children_servers = set()

    for server in servers:
        answer = dns_worker.get_NS_for_domain(server, designated_domain)
        if answer is not None:
            if (server, designated_domain) not in dns_worker.DNS_dict:
                dns_worker.DNS_dict[(server, designated_domain)] = answer
            for new_server in answer:
                children_servers.add(new_server)

    for child_server in children_servers:
        answer = dns_worker.get_NS_for_domain(child_server, designated_domain)
        if answer is not None:
            dns_worker.DNS_dict[(child_server, designated_domain)] = answer

    return children_servers


def getDataForURL(url_data, dns_worker):
    """
    starts collecting infomation about the domains related to the given URL
    :param url_data: {list} stores information related to the URL
    """
    obj = DI.DomainInfo(url_data[GET_URL])
    domains = obj.get_domains()
    servers = dns_worker.root_servers
    for i in range(len(domains)-1):
        servers = getDNSData(servers, domains[i], dns_worker)


def storeInCSV(file_name, dict_to_store, field_names):
    """
    stores a dictionary in a CSV format file
    :param file_name: {string} the file's name (must end with .csv)
    :dict_to_store: {dict} a dictionary to store in a CSV file
    :field_names: {list} a list of the dictionary's attributes/fields names
    """
    with open(file_name, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        data = [dict(zip(field_names, [k, v])) for k, v in dict_to_store.items()]
        writer.writerows(data)

def storeInServer(dns_worker):
    for k, v in dns_worker.name_to_server_info_dict.items():
        server = Server.objects.create(host_name=v[SI.HOST_NAME], description=v[SI.DESCRIPTION], original_domain=v[SI.DOMAIN])
        for ipv4address in v[SI.HOST_ADDRESS]:
            server.addressipv4_set.create(ip_address=ipv4address)
        for ipv6address in v[SI.HOST6_ADDRESS]:
            server.addressipv6_set.create(ip_address=ipv6address)


def storeInKnownNameServer(dns_worker):
    for k, v in dns_worker.DNS_dict.items():
        s = Server.objects.get(host_name=k[0])
        for known_server in v:
            KnownNameServer.objects.create(server=s, domain=k[1], known_server=known_server)


def check_misconfig(dns_worker, misconfiguration_result):
    record_num = 0
    for keyA,valueA in dns_worker.DNS_dict.items():
        record_num += 1
        if record_num % 100 == 0:
            print("record #" + str(record_num))
        host_A, domain_A = keyA
        if domain_A not in misconfiguration_result.misconfiguration_count_dict:
            misconfiguration_result.misconfiguration_count_dict[domain_A] = 0
        servers_known_to_A = set(valueA)
        for keyB, valueB in dns_worker.DNS_dict.items():
            host_B, domain_B = keyB
            servers_known_to_B = set(valueB)
            if host_A != host_B and domain_A == domain_B:
                foreign_to_B = servers_known_to_A - servers_known_to_B
                foreign_to_A = servers_known_to_B - servers_known_to_A
                if len(foreign_to_A) > 0 or len(foreign_to_B) > 0:
                    misconfiguration_result.misconfiguration_dict[(host_A, host_B, domain_A)] = \
                        MisconfigurationInfo(host_A, host_B, foreign_to_A, foreign_to_B, domain_A)
                    misconfiguration_result.misconfiguration_count_dict[domain_A] += 1


def main_url(url):
    dns_worker = DI.DNSWorker()

    getDataForURL([url], dns_worker)

    storeInServer(dns_worker)
    storeInKnownNameServer(dns_worker)


def main_csv(file):

    dns_worker = DI.DNSWorker()
    misconfiguration_result = MisconfigurationResult()

    url_list_generator = getURLsFromCSV(file)
    for url_data in url_list_generator:
        getDataForURL(url_data, dns_worker)

    check_misconfig(dns_worker, misconfiguration_result)

    storeInServer(dns_worker)
    storeInKnownNameServer(dns_worker)

    storeInCSV('results_servers.csv', dns_worker.name_to_server_info_dict, ['Server Name', 'Server Information'])
    storeInCSV('results_records.csv', dns_worker.DNS_dict, ['(Server Name, Domain)', 'Servers known in domain'])
    storeInCSV("misconfigurations.csv", misconfiguration_result.misconfiguration_dict, ["server1, server2, domain", "misconfiguration info"])
    storeInCSV("misconfigurations_count.csv", misconfiguration_result.misconfiguration_count_dict, ["domain", "num of misconfigurations"])

