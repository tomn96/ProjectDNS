# import csv
from .models import RootDNSServers


# def main1():
#     with open("IANA Root Servers.csv", "r") as f:
#         # utf8 = (line.decode('utf-8') for line in f)
#         file_reader = csv.reader(f)
#
#         for row in file_reader:
#             RootDNSServers.objects.create(host_name=row[0], ipv4_address=row[1], ipv6_address=row[2],
#                                           description=row[3])


def main2():
    roots = [["a.root-servers.net", "198.41.0.4", "2001:503:ba3e::2:30", "VeriSign Inc."],
             ["b.root-servers.net", "199.9.14.201", "2001:500:200::b", "University of Southern California (ISI)"],
             ["c.root-servers.net", "192.33.4.12", "2001:500:2::c", "Cogent Communications"],
             ["d.root-servers.net", "199.7.91.13", "2001:500:2d::d", "University of Maryland"],
             ["e.root-servers.net", "192.203.230.10", "2001:500:a8::e", "NASA (Ames Research Center)"],
             ["f.root-servers.net", "192.5.5.241", "2001:500:2f::f", "Internet Systems Consortium Inc."],
             ["g.root-servers.net", "192.112.36.4", "2001:500:12::d0d", "US Department of Defense (NIC)"],
             ["h.root-servers.net", "198.97.190.53", "2001:500:1::53", "US Army (Research Lab)"],
             ["i.root-servers.net", "192.36.148.17", "2001:7fe::53", "Netnod"],
             ["j.root-servers.net", "192.58.128.30", "2001:503:c27::2:30", "VeriSign Inc."],
             ["k.root-servers.net", "193.0.14.129", "2001:7fd::1", "RIPE NCC"],
             ["l.root-servers.net", "199.7.83.42", "2001:500:9f::42", "ICANN"],
             ["m.root-servers.net", "202.12.27.33", "2001:dc3::35", "WIDE Project"]]

    for row in roots:
        RootDNSServers.objects.create(host_name=row[0], ipv4_address=row[1], ipv6_address=row[2], description=row[3])
