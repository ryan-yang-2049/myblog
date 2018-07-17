from django.shortcuts import render,HttpResponse,redirect

# Create your views here.
from django.http import JsonResponse
from django.contrib import auth

from django.contrib.auth.decorators import login_required
from bs4 import BeautifulSoup
#own class
from blog.utils import validCode
from blog import  models
from blog.utils import MyForms


def login(request):
	if request.method == "POST":
		response = {"user":None,"msg":None}
		user = request.POST.get("user")
		pwd = request.POST.get("pwd")
		valid_code = request.POST.get("valid_code")

		valid_code_str = request.session.get("valid_code_str")
		if valid_code.upper() == valid_code_str.upper():
			user_obj = auth.authenticate(username=user,password=pwd)
			if user_obj:
				auth.login(request,user_obj)
				response["user"] = user_obj.username
			else:
				response["msg"] = "用户名或者密码错误！"
		else:
			response["msg"] = "验证码错误！"
		return JsonResponse(response)
	return render(request, "login.html")

def get_validCode_img(request):
	data = validCode.get_valid_code_img(request)
	return HttpResponse(data)


def register(request):
	if request.is_ajax():
		form = MyForms.UserForm(request.POST)
		print(request.POST)
		response = {"user_info": None, "msg": None}
		if form.is_valid():
			response["user_info"] = form.cleaned_data.get("user")
			user = form.cleaned_data.get("user")
			pwd = form.cleaned_data.get("pwd")
			email = form.cleaned_data.get("email")
			avatar_obj = request.FILES.get("avatar")
			extra = {}

			if avatar_obj:
				extra["avatar"] = avatar_obj
			# 注册成功自动创建博客标题以及站点
			blog_obj = models.Blog.objects.create(title="%s的博客"%user,site_name=user,theme="%s.css"%user)


			models.UserInfo.objects.create_user(username=user,password=pwd,email=email,blog=blog_obj,**extra)


		else:
			response["msg"] = form.errors

		return JsonResponse(response)

	form = MyForms.UserForm()
	return render(request,"register.html",locals())


def logout(request):

	auth.logout(request)
	return redirect("/login/")

def index(request):



	return render(request,"index.html")


@login_required
def cn_backend(request):
	category_info_list = models.Blog.objects.filter(userinfo__username=request.user).values("category__title")
	print(category_info_list)

	return render(request,"backend/base.html",locals())


def add_articles(request):

	if request.method == "POST":
		print(request.POST)
		title = request.POST.get("title")
		content = request.POST.get("content")
		soup = BeautifulSoup(content,"html.parser")
		for tag_info in soup.find_all():
			if tag_info.name == "script":
				tag_info.decompose()

		desc = soup.text[0:100]
		categroy = request.POST.get("categroy")
		tag = request.POST.get("tag")
		print("categroy======",categroy)
		print("tag=====",tag)

	category_info_list = models.Blog.objects.filter(userinfo__username=request.user).values("category__title")
	tag_info_list = models.Blog.objects.filter(userinfo__username=request.user).values("tag__title")
	print(tag_info_list)
	return render(request,"backend/add_article.html",locals())

def add_tag(request):


	return HttpResponse("OK")