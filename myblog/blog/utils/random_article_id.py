# -*- coding: utf-8 -*-

# __title__ = 'random_article_id.py'
# __author__ = 'YangYang'
# __mtime__ = '2018.07.19'


import random

def article_id_num():
	article_id_num = ""
	for i in range(7):
		random_num = str(random.randint(1,9)+random.randint(0,9))
		article_id_num += random_num

	article_id_num = article_id_num[0:7]+".html"
	return str(article_id_num)
