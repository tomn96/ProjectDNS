from django.shortcuts import render
from django.http import HttpResponse


def index(request):

    members = list()
    members.append(Member('Tom Nissim'))
    members.append(Member('Tomer Lior'))
    members.append(Member('Tom Elyassi'))
    members.append(Member('Haya Shulman', True))

    context = {'group_members': members}

    return render(request, 'DNSmisconfiguration/index.html', context)


class Member:
    def __init__(self, name, mentor=False):
        self.name = name
        self.mentor = mentor


def address(request):
    return HttpResponse("Enter new URL please")


def csv(request):
    return HttpResponse("Enter new CSV file please")
