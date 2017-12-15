from django.shortcuts import render
from django.http import HttpResponse

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
    return HttpResponse("please upload CSV file")


def address(request):
    return HttpResponse("please enter URL address")
