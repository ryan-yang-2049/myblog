"""myblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from django.views.static import serve
from blog import views
from myblog import settings
urlpatterns = [
    path('admin/', admin.site.urls),
	re_path('^$', views.index),
	path('index/', views.index),
    path('login/', views.login),
    path('register/', views.register),
    path('logout/',views.logout ),
    path('get_validCode_img/',views.get_validCode_img),


	# 首页分类标签
	re_path('cate/(?P<categroy_id>.*)/$',views.cate_view),

	# 后台管理界面
	path("cn_backend/",views.cn_backend),
	path("cn_backend/add_articles/",views.add_articles),
	path("cn_backend/add_attribute/",views.add_attribute),


	#media 配置 头像
	re_path(r'media/(?P<path>.*)$',serve,{"document_root":settings.MEDIA_ROOT}),


	# 个人站点配置
	re_path(r'^(?P<username>\w+)/$',views.home_site),
	re_path(r'^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/$',views.home_site),

	# 文章详情页
	re_path(r'^(?P<username>\w+)/articles/(?P<article_id>.*)$',views.article_detail)
]
