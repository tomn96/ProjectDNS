import MissconfigurationInfo as MI
import pandas as PD
import csv

DEFAULT_URLS_FILE = "C:\\Users\\Tomeriq\\Documents\\Visual Code\\Python\\ProjectDNS\\dns\\URLs.csv"

GET_URL = 0

def getURLsFromCSV():
    raw_data = PD.read_csv(DEFAULT_URLS_FILE, names=['URL'])
    return raw_data

def temp(servers_to_check, designated_domain):
    servers = set(servers_to_check)
    children_servers = set()

    for server in servers:
        answer = MI.get_NS_for_domain(server, designated_domain)
        if answer is not None:
            if (server, designated_domain) not in MI.DNS_dict:
                MI.DNS_dict[(server, designated_domain)] = answer
            for new_server in answer:
                # TODO: not add - if exists in set then just update
                children_servers.add(new_server)

    for child_server in children_servers:
        answer = MI.get_NS_for_domain(child_server, designated_domain)
        if answer is not None:
            MI.DNS_dict[(child_server, designated_domain)] = answer

    return children_servers


def temp2(url_data):
    obj = MI.MisconfigurationInfo(url_data[GET_URL])
    domains = obj.get_domains()
    servers = MI.root_servers   # FIXME: deep copy
    for i in range(len(domains)-1):
        servers = temp(servers, domains[i])

if __name__ == '__main__':
    url_list = getURLsFromCSV()
    for url_data in url_list.values:
        temp2(url_data)

    with open('results_servers.csv', 'w') as f:
        fieldnames = ['Application Name', 'Application ID']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        data = [dict(zip(fieldnames, [k, v])) for k, v in MI.name_to_server_info_dict.items()]
        writer.writerows(data)

    with open('results_records.csv', 'w') as f:
        fieldnames = ['Application Name', 'Application ID']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        data = [dict(zip(fieldnames, [k, v])) for k, v in MI.DNS_dict.items()]
        writer.writerows(data)
    

    # url_list = getURLsFromCSV()
    # misconfigurations_for_urls = list()
    # for url_data in url_list.values:
    #     misconfigurations_for_urls.append(
    #         MI.MisconfigurationInfo(url_data[GET_URL]))
    # misconfigurations_for_urls[0].get_domain_info("co.il")
    # misconfigurations_for_urls[0].find_misconfigurations()
        # print(url.find_misconfigurations(...))
