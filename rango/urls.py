from django.urls import path
from rango import views
from rango.views import AboutView,AddCategoryView,ShowCategoryView,AddPageView,GotoURLView,RegisterProfileView

app_name = 'rango'

urlpatterns = [
	path('',views.index, name='index'),
	path('about/', AboutView.as_view(), name='about'),
	path('category/<slug:category_name_slug>/', ShowCategoryView.as_view(), name='show_category'),
	path('add_category/', AddCategoryView.as_view(), name='add_category'),
	path('category/<slug:category_name_slug>/add_page/', AddPageView.as_view(), name='add_page'),
    # path('search/',views.search, name='search'),
    path('goto/',GotoURLView.as_view(), name='goto'),
    path('register_profile/', RegisterProfileView.as_view(), name='register_profile'),
]