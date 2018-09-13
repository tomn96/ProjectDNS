import MissconfigurationInfo as MI
import pandas as PD

def temp(servers_to_check, designated_domain):
    servers = set(servers_to_check)
    children_servers = set()
    
    for server in servers:
        answer = get_NS_for_domain(server, domain)
        if answer is not None:
            DNS_dict[(server, domain)] = answer
            for new_server in answer:
                children_servers.add(new_server) # TODO: not add - if exists in set then just update
    
    for child_server in children_servers:
        answer = get_NS_for_domain(child_server, domain)
        if answer is not None:
            DNS_dict[(child_server, domain)] = answer
    
    return children_servers

def temp2(url_data):
    obj = MI.MisconfigurationInfo(url_data[GET_URL])
    domains = obj.get_domains()
    servers = MI.root_servers   # FIXME: deep copy
    for i in range(len(domains)-1):
        servers = temp(servers, domains[i])

def main():
    url_list = getURLsFromCSV()
    for url_data in url_list.values:
        temp2(url_data)


if __name__ == '__main__':
    # main()
