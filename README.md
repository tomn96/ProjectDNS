# DNS misconfiguration detection tool
## Networks Security course 67914

----
## Abstract
see [DNS protocol](https://ns1.com/resources/dns-protocol)

> Tool for detecting and analyzing DNS misconfigurations among the internet servers.The tool scans through a list of URL addresses, and checks whether their authoritative servers are misconfigured.

>The program is executed through a website that hosted in AWS.

----
## Usage
### The program supports 2 execution modes:

#### 1. Single URL
> receives a single url address via designated text box in the website UI.

> for example: walla.co.il

#### 2. Multiple URLs in CSV format
> receives a csv uploaded to the designated upload box. The csv file consists of the URLs that will be checked, in the following format:

> URL_1

> URL_2

> ...

> URL_N

> for example: input.csv:

> google.com

> walla.co.il

> packetlife.net

> moodle2.cs.huji.ac.il

----
## Process and Output

### The program performs two stages 

#### Information gathering and Data Base construction 

> the program breaks each URL in to sub-domains, for each sub domain the program collects DNS data. 

> The program will output **two** csv files consists of the data it collected:

>1. **results_servers.csv**

>  a csv file consists of the data collected on each server that participated in the dns process for the sub-domain.

>  The file is in the format of:

>  <server name> , <server information>

>  server information holds the following attributes for a specific server:
>  * host name

>  * domain
>  * ipv4 addresses

>  * ipv6 addresses
>  * description

>  for additional information related to format
>  [download results_records.csv example](https://ns1.com/resources/dns-protocol)

>2. **results_records.csv**

>  a csv file in which each record consists of a *name server*, a domain and the name servers that the *name server* knows in the domain

>  The file is in the format of:

>  <server name, domain> , <servers known in the domain>

>  [download results_records.csv example](https://ns1.com/resources/dns-protocol)


#### Misconfigurations Detection 

> the program uses the data it collected in the previous stage and analyzes it in order to discover misconfigurations.

> A misconfiguration is defined to be a state in which two servers "knows" different servers in the same domain, one server knows more name servers (or less) in the same domain.

> The program will output **two** csv files consists of the misconfiguration it detected:

>1. **misconfigurations.csv**

>  a csv file consists of the misconfigurations that were discovered.

>  The file is in the format of:

>  <server1, server2, domain> , <Misconfiguration information>

>  Misconfiguration information holds the following attributes for a specific misconfiguration:
>  * host name

>  * domain
>  * first server

>  * second server
>  * the servers that both servers know

>  * the servers that the *first server* knows and the *second server* does not
>  * the servers that the *second server* knows and the *first server* does not


>  for additional information related to format
>  [download misconfigurations.csv example](https://ns1.com/resources/dns-protocol)

>2. **misconfigurations_count.csv**

>  a csv file in which each record consists of a *domain*, and the number of misconfigurations detected for the *domain*

>  The file is in the format of:

>  <domain> , <number of misconfigurations detected>

>  [download misconfigurations_count.csv example](https://ns1.com/resources/dns-protocol)

**In addition to the downloadable csv files, the results are stored in a Django database contained in the website
**