# -*- coding: utf-8 -*-

# __title__ = 'my_classification_tags.py'
# __author__ = 'YangYang'
# __mtime__ = '2018.07.20'

from django.db.models import Count
from django import  template
from django.db.models.functions import TruncMonth
from blog import models


register = template.Library()

# 把数据和样式结合成一个标签函数，调用这个标签函数，相当于把这个渲染完的html就传递过去了
@register.inclusion_tag("classification.html")
def get_classification_style(username):
	user_obj = models.UserInfo.objects.filter(username=username).first()
	blog_obj = user_obj.blog
	category_list = models.Category.objects.filter(blog=blog_obj).values("pk").annotate(
		c=Count("article__title")).values("title", "c")

	tag_list = models.Tag.objects.filter(blog=blog_obj).values("pk").annotate(c=Count("article__title")).values("title",
	                                                                                                            "c")
	date_list = models.Article.objects.filter(user=user_obj).annotate(month=TruncMonth('create_time')).values('month').annotate(
		c=Count('pk')).values('month', 'c').order_by("-month")

	return {"user_obj":user_obj,"blog":blog_obj,"category_list":category_list,"tag_list":tag_list,"date_list":date_list}
	# return locals()




@register.inclusion_tag("categroy_list.html")
def get_categroy_data():
	category_list = models.Category.objects.all()
	return {"category_list":category_list}


def get_tag_data():
	pass

@register.inclusion_tag("date_list.html")
def get_date_data():

	best_new_article = models.Article.objects.values('title','article_id').order_by("-create_time")[:5]


	print(best_new_article)
	return {"best_new_article":best_new_article}





