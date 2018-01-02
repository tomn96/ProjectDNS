import dns
import dns.name
import dns.query
import dns.resolver
import QueryObj as QO

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

def compare_servers_list(resolver_list, dns_routine_list):
    foreign_to_resolver = build_foreign_list(dns_routine_list, resolver_list)
    foreign_to_dns_routine = build_foreign_list(resolver_list, dns_routine_list)
    return (foreign_to_resolver, foreign_to_dns_routine)



def perform_DNS_routine(domain, log=lambda msg: None):

    # gets the default dns resolver
    default_resolver = dns.resolver.get_default_resolver()

    # creates the initial dns info tree
    dns_tree = dict()

    # starts with the first name server of the default resolver
    ns = default_resolver.nameservers[0]

    # splits the domain to sub-domains
    n = domain.split('.')
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

        # checks if there are authoritative servers for this name server
        if len(response.authority) > 0:
            rrsets = response.authority
        elif len(response.additional) > 0:
            rrsets = [response.additional]
        else:
            # no authoritative severs found - saves the current name server as authoritative
            rrsets = response.answer

        # handles all authoritative name servers for the current domain (not just the first one)
        for rrset in rrsets:
            for rr in rrset:
                if rr.rdtype == dns.rdatatype.SOA: # in case of DNSSec
                    log('Same server is authoritative for %s' % (sub))
                elif rr.rdtype == dns.rdatatype.A:  # in case of address
                    ns = rr.items[0].address
                    log('Glue record for %s: %s' % (rr.name, ns))
                elif rr.rdtype == dns.rdatatype.NS:  # in case of name server
                    authority = rr.target
                    ns = default_resolver.query(authority).rrset[0].to_text()

                    # TODO ask about children too

                    queryInfo = QO.QueryObj(str(rr))
                    dns_tree[sub].append(queryInfo)
                    log('%s [%s] is authoritative for %s; ttl %i' %
                        (authority, ns, sub, rrset.ttl))
                    result = rrset
                else:
                    # IPv6 glue records etc
                    log('Ignoring %s' % (rr))
                    pass

    return result


import sys


def log(msg):
    sys.stderr.write(msg + u'\n')


for s in sys.argv[1:]:
    print(perform_DNS_routine(s, log))

# lst1 = ["Tomer", "Yossi", "Tom", "Avi"]
# lst2 = ["Yossi", "Avi", "Moshe"]
# t = compare_servers_list(lst1, lst2)

