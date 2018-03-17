import dns
import dns.name
import dns.query
import dns.resolver

class DomainInfo:

    def __init__(self, domain, default_resolver):

        # ToDo document the meaning of each list
        self.__domain = domain
        self.__default_resolver = default_resolver
        self.__defaultNS = list()


    # This function finds the values of lst1 that ARE NOT in lst2
    def build_foreign_list(self, lst1, lst2):
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

    # TODO alter the function to match the new version
    # Finds the differences between the servers lists of the resolver's response and the process of the DNS protocol
    def find_misconfigurations(self, listToCompare):
        foreign_to_server = self.build_foreign_list(list(self.__name_servers), listToCompare)
        foreign_to_dns_routine = self.build_foreign_list(listToCompare, list(self.__name_servers))
        self.__misconfigurations = (foreign_to_server, foreign_to_dns_routine)

    def getDefaultQueriedServers(self):

        # starts with the first name server of the default resolver
        serverToStartFrom = self.__default_resolver.nameservers[0]

        # create a query for the name servers of this domain
        query = dns.message.make_query(self.__domain, dns.rdatatype.NS)
        self.__response = dns.query.udp(query, serverToStartFrom)

        # check if query was successfull
        rcode = self.__response.rcode()
        if rcode != dns.rcode.NOERROR:
            if rcode == dns.rcode.NXDOMAIN:
                raise Exception('%s does not exist.' % (self.__domain))
            else:
                raise Exception('Error %s' % (dns.rcode.to_text(rcode)))

                # TODO - Where these Exceptions are caught?

        # checks if there are authoritative servers for this name server
        if len(self.__response.authority) > 0:
            rrsets = self.__response.authority
        elif len(self.__response.additional) > 0:
            rrsets = [self.__response.additional]
        else:
            rrsets = self.__response.answer

        # handles all authoritative name servers for the current domain (not just the first one)
        for rrset in rrsets:
            for rr in rrset:
                if(rr.rdtype)
                self.__selfQueriedNameServers.append(rr.items[0])
                if (rr.rdtype != dns.rdatatype.NS):
                    rrName = rr.name
                else:
                    rrName = str(rr)
                if rr.rdtype == dns.rdatatype.A:  # in case of address ipv4
                    ns = rr.items[0].address
                elif rr.rdtype == dns.rdatatype.NS:  # in case of name server
                    authority = rr.target
                    ns = self.__default_resolver.query(authority).rrset[0].to_text()
                else:
                    pass
                addRRData(rr)
            queryInfo = None
            return ns

    # def getNSForSubDomain(self):