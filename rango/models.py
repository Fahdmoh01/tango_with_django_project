from django.db import models
from django.template.defaultfilters import slugify

# Create your models here.
class Category(models.Model):
	name = models.CharField(max_length=128, unique=True)
	NAME_MAX_LENGTH = 128
	views= models.IntegerField(default=0)
	likes = models.IntegerField(default=0)
	
	#adding a slug field to slugify URLS.
	#always add the unique attribute after following creating your Database and populating it.
	#else there will be migration issues.
	slug = models.SlugField(unique=True) 


	def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		super(Category, self).save(*args, **kwargs)


	#Meta class just allows for correct plural form of model names in Django admin panel
	class Meta:
		verbose_name_plural = 'Categories'

	def __str__(self):
		return self.name


class Page(models.Model):
	TITLE_MAX_LENGTH =128
	URL_MAX_LENGTH = 200

	category = models.ForeignKey(Category, on_delete=models.CASCADE)
	title = models.CharField(max_length=TITLE_MAX_LENGTH)
	url = models.URLField()
	views = models.IntegerField(default=0)

	#Meta class just allows for correct plural form of model names in Django admin panel
	class Meta:
		verbose_name_plural ='Pages'

	def __str__(self):
		return self.title
	
	