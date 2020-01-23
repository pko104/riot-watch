from django.contrib import admin
from .models import Tutorial

# Register your models here.

class TutorialAdmin(admin.ModelAdmin):
	fields = [	"tutorial_published",
				"tutorial_title",
				"tutorial_content",]


admin.site.register(Tutorial, TutorialAdmin)
