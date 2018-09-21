from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from . import dns_utils
from .forms import SingleUrlForm
from django.views.decorators.csrf import csrf_exempt


class Member:
    def __init__(self, name, role="Project Member", brief=None, email="Not Allowed", image="", image_alt=None):
        self.name = name
        self.role = role
        self.brief = brief if brief is not None else "Acts as a " + role + " in this project"
        self.email = email
        self.image = "DNSmisconfiguration/" + image
        self.image_alt = image_alt if image_alt is not None else "Image of " + name


def index(request):

    members = list()
    members.append(Member("Tom Nissim"))
    members.append(Member("Tomer Lior"))
    members.append(Member("Tom Eliassy"))
    members.append(Member("Haya Shulman", role="Mentor"))

    context = {'team_members': members}
    return render(request, 'DNSmisconfiguration/index.html', context)


def csv(request):
    return render(request, 'DNSmisconfiguration/csv.html')


def address(request):
    if request.method == 'POST':
        form = SingleUrlForm(request.POST)
        if form.is_valid():
            dns_worker, misconfiguration_result = dns_utils.main_url(form.cleaned_data["url"])

            sorted_misconfiguration_count = sorted(misconfiguration_result.misconfiguration_count_dict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

            top10_misconfiguration_count = sorted_misconfiguration_count[:10]

            domains = list(map(lambda a: a[0], top10_misconfiguration_count))

            context = {'misconfigurations': list(map(lambda a: a[1], top10_misconfiguration_count)),
                       'domains_amount': len(domains)}

            for i, domain in enumerate(domains):
                domain_str_key = 'domain' + str(i)
                context[domain_str_key] = domain

            return render(request, 'DNSmisconfiguration/results.html', context)
    else:
        form = SingleUrlForm()

    return render(request, 'DNSmisconfiguration/address.html', {'form': form})


def about(request):
    return render(request, 'DNSmisconfiguration/about.html')


@csrf_exempt
def upload_csv(request):
    if request.method == 'POST':
        dns_worker, misconfiguration_result = dns_utils.main_csv(request.FILES['file'])

        sorted_misconfiguration_count = sorted(misconfiguration_result.misconfiguration_count_dict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

        top10_misconfiguration_count = sorted_misconfiguration_count[:10]

        domains = list(map(lambda a: a[0], top10_misconfiguration_count))

        context = {'misconfigurations': list(map(lambda a: a[1], top10_misconfiguration_count)),
                   'domains_amount': len(domains)}

        for i, domain in enumerate(domains):
            domain_str_key = 'domain' + str(i)
            context[domain_str_key] = domain

        return render(request, 'DNSmisconfiguration/results.html', context)

    return csv(request)


def uploaded_csv(request, csv_result):
    return HttpResponse("This is your CSV file: \n" + str(csv_result))
