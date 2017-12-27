#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dns.query
import dns.resolver
from dns.exception import DNSException

def query_authoritative_ns (domain, log=lambda msg: None):

    default = dns.resolver.get_default_resolver()
    ns = default.nameservers[0]

    n = domain.split('.')

    for i in range(len(n), 0, -1):
        sub = '.'.join(n[i-1:])

        log('Looking up %s on %s' % (sub, ns))
        query = dns.message.make_query(sub, dns.rdatatype.NS)
        response = dns.query.udp(query, ns)

        rcode = response.rcode()
        if rcode != dns.rcode.NOERROR:
            if rcode == dns.rcode.NXDOMAIN:
                raise Exception('%s does not exist.' % (sub))
            else:
                raise Exception('Error %s' % (dns.rcode.to_text(rcode)))

        if len(response.authority) > 0:
            rrsets = response.authority
        elif len(response.additional) > 0:
            rrsets = [response.additional]
        else:
            rrsets = response.answer

        # Handle all RRsets, not just the first one
        for rrset in rrsets:
            for rr in rrset:
                if rr.rdtype == dns.rdatatype.SOA:
                    log('Same server is authoritative for %s' % (sub))
                elif rr.rdtype == dns.rdatatype.A:
                    ns = rr.items[0].address
                    log('Glue record for %s: %s' % (rr.name, ns))
                elif rr.rdtype == dns.rdatatype.NS:
                    authority = rr.target
                    ns = default.query(authority).rrset[0].to_text()
                    log('%s [%s] is authoritative for %s; ttl %i' %
                        (authority, ns, sub, rrset.ttl))
                    result = rrset
                else:
                    # IPv6 glue records etc
                    #log('Ignoring %s' % (rr))
                    pass

    return result

import sys

def log (msg):
    sys.stderr.write(msg + u'\n')

for s in sys.argv[1:]:
    print(query_authoritative_ns (s, log))