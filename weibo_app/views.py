from django.shortcuts import render

# Create your views here.
def index(request):
    #request.POST
    #request.GET
    #return HttpResponse("YOU now entered our data connector. PLEASE CLOSE this page..........")
    return render(request, 'home.html')