import dns
import dns.name
import dns.query
import dns.resolver
import QueryObj as QO
import sys
import pandas as pd

FILE_INDEX = 1
FIRST = 0

#---------------------------------------------------------------Assist Methods-----------------------------------------

#This function finds the values of lst1 that ARE NOT in lst2
def build_foreign_list(lst1, lst2):
    result = list()
    for element in lst1:
        i = 0
        while i <(len(lst2)):
            if element == lst2[i]:
                break
            i+= 1
        if i == len(lst2):
            result.append(element)
    return result

#Finds the differences between the servers lists of the resolver's response and the process of the DNS protocol
def compare_servers_list(resolver_list, dns_routine_list):
    foreign_to_resolver = build_foreign_list(dns_routine_list, resolver_list)
    foreign_to_dns_routine = build_foreign_list(resolver_list, dns_routine_list)
    return (foreign_to_resolver, foreign_to_dns_routine)


#----------------------------------------------------------------Major Methods------------------------------------------

#This function performs an execution of the DNS protocol regarding the requested domain
def perform_DNS_routine(domain, log=lambda msg: None):

    # gets the default dns resolver
    default_resolver = dns.resolver.get_default_resolver()

    # creates the initial dns info tree
    dns_tree = dict()

    # starts with the first name servers of the default resolver
    ns = default_resolver.nameservers[0]

    # splits the domain to sub-domains
    n = domain.split('.') #TODO - create an assist method for preparing all the required combination of the NS?
    for i in range(len(n), 0, -1):
        sub = '.'.join(n[i - 1:])
        dns_tree[sub] = list()

        # starts checking the sub-domain name servers
        log('Looking up %s on %s' % (sub, ns))
        query = dns.message.make_query(sub, dns.rdatatype.NS)
        response = dns.query.udp(query, ns)

        # checks if succeeded (found name servers)
        rcode = response.rcode()
        if rcode != dns.rcode.NOERROR:
            if rcode == dns.rcode.NXDOMAIN:
                raise Exception('%s does not exist.' % (sub))
            else:
                raise Exception('Error %s' % (dns.rcode.to_text(rcode)))

            #TODO - Where these Exceptions are caught?

        # checks if there are authoritative servers for this name server
        if len(response.authority) > 0:
            rrsets = response.authority
        elif len(response.additional) > 0:
            rrsets = [response.additional]
        else:
            # no authoritative severs found - saves the current name server as authoritative
            rrsets = response.answer
        rrName = None
        queryInfo = None
        # handles all authoritative name servers for the current domain (not just the first one)
        for rrset in rrsets:
            for i in range(len(rrset)):
                if((rrset[i].rdtype == dns.rdatatype.A or rrset[i].rdtype == dns.rdatatype.AAAA) and
                           rrName != rrset[i].name or rrset[i].rdtype == dns.rdatatype.NS ):
                    queryInfo = QO.QueryObj(sub)
                    dns_tree[sub].append(queryInfo)
                    if (rrset[i].rdtype != dns.rdatatype.NS):
                        rrName = rrset[i].name
                    else:
                        rrName = str(rrset[i])
                if rrset[i].rdtype == dns.rdatatype.SOA: # in case of DNSSec
                    log('Same server is authoritative for %s' % (sub))
                elif rrset[i].rdtype == dns.rdatatype.A:  # in case of address
                    ns = rrset[i].items[0].address
                    log('Glue record for %s: %s' % (rrset[i].name, ns))
                elif rrset[i].rdtype == dns.rdatatype.NS:  # in case of name server
                    authority = rrset[i].target
                    ns = default_resolver.query(authority).rrset[0].to_text()

                    # TODO ask about children too

                    log('%s [%s] is authoritative for %s; ttl %i' %
                        (authority, ns, sub, rrset.ttl))
                    result = rrset
                else:
                    log('Ignoring %s' % (rrset[i]))
                    pass
                queryInfo.addRRData(rrset[i])
            queryInfo = None
    return dns_tree




def log(msg):
    sys.stderr.write(msg + u'\n')


def printQueryObjects(DNSTree):
    for domain in DNSTree.keys():
        print("################################\nDomain: " + domain +"\n################################\n")
        for qo in DNSTree[domain]:
            print(str(qo))

# for s in sys.argv[1:]:


    # lst1 = ["Tomer", "Yossi", "Tom", "Avi"]
    # lst2 = ["Yossi", "Avi", "Moshe"]
    # t = compare_servers_list(lst1, lst2)



#------------------------------------------------------------Main Function----------------------------------------------
# if __name__ == "__main__":
#     #Gets the input from the user
#     df=pd.read_csv(sys.argv[FILE_INDEX], sep=',',header=None)
#
#     #Process every url address in the input csv file
#     for urlAddr in df.itertuples():
#         #TODO Check validation of the url addr?
#         perform_DNS_routine(urlAddr)

if __name__ == '__main__':
    d = perform_DNS_routine("walla.co.il")
    # printQueryObjects(d)