import DomainInfo as DI
import pandas as PD
import csv

DEFAULT_URLS_FILE = "C:\\Users\\Tomeriq\\Documents\\Visual Code\\Python\\ProjectDNS\\dns\\URLs.csv"

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

if __name__ == '__main__':
    url_list = getURLsFromCSV()
    for url_data in url_list.values:
        getDataForURL(url_data)
    
    storeInCSV('results_servers.csv', DI.name_to_server_info_dict, ['Server Name', 'Server Information'])
    storeInCSV('results_records.csv', DI.DNS_dict, ['(Server Name, Domain)', 'Servers known in domain'])

