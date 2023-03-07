from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.views import View
from django.utils.decorators import method_decorator

#import view
from rango.bing_search import run_query

#importing models
from rango.models import Category
from rango.models import Page

#import forms
from rango.forms import CategoryForm,PageForm, UserForm, UserProfileForm

def index(request):
	# Query the database for a list of All categories currently stored.
	# Order the categories by the number of likes in descending order.
	# Retrieve the top 5 only -- or all if less than 5.
	# Place the list in our context_dict dictionary (with our boldmessage!).
	# that will be passed to the template engine.
	category_list = Category.objects.order_by('-likes')[:5]
	#retirve top 5 most viewed pages
	page_list = Page.objects.order_by('-views')[:5]

	context_dict ={}
	context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
	context_dict['categories'] = category_list
	context_dict['pages'] = page_list
	
	visitor_cookie_handler(request)
	# context_dict['visits'] = request.session['visits']

	#obtain our response object early so we can add cookie information
	response = render(request, 'rango/index.html', context = context_dict)
	# Call the helper function to handle the cookies
	return response



class AboutView(View):
	def get(self, request):
		context_dict ={}
		visitor_cookie_handler(request)
		context_dict['visits'] = request.session['visits']

		return render(request,'rango/about.html',context=context_dict)

class ShowCategoryView(View):
	context_dict ={}
	query= None
		
	@method_decorator(login_required)
	def post(self, request, category_name_slug):
		self.query = request.POST.get('query')
		if self.query:
			pages = Page.objects.filter(category__slug=category_name_slug, title__icontains=self.query)
			self.context_dict['result_list'] = pages
			self.context_dict['query'] = self.query
		
		return render(request, 'rango/category.html', self.context_dict)

	def get(self, request, category_name_slug):
		try:
			# can we find a category name slug wiht the given name? If we can't, the .get() method raises a DoesNotExist exception.
			# The .get() method returns one model instance or raises an exception.
			category = Category.objects.get(slug=category_name_slug)
			# Retrieve all of the associated pages.
			# The filter() will return a list of page objects or an empty list.	
			pages = Page.objects.filter(category=category)
			ordered_pages = pages.order_by('-views')
			# Adds our results list to the template context under names pages.
			self.context_dict['pages'] = ordered_pages
			# We also add the category objects from the database to the context dictionary.We'll use this in the template to verify  category exists
			self.context_dict['category'] = category
		except Category.DoesNotExist:
			# We get here if we didgn't find the specified category. Don't do anything
			# the template will display the "no category" message for us.
			self.context_dict['category'] = None
			self.context_dict['pages'] = None

		#Go render the response and return it to the client.
		return render(request, 'rango/category.html', self.context_dict)


class AddCategoryView(View):
	@method_decorator(login_required)
	def get(self, request):
		form = CategoryForm()
		return render(request, 'rango/add_category.html',{'form':form})

	@method_decorator(login_required)
	def post(self, request):
		form = CategoryForm(request.POST)

		if form.is_valid():
			form.save(commit=True)
			return redirect(reverse('rango:index'))
		else:
			print(form.errors)
		
		return render(request, 'rango/add_category.html', {'form':form})
		


class AddPageView(View):
	@method_decorator(login_required)	
	def get(self,request, category_name_slug):
		try:
			category = Category.objects.get(slug=category_name_slug)
		except Category.DoesNotExist:
			category = None
   		# You cannot add a page to a Category that does not exist...
		if category is None:
			return redirect('/rango/')
		
		form = PageForm()
		context_dict ={'form':form, 'category':category}
		return render(request, 'rango/add_page.html', context=context_dict)

	@method_decorator(login_required)
	def post(self,request,category_name_slug):
		try:
			category = Category.objects.get(slug=category_name_slug)
		except Category.DoesNotExist:
			category = None
   		# You cannot add a page to a Category that does not exist...
		if category is None:
			return redirect('/rango/')
		
		form = PageForm(request.POST)

		if form.is_valid():
			if category:
				page = form.save(commit=False)
				page.category = category
				page.views = 0
				page.save()
				
				return redirect(reverse('rango:show_category',
										kwargs={'category_name_slug':
												category_name_slug}))
		else:
			print(form.errors)


		context_dict = {'form': form, 'category': category}
		return render(request, 'rango/add_page.html', context=context_dict)	
		

# @login_required
# def restricted(request):
# 	return render(request, 'rango/restricted.html')


#Use the login_required() decorator to ensure only those logged in can  access the view
# @login_required
# def user_logout(request):
# 	# Since we know the user is logged in, we can now just log them out.
# 	logout(request)
# 	# Take the user back to the homepage.
# 	return redirect(reverse('rango:index'))


# A helper method
def get_server_side_cookie(request, cookie, default_val= None):
	val = request.session.get(cookie)
	if not val:
		val = default_val
	return val

#a helper function to calculate the number of visits a user makes to a page.
def visitor_cookie_handler(request):
	# Get the number of visits to the site.
	# We use the COOKIES.get() function to obtain the visits cookie.
	# If the cookie exists, the value returned is casted to an integer.
	# If the cookie doesn't exist, then the default value of 1 is used.
	visits = int(get_server_side_cookie(request,'visits', '1'))
	last_visit_cookie = get_server_side_cookie(request,'last_visit', str(datetime.now()))
	last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')


	#if it's more than a day since the last visit..
	if(datetime.now() - last_visit_time).days > 0:
		visits = visits + 1
		#Update the last visit cookie now that we have update the count.
		request.session['last_visit'] = str(datetime.now())
	else:
		# set the last visits cookie
		request.session['last_visit'] = last_visit_cookie
	
	#Update/set the visits cookie
	request.session['visits'] = visits

#this helper function takes the request and response objects - because we want to be able to access the incoming cookies
#from the request and add or update the cookies in the response.


# def search(request):
# 	#result_list = []
# 	context_dict ={}
# 	context_dict['result_list'] =[]
# 	print("Checking what is in request",request)
# 	if request.method == 'POST':
# 		query = request.POST['query'].strip()
# 		print("Query", query)
# 		if query:
# 			#Run our Bing function to get the results list!
# 			# result_list  = run_query(query)
# 			context_dict['result_list'] = run_query(query)
# 			context_dict['query'] = query
# 			print(query)

# 	return render(request, 'rango/search.html',context_dict)




class GotoURLView(View):
	def get(self, request):
		try:
			page_id = request.GET.get('page_id')
			page = get_object_or_404(Page, id=page_id)
			page.views +=1
			page.save()
			return redirect(page.url)
		except Page.DoesNotExist:
			return redirect(reverse('rango:index'))


class RegisterProfileView(View):
	@method_decorator(login_required)
	def get(self, request):
		form = UserProfileForm()
		context_dict = {'form':form}
		return render(request, 'rango/profile_registration.html', context_dict)

	@method_decorator(login_required)
	def post(self, request):
		form = UserProfileForm(request.POST, request.FILES)

		if form.is_valid():
			user_profile = form.save(commit=False)
			user_profile.user = request.user
			user_profile.save()

			return redirect(reverse('rango:index'))
		else:
			print(form.errors)

		context_dict = {'form': form}
		return render(request, 'rango/profile_registration.html', context_dict)
