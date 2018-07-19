from django.shortcuts import render,HttpResponse,redirect

# Create your views here.
from django.http import JsonResponse
from django.contrib import auth

from django.contrib.auth.decorators import login_required
from bs4 import BeautifulSoup
from django.db.models import Count
from django.db.models.functions import TruncMonth

#own class
from blog.utils import validCode
from blog import  models
from blog.utils import MyForms
from blog.utils.random_article_id import  article_id_num

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

	article_list = models.Article.objects.all()
	category_list = models.Category.objects.all()
	#根据用户文章数进行排序
	user_article_info = models.UserInfo.objects.values("pk").annotate(c=Count("article__nid")).values("username","c").order_by("-c")
	# print(user_article_info)

	return render(request,"index.html",locals())

def home_site(request,username,**kwargs):
	'''
	个人站点首页
	:param request:
	:return:
	'''
	user_obj = models.UserInfo.objects.filter(username=username).first()

	if not user_obj:
		return render(request,"not_found.html")

	blog_obj = user_obj.blog    # type <class 'blog.models.Blog'>
	article_list = models.Article.objects.filter(user=user_obj) # 等价于  article_list = user_obj.article_set.all()


	if kwargs:
		condition = kwargs.get("condition")
		param = kwargs.get("param")
		if condition == "category":
			article_list = article_list.filter(category__title=param)
		elif condition == "tag":
			article_list = article_list.filter(tags__title=param)
		else:
			year,month = param.split("-")
			article_list = article_list.filter(create_time__year=year,create_time__month=month)




	category_list = models.Category.objects.filter(blog=blog_obj).values("pk").annotate(c=Count("article__title")).values("title","c")

	# 查询当前站点的每一个标签名称以及对应的文章数
	tag_list = models.Tag.objects.filter(blog=blog_obj).values("pk").annotate(c=Count("article__title")).values("title","c")


	# 查询当前站点每一个年月的名称以及对应的文章数
	# ret = models.Article.objects.extra(select={"is_recent":"create_time">"2018-01-01"}).values("title","is_recent")
	# date_list = models.Article.objects.filter(user=user_obj).extra(select={"y_m_date":"date_format(create_time,'%%Y-%%m')"}).values("y_m_date").annotate(c=Count("pk")).values("y_m_date","c")
	date_list = models.Article.objects.annotate(month=TruncMonth('create_time')).values('month').annotate(c=Count('pk')).values('month','c')



	return render(request,"home_site.html",locals())




@login_required
def cn_backend(request):
	category_info_list = models.Blog.objects.filter(userinfo__username=request.user).values("category__title")
	print(category_info_list)
	article_list = models.Article.objects.filter(user=request.user)
	print(article_list)

	return render(request,"backend/backend.html",locals())


def add_articles(request):
	blog_id = models.Blog.objects.filter(userinfo__username=request.user).first()
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
		article_id = article_id_num()
		print(article_id)

		if  categroy:
			categroy_obj = models.Category.objects.filter(blog_id=blog_id,title=categroy).first()
			article_obj = models.Article.objects.create(title=title, content=str(soup), user=request.user, desc=desc,article_id=article_id,category=categroy_obj)
			if tag:
				tag_obj = models.Tag.objects.filter(title=tag, blog_id=blog_id).first()
				models.Article2Tag.objects.create(article=article_obj, tag=tag_obj)
		else:
			article_obj = models.Article.objects.create(title=title, content=str(soup), user=request.user, desc=desc,article_id=article_id)
			if tag:
				tag_obj = models.Tag.objects.filter(title=tag, blog_id=blog_id).first()
				models.Article2Tag.objects.create(article=article_obj, tag=tag_obj)

		return redirect('/cn_backend/')

	category_info_list = models.Blog.objects.filter(title=blog_id).values("category__title")
	# category_info_list = models.Blog.objects.filter(userinfo__username=request.user).values("category__title")
	tag_info_list = models.Blog.objects.filter(title=blog_id).values("tag__title")
	# tag_info_list = models.Blog.objects.filter(userinfo__username=request.user).values("tag__title")

	return render(request,"backend/add_article.html",locals())



def add_attribute(request):

	if request.method == "POST":
		print(request.POST)
		categroy_name = request.POST.get("categroy_name")
		tag_name = request.POST.get("tag_name")
		blog = models.Blog.objects.filter(userinfo__username=request.user).first()
		print("blog",blog)
		if categroy_name:
			categroy_exist = models.Category.objects.filter(title=categroy_name).first()
			if not categroy_exist:
				models.Category.objects.create(title=categroy_name,blog=blog)

		if tag_name:
			tag_exist = models.Tag.objects.filter(title=tag_name).first()
			if not tag_exist:
				models.Tag.objects.create(title=tag_name,blog=blog)

	category_info_list = models.Blog.objects.filter(userinfo__username=request.user).values("category__title")
	tag_info_list = models.Blog.objects.filter(userinfo__username=request.user).values("tag__title")
	return render(request, "backend/add_attribute.html",locals())