from django.shortcuts import render,HttpResponse,redirect

# Create your views here.
from django.contrib import auth

from django.contrib.auth.decorators import login_required
from bs4 import BeautifulSoup
# 事务
from django.db import transaction
# 发送邮件
from django.core.mail import send_mail
from myblog import settings
import threading
import json
from  django.db.models  import  F
from django.http import JsonResponse
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
	return render(request,"index.html",locals())

def cate_view(request,categroy_id):
	article_list = models.Article.objects.filter(category=categroy_id).all()
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
	return render(request,"home_site.html",locals())

@login_required
def cn_backend(request):
	category_info_list = models.Blog.objects.filter(userinfo__username=request.user).values("category__title")
	article_list = models.Article.objects.filter(user=request.user)
	return render(request,"backend/backend.html",locals())

@login_required
def add_articles(request):
	blog_id = models.Blog.objects.filter(userinfo__username=request.user).first()
	if request.method == "POST":
		title = request.POST.get("title")
		content = request.POST.get("content")
		soup = BeautifulSoup(content,"html.parser")
		for tag_info in soup.find_all():
			if tag_info.name == "script":
				tag_info.decompose()   # 删除这个标签
		desc = soup.text[0:100]
		categroy = request.POST.get("categroy")
		tag = request.POST.get("tag")
		article_id = article_id_num()
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
	tag_info_list = models.Blog.objects.filter(title=blog_id).values("tag__title")
	return render(request,"backend/add_article.html",locals())

@login_required
def edit_article(request,article_nid):
	blog_id = models.Blog.objects.filter(userinfo__username=request.user).first()
	if request.method == "POST":
		title = request.POST.get("title")
		content = request.POST.get("content")
		soup = BeautifulSoup(content,"html.parser")
		for tag_info in soup.find_all():
			if tag_info.name == "script":
				tag_info.decompose()   # 删除这个标签
		desc = soup.text[0:100]

		categroy = request.POST.get("categroy")
		tag = request.POST.get("tag")
		if  categroy:
			categroy_obj = models.Category.objects.filter(blog_id=blog_id,title=categroy).first()
			article_obj = models.Article.objects.filter(nid=article_nid).update(title=title, content=str(soup),desc=desc,category=categroy_obj)
			if tag:
				tag_obj = models.Tag.objects.filter(title=tag, blog_id=blog_id).first()
				models.Article2Tag.objects.filter(article_id=article_nid).update(article=article_obj, tag=tag_obj)
		else:
			article_obj = models.Article.objects.filter(nid=article_nid).update(title=title, content=str(soup),desc=desc)
			if tag:
				tag_obj = models.Tag.objects.filter(title=tag, blog_id=blog_id).first()
				models.Article2Tag.objects.filter(article_id=article_nid).create(article=article_obj, tag=tag_obj)
		return redirect('/cn_backend/')

	article_detail_content = models.Article.objects.filter(nid=article_nid).first()
	old_title = article_detail_content.title
	old_content = article_detail_content.content
	old_category = article_detail_content.category.nid
	old_tag = models.Article2Tag.objects.filter(article_id=article_nid)
	if old_tag:
		old_tag = old_tag.values("tag_id").first()["tag_id"]
	else:
		old_tag = None
	category_info_list = models.Blog.objects.filter(title=blog_id).values("category__title","category__nid")
	tag_info_list = models.Blog.objects.filter(title=blog_id).values("tag__title","tag__nid")
	return render(request,"backend/edit_article.html",locals())

def delete_article(request):
	if request.is_ajax():
		article_nid = request.POST.get("article_nid")
		#删除文章表的数据
		ret1 = models.Article.objects.filter(nid=article_nid).delete()
		# 删除article2tag的数据
		ret2 = models.Article2Tag.objects.filter(article_id=article_nid).delete()
	return HttpResponse("ok")
# 文章图片上传
import os
def upload(request):
	img = request.FILES.get("upload_img")
	path = os.path.join(settings.MEDIA_ROOT,"add_article_img",request.user.username)
	filename = os.path.join(path,img.name)
	if not os.path.exists(path):
		os.makedirs(path)
	with open(filename,"wb") as  f:
		for line in img:
			f.write(line)
	#用于创建文章界面图片展示
	response = {
		"error":0,
		"url":"%s/add_article_img/%s/%s"%(settings.MEDIA_URL,request.user.username,img.name)
	}
	return JsonResponse(response)
def add_attribute(request):
	if request.method == "POST":
		categroy_name = request.POST.get("categroy_name")
		tag_name = request.POST.get("tag_name")
		blog = models.Blog.objects.filter(userinfo__username=request.user).first()
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

def article_detail(request,username,article_id):
	'''
	此时的article_id 只是 Article表中的一个字段，并不是主键值
	:param request:
	:param username:
	:param article_id:
	:return:
	'''
	user_obj = models.UserInfo.objects.filter(username=username).first()
	blog_obj = user_obj.blog
	article_obj = models.Article.objects.filter(user=user_obj,article_id=article_id).first()
	comment_list = models.Comment.objects.filter(article_id=article_obj.pk)
	return  render(request,"article_detail.html",locals())

# 点赞视图
def digg(request):
	article_nid = request.POST.get("article_nid")
	is_up = request.POST.get("is_up")  # 拿到的是一个true或者false的字符串，如果此时直接传入到数据库，那此时都为真，因此，要反序列化为布尔值
	is_up = json.loads(request.POST.get("is_up"))
	#点赞人，即当前登陆人
	user_id  = request.user.pk
	#判断用户是否对某篇文章进行过点赞或者踩
	done_obj = models.ArticleUpDown.objects.filter(user_id=user_id,article_id=article_nid).first()
	response = {"state":True,"handled":None}
	if not done_obj:
		aud = models.ArticleUpDown.objects.create(user_id=user_id,article_id=article_nid,is_up=is_up)
		queryset = models.Article.objects.filter(pk=article_nid)
		if is_up:
			queryset.update(up_count = F("up_count")+1 )
		else:
			queryset.update(down_count=F("down_count") + 1)
	else:
		response["state"] = False
		response["handled"] = done_obj.is_up
	return JsonResponse(response)

def comment(request):
	article_nid = request.POST.get("article_nid")
	pid = request.POST.get("pid")
	content = request.POST.get("content")
	user_id = request.user.pk
	article_obj = models.Article.objects.filter(pk=article_nid).first()
	# 事务
	with transaction.atomic():
		comment_obj = models.Comment.objects.create(user_id=user_id,article_id=article_nid,parent_comment_id=pid,content=content)
		models.Article.objects.filter(pk=article_nid).update(comment_count=F("comment_count")+1)
	response = {}
	response["create_time"] = comment_obj.create_time.strftime("%Y-%m-%d")  #进行json序列化的时候不能对对象进行序列化,所以要先格式化
	response["content"] = comment_obj.content
	response["username"] = request.user.username
	# 发送邮件
	t=threading.Thread(target=send_mail,args=("您的文章 %s 新增了一条评论内容"%article_obj.title,
	                                          content,
	                                          settings.EMAIL_HOST_USER,
	                                          settings.EMAIL_RECV_USER))
	t.start()
	return JsonResponse(response)
def get_comment_tree(request):
	article_nid = request.GET.get("article_nid")
	ret = list(models.Comment.objects.filter(article_id=article_nid).order_by('pk').values("pk","user__username","content","create_time","parent_comment_id",))
	# ret = list(models.Comment.objects.filter(article_id=article_nid).order_by('pk').values())
	# 里面是一个queryset的对象，要进行序列化，必须先实例化对象
	return JsonResponse(ret,safe=False)