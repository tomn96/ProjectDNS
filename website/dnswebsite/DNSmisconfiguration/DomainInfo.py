import dns
import dns.name
import dns.query
import dns.resolver
from . import ServerInfo as SI
from .models import RootDNSServers

# TOP_LEVEL_DOMAIN = 0

# RESOLVER_ORIGIN = True

# time before ignoring udp response (in seconds)
UDP_QUERY_TIME_OUT = 4

# server data that should be handled as a list
LIST_TYPE_ARGS = {SI.IPV4_INDEX, SI.IPV6_INDEX, SI}


class DNSWorker:

    def __init__(self):
        # static dictionary in the form of { server_name -> ServerInfo }
        # the key is the server's name, the value is a ServerInfo object that contains the server's data
        self.name_to_server_info_dict = dict()

        # static ServerInfo object list of 13 IANA root name servers
        self.root_servers = self.build_root_servers_info_objects()

        # static dictionary in the form of { (server's name , domain) -> list of NS the servers knows for the domain }
        # the key is a tuple of server's name, domain, the value is a list of known servers to the server with the given server's name
        self.DNS_dict = dict()

    def get_master_root_servers(self):
        """
        reads the addresses of the 13 IANA root servers
        (see https://www.iana.org/domains/root/servers)
            :returns: {array} the raw data read from csv file
        """
        roots = RootDNSServers.objects.all()
        result = []
        for root in roots:
            result.append([root.host_name, root.ipv4_address, root.ipv6_address, root.description])

        return result


    def build_root_servers_info_objects(self):
        """
        builds ServerInfo objects for each root server
            :param servers_info: {list} the servers data parameters
            :returns: {list} list of server names for each root server
        """
        servers_info = self.get_master_root_servers()
        root_servers_names = set()
        for server_csv_data in servers_info:
            server_data = list()
            for i in range(len(server_csv_data)):
                if i in LIST_TYPE_ARGS:
                    server_data.append(list())
                    server_data[i].append(server_csv_data[i])
                else:
                    server_data.append(server_csv_data[i])
            server_data.append("Root Domain")
            self.name_to_server_info_dict[server_data[SI.HOST_INDEX]] = SI.ServerInfo(server_data)
            root_servers_names.add(server_data[SI.HOST_INDEX])
        return root_servers_names


    def add_server_data_from_query_response(self, server_info, response):
            """
            adds data from a given dns response to server_info list
                :param server_info: {list} a list of server's data paramaters
                :param response: {DNS.response} a dns response for a 'udp' query
            """
            if response.rdtype == dns.rdatatype.NS:  # TODO: can be called if record was from authority/answer. not sure whether need to add code or not.
                return

            ip_type = None

            # checks if IPv4 or IPv6
            if response.rdtype == dns.rdatatype.A:
                ip_type = SI.IPV4_INDEX
            elif response.rdtype == dns.rdatatype.AAAA:
                ip_type = SI.IPV6_INDEX
            elif response.rdtype == dns.rdatatype.CNAME or response.rdtype == dns.rdatatype.SOA:
                return
            # adds all addresses listed for the server
            for ip in response.items:
                server_info[ip_type].append(ip.address)

            return


    def create_new_server_data_list(self, server_name):
            """
            creates a new list of server's data paramaters
                :param server_name: {string} server's host name
            """
            server_info = list()
            server_info.append(server_name)
            server_info.append(list())
            server_info.append(list())
            return server_info


    def get_NS_for_domain(self, server, domain_to_check):
        """
        queries this server for NS in the given domain
            :param server: {ServerInfo} server to make dns query from
            :param domain_to_check: {string} the domain to query
            :returns: {list} names of servers known to server
        """
        server_data_dict = dict() # dictionary in the form of { server's name -> server's data }
        known_servers_names = set() # a set of server names
        response = None
        resolver = dns.resolver.Resolver()

        # clears the default servers the resolver queries
        # [local COMM/dns and 8.8.8.8 (google)]
        resolver.nameservers.clear()
        server_name = None

        # adds the server's addresses to the servers queried
        # by resolver
        for address in self.name_to_server_info_dict[server][SI.HOST_ADDRESS]:
            resolver.nameservers.append(address)

        try:
            # queries the name server for the given domain
            query = dns.message.make_query(domain_to_check, dns.rdatatype.NS)
            response = dns.query.udp(query, str(address), timeout=UDP_QUERY_TIME_OUT)
        except dns.resolver.NXDOMAIN:
            print("No such Domain" + domain_to_check)
        except dns.resolver.Timeout:
            print(str(server) + " was queried for the domain " + domain_to_check + " and request timeout")
            # self.DNS_dict[(str(server), domain_to_check)] = set()
            return None
        except dns.exception.DNSException:
            print("Unhandled DNS exception")
        except Exception as e:
            print(e.__cause__)

        if response is None:
            return None

        # analyses respone and creates data lists
        if len(response.authority) > 0:
            for rr in response.authority[0].items:
                server_name = str(rr.mname) if rr.rdtype == dns.rdatatype.SOA else str(rr.target)
                known_servers_names.add(server_name)
                if server_name not in self.name_to_server_info_dict:
                    server_data_dict[server_name] = self.create_new_server_data_list(server_name)
                    server_data_dict[server_name].append("Name server for domain " + '"' + str(domain_to_check) + '"')
                    server_data_dict[server_name].append(str(domain_to_check))
                    self.add_server_data_from_query_response(server_data_dict[server_name], rr)
                else:
                    self.name_to_server_info_dict[server_name].add_rr_data(rr)

        if len(response.answer) > 0:
            for rr in response.answer[0].items:
                server_name = str(rr.target)
                known_servers_names.add(server_name)
                if server_name not in self.name_to_server_info_dict:
                    server_data_dict[server_name] = self.create_new_server_data_list(server_name)
                    server_data_dict[server_name].append(
                        "Name server for domain " + '"' + str(domain_to_check) + '"')
                    server_data_dict[server_name].append(str(domain_to_check))
                    self.add_server_data_from_query_response(server_data_dict[server_name], rr)
                else:
                    self.name_to_server_info_dict[server_name].add_rr_data(rr)

        for rr in response.additional:
            server_name = str(rr.name)
            known_servers_names.add(server_name)
            if server_name not in self.name_to_server_info_dict:
                server_data_dict[server_name] = self.create_new_server_data_list(server_name)
                server_data_dict[server_name].append(
                    "Name server for domain " + '"' + str(domain_to_check) + '"')
                server_data_dict[server_name].append(str(domain_to_check))
                self.add_server_data_from_query_response(server_data_dict[server_name], rr)
            else:
                self.name_to_server_info_dict[server_name].add_rr_data(rr)

        # builds a ServerInfo object for each server data list
        for server_data in server_data_dict.values():
            self.name_to_server_info_dict[server_data[SI.HOST_INDEX]] = SI.ServerInfo(server_data)
            known_servers_names.add(server_data[SI.HOST_INDEX])

        # builds a ServerInfo object for each server data list
        return known_servers_names


class DomainInfo:
    """
    stores data related to the domain
    """
    def __init__(self, url):
        self.__url = url   
        self.__domains = list()     # sub domains
        self.__initDomains()

    def __initDomains(self):
        subDomains = self.__url.split('.')
        for i in range(len(subDomains), 0, -1):
            sub = '.'.join(subDomains[i - 1:])
            self.__domains.append(sub)

    def get_domains(self):
        """
        :returns: {list} a list of sub-domains extracted from the url
        """
        return self.__domains

    def get_domain_info(self, domain, dns_worker):
        """
        Queries the IANA root servers about the sub-domains of this url
        the result is stored in a static dictionary
        """
        servers_to_check = set()
        
        # start with IANA root server, query about top sub-domain first
        for root_server in dns_worker.root_servers:
            servers_to_check.add(root_server)

        while len(servers_to_check) > 0:
            for server in servers_to_check:
                if (server, domain) not in dns_worker.DNS_dict:
                    answer = dns_worker.get_NS_for_domain(server, domain)
                    if(answer is not None):
                        dns_worker.DNS_dict[(server,domain)] = answer
                        for new_server in answer:
                            servers_to_check.add(new_server)
                servers_to_check.remove(server)
