import dns
import dns.name
import dns.query
import dns.resolver
import DomainInfo as DI
import ServerInfo as SI
import pandas as PD


RESOLVER_ORIGIN = True
ROOT_SERVERS_FILE_PATH = 'C:\\Users\\Tomeriq\\Documents\\Visual Code\\Python\\ProjectDNS\\dns\\IANA Root Servers.csv'


def get_master_root_servers():
    """
    reads the addresses of the 13 IANA root servers 
    (see https://www.iana.org/domains/root/servers)
        :returns: {array} the raw data read from csv file
    """
    raw_data = PD.read_csv(ROOT_SERVERS_FILE_PATH, names=[
        'Server Name', 'IPv4 Address', 'IPv6 Address', 'Owner Description'])
    return raw_data


def build_root_servers_info_objects(servers_info_file_path):
    """
    builds ServerInfo objects for each root server
        :param servers_info: {list} the servers data paramaeters
        :returns: {list} list of ServerInfo objects for each root server
    """
    servers_info = get_master_root_servers()
    servers = list()
    for server_csv_data in servers_info.values:
        server_data = list()
        for i in range(len(server_csv_data)):
            server_data.append(server_csv_data[i])
        server_data.append("Root Domain")
        servers.append(SI.ServerInfo(server_data))
    return servers

@staticmethod
def build_foreign_list(lst1, lst2):
    """
    create as list composed of elements found in the 
    first list and not found in the second list
        :param lst1: {list} first list
        :param lst2: {list} second list
    """
    result = list()
    for element in lst1:
        i = 0
        while i < (len(lst2)):
            if element == lst2[i]:
                break
            i += 1
        if i == len(lst2):
            result.append(element)
    return result

@staticmethod
def add_server_data_from_query_response(server_info, response):
        """
        adds data from a given dns response to server_info list
            :param server_info: {list} a list of server's data paramaters
            :param response: {DNS.response} a dns response for a 'udp' query
        """
        ip_type = None

        # checks if IPv4 or IPv6
        if response.rdtype == dns.rdatatype.A:
            ip_type = SI.IPV4_INDEX
        elif response.rdtype == dns.rdatatype.AAAA:
            ip_type = SI.IPV6_INDEX

        # adds all addresses listed for the server
        for ip in response.items:
            server_info[ip_type].append(ip.address)

        return server_info

@staticmethod
def create_new_server_data_list(server_name):
        """
        creates a new list of server's data paramaters
            :param server_name: {string} server's host name
        """
        server_info = list()
        server_info.append(server_name)
        server_info.append(list())
        server_info.append(list())
        return server_info

@staticmethod
def get_NS_for_domain(server, domain_to_check):
    """
    querries this server for NS in the given domain
        :param server: {ServerInfo} server to make dns query from
        :param domain_to_check: {string} the domain to query
    """
    NS_dict = dict() # dictionary in the form of { server's name -> server's data }
    response = None
    resolver = dns.resolver.Resolver()
    for address in server[SI.HOST_ADDRESS]:
        resolver.nameservers.append(address)

        # queries the name servers for the given domain
        query = dns.message.make_query(domain_to_check, dns.rdatatype.NS)
        response = dns.query.udp(query, str(address))

        # analyses respone and creates data lists
        for rr in response.additional:
            if rr.name not in NS_dict:
                NS_dict[rr.name] = create_new_server_data_list(rr.name)
                NS_dict[rr.name].append(
                    "Name server for domain " + '"' + str(domain_to_check) + '"')
                NS_dict[rr.name].append(str(domain_to_check))
            add_server_data_from_query_response(NS_dict[rr.name], rr)

    # builds a ServerInfo object for each server data list
    name_servers = list()
    for server_data in NS_dict.values():
        name_servers.append(SI.ServerInfo(server_data))

    return name_servers


# static ServerInfo object list of 13 IANA root name servers
root_servers = build_root_servers_info_objects(ROOT_SERVERS_FILE_PATH)

class MisconfigurationInfo:

    def __init__(self, url):
        self.__url = url
        self.__domains = list()
        self.__initDomains()

    def __initDomains(self):
        subDomains = self.__url.split('.')
        for i in range(len(subDomains), 0, -1):
            sub = '.'.join(subDomains[i - 1:])
            self.__domains.append(sub)

    def find_misconfigurations(self):
        """
        Finds the differences between the servers lists of the resolver's response and the process of the DNS protocol
            :param server: {ServerInfo} a DNS for which the misconfiguration is computed 
            :param domain_to_check: {string} the domain that being checked for misconfigurations
            :returns: {tuple} - 3 lists that contains information about misconfigurations:
                        [0] - server name
                        [1] - server queried NS that are not known to ancestor domain servers
                        [2] - server queried NS that are not known to siblings domain servers
                        [3] - server queried NS that are not known to child domain servers
        """
        
        misconfigurations = None
        foreign_to_ancestor = None
        foreign_to_siblings = None
        foreign_to_child = None

        sub_domain_NS_list = list()
        sub_domain_level = len(self.__domains) - 1

        # start with IANA root server, query about top sub-domain first
        for root_server in root_servers:
                    sub_domain_NS_list.extend(get_NS_for_domain(
                        root_server, self.__domains[sub_domain_level]))

        sub_domain_level -= 1

        while(sub_domain_level > 0):
            # check misconfiguration for each server in list
            for server in sub_domain_NS_list:
                NS_to_compare_with = get_NS_for_domain(server, self.__domains[sub_domain_level])
                #TODO - Finish!
            
                
                                    
