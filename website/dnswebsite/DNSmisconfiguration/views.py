import os
import pickle
import csv
from ast import literal_eval
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import StreamingHttpResponse, Http404, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from . import dns_utils, CheckCSV
from .forms import SingleUrlForm, UploadFileForm
from .models import StoredDict, RootDNSServers


class Member:
    def __init__(self, name, role="Project Member", brief=None, email="Not Allowed", image="", image_alt=None):
        self.name = name
        self.role = role
        self.brief = brief if brief is not None else "Acts as a " + role + " in this project"
        self.email = email
        self.image = "DNSmisconfiguration/" + image
        self.image_alt = image_alt if image_alt is not None else "Image of " + name


def handle_dns(dns_worker, misconfiguration_result):
    information = StoredDict.objects.create(pickle_dict=pickle.dumps(dns_worker.name_to_server_info_dict))
    dns = StoredDict.objects.create(pickle_dict=pickle.dumps(dns_worker.DNS_dict))
    misconfiguration_data = StoredDict.objects.create(pickle_dict=pickle.dumps(misconfiguration_result.misconfiguration_dict))
    misconfiguration_count = StoredDict.objects.create(pickle_dict=pickle.dumps(misconfiguration_result.misconfiguration_count_dict))

    sorted_misconfiguration_count = sorted(misconfiguration_result.misconfiguration_count_dict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

    top10_misconfiguration_count = sorted_misconfiguration_count[:10]

    domains = list(map(lambda a: a[0], top10_misconfiguration_count))

    context = {'misconfigurations': list(map(lambda a: a[1], top10_misconfiguration_count)),
               'domains_amount': len(domains),
               'information_id': str(information.id),
               'dns_id': str(dns.id),
               'misconfiguration_data_id': str(misconfiguration_data.id),
               'misconfiguration_count_id': str(misconfiguration_count.id),
               'also_dns': True
               }

    for i, domain in enumerate(domains):
        domain_str_key = 'domain' + str(i)
        context[domain_str_key] = domain

    return context


def handle_misconfiguration(misconfiguration_result):
    misconfiguration_data = StoredDict.objects.create(pickle_dict=pickle.dumps(misconfiguration_result.misconfiguration_dict))
    misconfiguration_count = StoredDict.objects.create(pickle_dict=pickle.dumps(misconfiguration_result.misconfiguration_count_dict))

    sorted_misconfiguration_count = sorted(misconfiguration_result.misconfiguration_count_dict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

    top10_misconfiguration_count = sorted_misconfiguration_count[:10]

    domains = list(map(lambda a: a[0], top10_misconfiguration_count))

    context = {'misconfigurations': list(map(lambda a: a[1], top10_misconfiguration_count)),
               'domains_amount': len(domains),
               'information_id': str(-1),
               'dns_id': str(-1),
               'misconfiguration_data_id': str(misconfiguration_data.id),
               'misconfiguration_count_id': str(misconfiguration_count.id)
               }

    for i, domain in enumerate(domains):
        domain_str_key = 'domain' + str(i)
        context[domain_str_key] = domain

    return context


def create_root():
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

    for root in roots:
        if not RootDNSServers.objects.filter(host_name=root[0]).exists():
            RootDNSServers.objects.create(host_name=root[0], ipv4_address=root[1], ipv6_address=root[2], description=root[3])


def index(request):
    # create_root()

    members = list()
    members.append(Member("Tom Nissim", email="tom.nissim1@mail.huji.ac.il", image_alt=""))
    members.append(Member("Tomer Lior", email="tomer.lior@mail.huji.ac.il", image_alt=""))
    members.append(Member("Tom Eliassy", email="tom.eliassy@mail.huji.ac.il", image_alt=""))
    members.append(Member("Haya Shulman", role="Mentor", image_alt=""))

    context = {'team_members': members}
    return render(request, 'DNSmisconfiguration/index.html', context)


def readme(request):
    return render(request, 'DNSmisconfiguration/readme.html')


def address(request):
    if request.method == 'POST':
        form = SingleUrlForm(request.POST)
        if form.is_valid():
            dns_worker, misconfiguration_result = dns_utils.main_url(form.cleaned_data["url"])
            context = handle_dns(dns_worker, misconfiguration_result)
            return render(request, 'DNSmisconfiguration/results.html', context)
    else:
        form = SingleUrlForm()

    return render(request, 'DNSmisconfiguration/address.html', {'form': form})


@csrf_exempt
def csv_url(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            dns_worker, misconfiguration_result = dns_utils.main_csv(request.FILES['file'])
            context = handle_dns(dns_worker, misconfiguration_result)
            context_stored = StoredDict.objects.create(pickle_dict=pickle.dumps(context))
            return HttpResponseRedirect('/results/' + str(context_stored.id))
    else:
        form = UploadFileForm()
    return render(request, 'DNSmisconfiguration/csv.html', {'form': form})


@csrf_exempt
def known_ns(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            utf8 = (line.decode('utf-8') for line in file)
            file_reader = csv.reader(utf8)

            known_ns_dict = dict()
            for counter, row in enumerate(file_reader):
                if row == ['(Server Name, Domain)', 'Servers known in domain']:
                    continue
                elif len(row) == 0:
                    continue
                else:
                    try:
                        tuple_key = literal_eval(row[0])
                        set_value = literal_eval(row[1])
                    except Exception:
                        continue

                    if type(tuple_key) == tuple and type(set_value) == set and len(tuple_key) == 2:
                        known_ns_dict[tuple_key] = set_value
                    else:
                        continue

            misconfiguration_result = dns_utils.main_known_ns(known_ns_dict)
            context = handle_misconfiguration(misconfiguration_result)
            context_stored = StoredDict.objects.create(pickle_dict=pickle.dumps(context))
            return HttpResponseRedirect('/results/' + str(context_stored.id))
    else:
        form = UploadFileForm()
    return render(request, 'DNSmisconfiguration/known_ns.html', {'form': form})


def results(request, dict_id):
    stored_context = get_object_or_404(StoredDict, id=int(dict_id))
    context = pickle.loads(stored_context.pickle_dict)
    return render(request, 'DNSmisconfiguration/results.html', context)


def top500(request):
    file_path = os.path.join(settings.STATIC_ROOT, 'DNSmisconfiguration/500topResults/misconfigurations_count.csv')
    if os.path.exists(file_path):
        misconfigurations_count = dict()
        with open(file_path, 'r') as fh:
            reader = csv.reader(fh)
            for counter, row in enumerate(reader):
                if row == ['domain', 'num of misconfigurations']:
                    continue
                elif len(row) == 0:
                    continue
                else:
                    if int(row[1]) == 0:
                        continue
                    else:
                        misconfigurations_count[row[0]] = int(row[1])

        sorted_misconfiguration_count = sorted(misconfigurations_count.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

        top10_misconfiguration_count = sorted_misconfiguration_count[:10]

        domains = list(map(lambda a: a[0], top10_misconfiguration_count))

        context = {'misconfigurations': list(map(lambda a: a[1], top10_misconfiguration_count)),
                   'domains_amount': len(domains),
                   'also_dns': True
                   }

        for i, domain in enumerate(domains):
            domain_str_key = 'domain' + str(i)
            context[domain_str_key] = domain

        return render(request, 'DNSmisconfiguration/top500.html', context)
    else:
        raise Http404


class Echo:
    def write(self, value):
        return value


def download_generator(writer, data):
    # yield writer.writeheader()
    for row in data:
        yield writer.writerow(row)


def download_dict(request, dict_id, option):
    int_dict_id = int(dict_id)
    int_option = int(option)

    field_names1 = ['Server Name', 'Server Information']
    field_names2 = ['(Server Name, Domain)', 'Servers known in domain']
    field_names3 = ["server1, server2, domain", "misconfiguration info"]
    field_names4 = ["domain", "num of misconfigurations"]
    field_names_list = [field_names1, field_names2, field_names3, field_names4]
    names = ['results_servers.csv', 'results_records.csv', 'misconfigurations.csv', 'misconfigurations_count.csv']

    stored_dict = get_object_or_404(StoredDict, id=int_dict_id)
    real_dict = pickle.loads(stored_dict.pickle_dict)

    pseudo_buffer = Echo()
    writer = csv.DictWriter(pseudo_buffer, fieldnames=field_names_list[int_option])
    data = (dict(zip(field_names_list[int_option], [k, v])) for k, v in real_dict.items())

    response = StreamingHttpResponse(download_generator(writer, data), content_type="text/csv")

    response['Content-Disposition'] = 'attachment; filename="' + names[int_option] + '"'
    return response


def download_csv_file(request, path):
    file_path = os.path.join(settings.STATIC_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/csv")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


def download_results_servers(request):
    return download_csv_file(request, 'DNSmisconfiguration/results_servers.csv')


def download_results_records(request):
    return download_csv_file(request, 'DNSmisconfiguration/results_records.csv')


def download_misconfigurations(request):
    return download_csv_file(request, 'DNSmisconfiguration/misconfigurations.csv')


def download_misconfigurations_count(request):
    return download_csv_file(request, 'DNSmisconfiguration/misconfigurations_count.csv')


def download_top500_results_servers(request):
    return download_csv_file(request, 'DNSmisconfiguration/500topResults/results_servers.csv')


def download_top500_results_records(request):
    return download_csv_file(request, 'DNSmisconfiguration/500topResults/results_records.csv')


def download_top500_misconfigurations(request):
    return download_csv_file(request, 'DNSmisconfiguration/500topResults/misconfigurations.csv')


def download_top500_misconfigurations_count(request):
    return download_csv_file(request, 'DNSmisconfiguration/500topResults/misconfigurations_count.csv')
