import threading

from django import forms
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import admin

from backend_api import models
from aaiss_backend import settings


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


class MailerThread(threading.Thread):
    def __init__(self, subject, targets, html_body):
        self.subject = subject
        self.targets = targets
        self.HTML_body = html_body
        threading.Thread.__init__(self)

    def run(self):
        html_message = self.HTML_body
        plain_message = strip_tags(html_message)
        print('STARTING TO SEND MAILS')
        print(self.targets)
        send_mail(subject=self.subject, message=plain_message, from_email=settings.EMAIL_HOST_USER,
                  recipient_list=self.targets, html_message=html_message,
                  fail_silently=False)
        print("SENDING DONE")


class MailerForm(forms.ModelForm):
    HTML_body = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = models.Mailer
        fields = '__all__'


class MailerAdmin(admin.ModelAdmin):
    model = models.Mailer
    form = MailerForm

    def execute_mailer(self, request, obj):
        for mailer in obj:
            if mailer.target_mode == 1:
                targets = models.User.objects.all()
                mails = []
                for target in targets:
                    mails.append(target.account.email)
                MailerThread(mailer.subject, mails, mailer.HTML_body).start()
            elif mailer.target_mode == 2:
                mails = []
                for workshop in mailer.workshop_selection:
                    for user in models.User.objects.all():
                        if workshop in user.registered_workshops:
                            if __name__ == '__main__':
                                mails.append(user.account.email)
                MailerThread(mailer.subject, mails, mailer.HTML_body).start()
            elif mailer.target_mode == 3:
                mails = []
                for user in models.User.objects.all():
                    if user.registered_for_presentations:
                        mails.append(user.account.email)
                MailerThread(mailer.subject, mails, mailer.HTML_body).start()
            elif mailer.target_mode == 4:
                targets = mailer.user_selection
                mails = []
                for target in targets:
                    mails.append(target.account.email)
                MailerThread(mailer.subject, mails, mailer.HTML_body).start()

    execute_mailer.short_description = 'Send selected mails'
    execute_mailer.allow_tags = True
    actions = ['execute_mailer']


admin.site.register(models.Mailer, MailerAdmin)