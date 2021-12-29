from django.contrib.auth.models import User
from django.db import transaction as tx
from django import forms

# Third Party
from taggit.forms import TagWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    HTML,
    ButtonHolder,
    Column,
    Fieldset,
    Layout,
    Row,
    Submit,
)


from .models import Article,ArticleComment
from .choices import ArticleStatus



class ArticleCreateForm(forms.ModelForm):
	title = forms.CharField(label="",required=False,max_length=70,widget=forms.TextInput(attrs={
		"placeholder":"New Article title here...","autofocus":True,"spellcheck":"true","data-emoji-picker":"true",
		}))
	content = forms.CharField(label="",required=True,max_length=450,help_text="<b class='counter-val'>450</b> characters.",widget=forms.Textarea(attrs={
		"placeholder":"Write your topic content here ....","rows":10,"cols":5,"spellcheck":"true","data-emoji-picker":"true",
		}))
	image = forms.ImageField(label="",required=False)

	tags = forms.CharField(label="",required=True,widget=forms.TextInput(attrs={
		"placeholder":"tags ..."
		}))
	class Meta:
		model = Article
		fields = ["title","content","image","tags"]

	field_order = ['title', 'image'] # the rest should follow

	def __init__(self,board,request,*args,**kwargs):
		self.request = request
		self.board = board
		super(self.__class__,self).__init__(*args,**kwargs)

	# clean - image : validate type,size,dimensions


	def clean_title(self):
		"""
		- clean_title :
		drafted articles with or without title can be saved.
		published articles without title won't be saved, error message
		"""
		title = self.cleaned_data['title']
		is_title = len(title) or False
		is_publishing = self.get_article_status() == ArticleStatus.P

		if not is_title and is_publishing:
			raise forms.ValidationError("Title can't be blank for published articles.")
		return self.cleaned_data["title"]


	def clean_tags(self):
		import re
		MAX_TAGS_ALLOWED = 3
		tags = self.cleaned_data.get("tags")

		# regex: clean each tag; No char for '%$#^&*()_=-!~' just alpha
		# missing `,` but spaces add `,`
		if len(tags.split(',')) > MAX_TAGS_ALLOWED:
			raise forms.ValidationError("TagList's exceeded the maximum of {0}".format(MAX_TAGS_ALLOWED))
		return self.cleaned_data["tags"]


	def clean_content(self):

		content = self.cleaned_data.get('content')

		required_len = int(self.fields['content'].max_length / 2) - 120 # 105

		if len(content) < required_len:
			raise forms.ValidationError('Minimum length of content is {len_}'.format(len_=required_len))
		return self.cleaned_data['content']


	def get_article_status(self):
		# use Js to set status `Depending on button clicked`
		request = self.request
		status = None
		if "publish-article" in request.POST:
			status = ArticleStatus.P
		elif "draft-article" in request.POST:
			status = ArticleStatus.D
		else:
			status = ArticleStatus.P #default-incases where it fails
		return status


	@tx.atomic
	def save(self,commit=True,*args,**kwargs):

		article = super().save(commit=False)
		status = self.get_article_status()
		article.created_by = self.request.user
		article.created_by_username = article.created_by.username
		is_publishing = False

		tags = self.cleaned_data['tags']
		if not status == ArticleStatus.D:
			from django.utils import timezone
			article.published_date = timezone.now()
			is_publishing = True
		article.status = status
		article.board = self.board

		if commit:
			article.save()
			for tag in self.cleaned_data["tags"].split(","):
				_tag = tag.lower().strip()
				article.tags.add(_tag)
		return article,is_publishing




class ArticleEditForm(forms.ModelForm):
	title = forms.CharField(label="",required=False,max_length=120,widget=forms.TextInput(attrs={
		"placeholder":"New Article title here...","autofocus":True,"spellcheck":"true","data-emoji-picker":"true",
		}))
	content = forms.CharField(label="",required=True,max_length=450,widget=forms.Textarea(attrs={
		"placeholder":"Write your topic content here ....","rows":10,"cols":5,"spellcheck":"true","data-emoji-picker":"true",
		}))
	image = forms.ImageField(label="",required=False)


	class Meta:
		model = Article
		fields = ["title","content","image","tags"]
		widgets = {
		'tags':TagWidget(attrs={"placeholder":"tags ..."}),
		}

	field_order = ['title', 'image']

	def __init__(self,board,request,*args,**kwargs):
		self.request = request
		self.board = board
		super(self.__class__,self).__init__(*args,**kwargs)


	def clean_title(self):
		"""
		- clean_title :
		drafted articles with or without title can be saved.
		published articles without title won't be saved, error message
		"""
		title = self.cleaned_data['title']
		is_title = len(title) or False
		if not is_title:
			raise forms.ValidationError("Title can't be blank.")
		return self.cleaned_data["title"]


	def clean_content(self):

		content = self.cleaned_data.get('content')

		required_len = int(self.fields['content'].max_length / 2) - 150 # 75

		if len(content) < required_len:
			raise forms.ValidationError('Minimum length of content is {len_}'.format(len_=required_len))
		return self.cleaned_data['content']


	def get_article_status(self):
		# use Js to set status `Depending on button clicked`
		request = self.request
		status = None
		if "publish-article" in request.POST:
			status = ArticleStatus.P
		elif "draft-article" in request.POST:
			status = ArticleStatus.D
		else:
			status = ArticleStatus.P #default-incases where it fails
		return status


	@tx.atomic
	def save(self,commit=True,*args,**kwargs):
		article = super().save(commit=False)
		status = self.get_article_status()
		article.created_by = self.request.user
		article.created_by_username = article.created_by.username
		is_publishing = False

		tags = self.cleaned_data['tags']
		if not status == ArticleStatus.D:
			from django.utils import timezone
			article.published_date = timezone.now()
			is_publishing = True
		article.status = status
		article.board = self.board
		if commit:
			article.save()
			# TODO : tag's edit not saving
			for tag in self.cleaned_data["tags"]:
				_tag = tag.lower().strip()
				article.tags.add(_tag)
		return article,is_publishing




class CommentForm(forms.ModelForm):

	content = forms.CharField(label="",required=True,max_length=450,widget=forms.Textarea(attrs={
		"placeholder":"Add a comment","rows":3,"cols":8,"data-emoji-picker":"true",
		}))

	class Meta:
		model = ArticleComment
		fields = ["content"]

	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)



class CommentEditForm(forms.ModelForm):

	content = forms.CharField(label="",required=True,max_length=450,widget=forms.Textarea(attrs={
		"placeholder":"Add a comment","rows":3,"cols":8,"data-emoji-picker":"true",
		}))


	class Meta:
		model = ArticleComment
		fields = ["content"]

	def __init__(self,comment,*args,**kwargs):
		self.comment = comment
		super().__init__(*args,**kwargs)
		self.fields["content"].initial = self.comment.content



class CommentReplyEditForm(forms.ModelForm):

	content = forms.CharField(label="",required=True,max_length=450,widget=forms.Textarea(attrs={
		"placeholder":"Add a comment","rows":3,"cols":8,"data-emoji-picker":"true",
		}))


	class Meta:
		model = ArticleComment
		fields = ["content"]

	def __init__(self,comment,*args,**kwargs):
		self.comment = comment
		super().__init__(*args,**kwargs)
		self.fields["content"].initial = self.comment.content
