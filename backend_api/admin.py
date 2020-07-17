from django import forms
from django.contrib import admin

from backend_api import models


def desc_creator(selected_model):
    class AdminForm(forms.ModelForm):
        desc = forms.CharField(widget=forms.Textarea)

        class Meta:
            model = selected_model
            fields = '__all__'

    class Admin(admin.ModelAdmin):
        form = AdminForm

    return Admin


admin.site.register(models.Account)
admin.site.register(models.User)
admin.site.register(models.FieldOfInterest)
admin.site.register(models.Teacher, desc_creator(models.Teacher))
admin.site.register(models.Workshop, desc_creator(models.Workshop))
admin.site.register(models.Presenter, desc_creator(models.Presenter))
admin.site.register(models.Presentation, desc_creator(models.Presentation))
admin.site.register(models.Misc, desc_creator(models.Misc))
