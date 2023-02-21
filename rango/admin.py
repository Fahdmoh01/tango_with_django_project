from django.contrib import admin
from rango.models import Category, Page, UserProfile


#helps to automatic slugify names
class CategoryAdmin(admin.ModelAdmin):
	prepopulated_fields={'slug':('name',)}

#This helps displays tile, category and url in the admin panel
class PageAdmin(admin.ModelAdmin):
	list_display=('title','category', 'url')

# Register your models here.
admin.site.register(Category, CategoryAdmin)
#This registers and displays tile, category and url in the admin panel
admin.site.register(Page,PageAdmin)
#Register model with admin interface
admin.site.register(UserProfile)