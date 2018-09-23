import os
import pickle
import csv
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import StreamingHttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from . import dns_utils, CheckCSV
from .forms import SingleUrlForm
from .models import StoredDict


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


def index(request):

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


def csv_url(request):
    return render(request, 'DNSmisconfiguration/csv.html')


@csrf_exempt
def upload_csv(request):
    if request.method == 'POST':
        dns_worker, misconfiguration_result = dns_utils.main_csv(request.FILES['file'])
        context = handle_dns(dns_worker, misconfiguration_result)
        return render(request, 'DNSmisconfiguration/results.html', context)

    return csv_url(request)


def known_ns(request):
    return render(request, 'DNSmisconfiguration/known_ns.html')


@csrf_exempt
def upload_known_ns(request):
    if request.method == 'POST':
        misconfiguration_result = CheckCSV.main_known_ns(request.FILES['file'])
        context = handle_misconfiguration(misconfiguration_result)
        return render(request, 'DNSmisconfiguration/results.html', context)

    return known_ns(request)


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
        with open(file_path, 'r') as f:
            response = StreamingHttpResponse((line for line in f), content_type="text/csv")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
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
