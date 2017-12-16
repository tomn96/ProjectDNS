from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from .utils.handle_csv import handle_csv_file
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
    return render(request, 'DNSmisconfiguration/address.html')


def about(request):
    return render(request, 'DNSmisconfiguration/about.html')


@csrf_exempt
def upload_csv(request):
    if request.method == 'POST':
        result = handle_csv_file(request.FILES['file'])
        return HttpResponseRedirect("uploaded_csv/" + str(result))
    return csv(request)


def uploaded_csv(request, csv_result):
    return HttpResponse("This is your CSV file: \n" + str(csv_result))
