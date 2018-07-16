from django.shortcuts import render

# Create your views here.

def login(request):
	if request.method == "POST":
		response = {"user":None,"msg":None}
		user = request.POST.get("user")
		pwd = request.POST.get("pwd")

		#



	return render(request,"login.html")



def index(request):


	return render(request,"index.html")