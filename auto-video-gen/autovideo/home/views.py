from django.shortcuts import render
from django.http import HttpResponse

from .utils import gpt

# Create your views here.
def index(request):
    script = gpt.generate_script("black people", 3, "english")
    return render(request, "home/index.html", {"response": script})

def test(req):
    return HttpResponse("test")