from django.contrib import admin

from backend_api import models

admin.site.register(models.Account)
admin.site.register(models.User)
admin.site.register(models.FieldOfInterest)
admin.site.register(models.Teacher)
admin.site.register(models.Workshop)
admin.site.register(models.Presenter)
admin.site.register(models.Presentation)
