import dns
import dns.name
import dns.query
import dns.resolver
import DomainInfo as DI
import ServerInfo as SI
import pandas as PD

TOP_LEVEL_DOMAIN = 0

RESOLVER_ORIGIN = True

# time before ignoring udp response (in seconds)
UDP_QUERY_TIME_OUT = 4

# server data that should be handled as a list
LIST_TYPE_ARGS = {SI.IPV4_INDEX,SI.IPV6_INDEX,SI}

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
            if i in LIST_TYPE_ARGS:
                server_data.append(list())
                server_data[i].append(server_csv_data[i])
            else:
                server_data.append(server_csv_data[i])
        server_data.append("Root Domain")
        servers.append(SI.ServerInfo(server_data))
    return servers

''' @staticmethod
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
    return result '''

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

        # if response.rdtype == dns.rdatatype.NS: # TODO: can be called if record was from authority/answer. not sure whether need to add code or not.

        # adds all addresses listed for the server
        for ip in response.items:
            server_info[ip_type].append(ip.address)

        return server_info

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

def get_NS_for_domain(server, domain_to_check):
    """
    querries this server for NS in the given domain
        :param server: {ServerInfo} server to make dns query from
        :param domain_to_check: {string} the domain to query
    """
    NS_dict = dict() # dictionary in the form of { server's name -> server's data }
    response = None
    resolver = dns.resolver.Resolver()

    # clears the default servers the resolver queries
    # [local COMM/dns and 8.8.8.8 (google)]
    resolver.nameservers.clear()
    server_name = None

    # adds the server's addresses to the servers queried
    # by resolver
    for address in server[SI.HOST_ADDRESS]:
        resolver.nameservers.append(address)

    try:
        # queries the name server for the given domain
        query = dns.message.make_query(domain_to_check, dns.rdatatype.NS)
        response = dns.query.udp(query, str(address), timeout=UDP_QUERY_TIME_OUT)
    except dns.resolver.NXDOMAIN:
        print("No such Domain")
    except dns.resolver.Timeout:
        print("Request timeout")
        return None
    except dns.exception.DNSException:
        print("Unhandled DNS exception")
    except Exception as e:
        print(e.__cause__)

    # analyses respone and creates data lists
    for rr in response.additional:
        server_name = str(rr.name)
        if server_name not in NS_dict:
            NS_dict[server_name] = create_new_server_data_list(server_name)
            NS_dict[server_name].append(
                "Name server for domain " + '"' + str(domain_to_check) + '"')
            NS_dict[server_name].append(str(domain_to_check))
        add_server_data_from_query_response(NS_dict[server_name], rr)

    if len(response.authority) > 0:
        for rr in response.authority[0].items:
            server_name = str(rr.target)
            if server_name not in NS_dict:
                NS_dict[server_name] = create_new_server_data_list(server_name)
                NS_dict[server_name].append(
                    "Name server for domain " + '"' + str(domain_to_check) + '"')
                NS_dict[server_name].append(str(domain_to_check))
            add_server_data_from_query_response(NS_dict[server_name], rr)


    if len(response.answer) > 0:
        for rr in response.answer[0].items:
        server_name = str(rr.target)
        if server_name not in NS_dict:
            NS_dict[server_name] = create_new_server_data_list(server_name)
            NS_dict[server_name].append(
                "Name server for domain " + '"' + str(domain_to_check) + '"')
            NS_dict[server_name].append(str(domain_to_check))
        add_server_data_from_query_response(NS_dict[server_name], rr)
    

    # TODO: need to check if record comes from NS and then from A/AAAA. then should update instead of creating new object.

    # builds a ServerInfo object for each server data list
    name_servers = list()
    for server_data in NS_dict.values():
        name_servers.append(SI.ServerInfo(server_data))

    return name_servers


# static ServerInfo object list of 13 IANA root name servers
root_servers = build_root_servers_info_objects(ROOT_SERVERS_FILE_PATH)

# static dictionary in the form of { domain -> list of NS the root servers knows for the domain } 
# equivalent to the union of all IANA root NS answers for a specific domain
root_NS_dict = dict()

# static dictionary in the form of { server's name + domain -> list of NS the servers knows for the domain }
DNS_dict = dict()

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

    def get_domain_info(self, domain):
        """
        Queries the IANA root servers about the sub-domains of this url
        the result is stored in a static dictionary
        """
        servers_to_check = set()

        # for server in get_NS_for_domain(root_servers[0], "il"):
        #     get_NS_for_domain(server,"il")
        
        # start with IANA root server, query about top sub-domain first
        for root_server in root_servers:
            servers_to_check.add(root_server)

        while len(servers_to_check) > 0:
            for server in servers_to_check:
                if (server, domain) not in DNS_dict:
                    answer = get_NS_for_domain(server, domain)
                    if(answer is not None):
                        DNS_dict[(server,domain)] = answer
                        for new_server in answer:
                            servers_to_check.add(new_server)
                servers_to_check.remove(server)

    def get_domains(self):
        return self.__domains
        
            
                                  
