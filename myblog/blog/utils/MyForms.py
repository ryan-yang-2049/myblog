# -*- coding: utf-8 -*-

# __title__ = 'MyForms.py'
# __author__ = 'YangYang'
# __mtime__ = '2018.07.17'

from django import forms
from django.forms import  widgets

from blog.models import UserInfo
from django.core.exceptions import ValidationError

wid_01=widgets.TextInput(attrs={"class":"form-control"})
wid_02=widgets.PasswordInput(attrs={"class":"form-control"})
wid_03=widgets.EmailInput(attrs={"class":"form-control"})


class UserForm(forms.Form):
	user=forms.CharField(max_length=32,
	                     error_messages={"required":"该字段不能为空"},
	                     label="用户名", widget=wid_01)
	pwd=forms.CharField(max_length=32,
	                    error_messages={"required": "该字段不能为空"},
	                    label="密码",
	                    widget=wid_02)
	re_pwd=forms.CharField(max_length=32,
	                       error_messages={"required": "该字段不能为空"},
	                       label="确认密码",widget=wid_02)
	email=forms.EmailField(max_length=32,
	                       error_messages={"required": "该字段不能为空"},
	                       label="邮箱",widget=wid_03)


	def clean_user(self):
		user = self.cleaned_data.get("user")
		user_obj = UserInfo.objects.filter(username=user).first()
		if not  user_obj:
			return user
		else:
			raise ValidationError("该用户已注册")


	def clean(self):
		pwd=self.cleaned_data.get("pwd")
		re_pwd=self.cleaned_data.get("re_pwd")

		if pwd and re_pwd:

			if pwd==re_pwd:
				return self.cleaned_data
			else:
				raise ValidationError("两次密码不一致")
		else:
			return self.cleaned_data


