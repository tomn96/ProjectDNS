import DomainInfo as DI
import pandas as PD
import csv

DEFAULT_URLS_FILE = "URLs.csv"

misconfiguration_dict = dict()
misconfiguration_count_dict = dict()

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

def getURLsFromCSV():
    """
    reads a csv file using Pandas library
    :returns: {pandas data list} the raw data read from the given csv file
    """
    raw_data = PD.read_csv(DEFAULT_URLS_FILE, names=['URL'])
    return raw_data

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



def check_misconfig():
    record_num = 0
    for keyA,valueA in DI.DNS_dict.items():
        record_num += 1
        if (record_num % 100 == 0):
            print("record #" + str(record_num))
        host_A, domain_A = keyA
        if domain_A not in misconfiguration_count_dict:
            misconfiguration_count_dict[domain_A] = 0
        servers_known_to_A = set(valueA)
        for keyB, valueB in DI.DNS_dict.items():
            host_B, domain_B = keyB
            servers_known_to_B = set(valueB)
            if (host_A != host_B and domain_A == domain_B):
                foreign_to_B = servers_known_to_A - servers_known_to_B
                foreign_to_A = servers_known_to_B - servers_known_to_A
                if (len(foreign_to_A) > 0 or len(foreign_to_B) > 0):
                    misconfiguration_dict[(host_A, host_B, domain_A)] = \
                        MisconfigurationInfo(host_A, host_B, foreign_to_A, foreign_to_B, domain_A)
                    misconfiguration_count_dict[domain_A] += 1

if __name__ == '__main__':
    url_list = getURLsFromCSV()
    for url_data in url_list.values:
        getDataForURL(url_data)
    check_misconfig()

    
    storeInCSV('results_servers.csv', DI.name_to_server_info_dict, ['Server Name', 'Server Information'])
    storeInCSV('results_records.csv', DI.DNS_dict, ['(Server Name, Domain)', 'Servers known in domain'])
    storeInCSV("misconfigurations.csv", misconfiguration_dict, ["server1, server2, domain", "misconfiguration info"])
    storeInCSV("misconfigurations_count.csv", misconfiguration_count_dict, ["domain", "num of misconfigurations"])

