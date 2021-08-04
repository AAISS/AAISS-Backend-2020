import threading

from django import forms
from django.core.mail import EmailMessage
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
        if selected_model == models.Workshop:
            list_display = ('__str__', 'capacity', 'cost', 'has_project', 'level', 'no_of_participants','year')
            readonly_fields = ('participants',)
        elif selected_model == models.Presentation:
            list_display = ('__str__', 'level', 'no_of_participants','year')
            readonly_fields = ('participants',)
    return Admin


admin.site.register(models.Account)


class UserAdmin(admin.ModelAdmin):
    list_display = ('account',)

admin.site.register(models.Staff)
admin.site.register(models.User, UserAdmin)
admin.site.register(models.FieldOfInterest)


class TeacherAdminForm(forms.ModelForm):
    bio = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = models.Presenter
        fields = '__all__'


class TeacherAdmin(admin.ModelAdmin):
    form = TeacherAdminForm
    list_display = ('__str__', 'order',)


admin.site.register(models.Teacher, TeacherAdmin)
admin.site.register(models.Workshop, desc_creator(models.Workshop))


class PresenterAdminForm(forms.ModelForm):
    bio = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = models.Presenter
        fields = '__all__'


class PresenterAdmin(admin.ModelAdmin):
    form = PresenterAdminForm
    list_display = ('__str__', 'order',)


admin.site.register(models.Presenter, PresenterAdmin)

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
        print('STARTING TO SEND MAILS')
        print(self.targets)

        email = EmailMessage(
            subject=self.subject,
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            bcc=self.targets,
            reply_to=(settings.EMAIL_HOST_USER,)
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)
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
                for workshop in mailer.workshop_selection.all():
                    for user in models.User.objects.all():
                        if workshop in user.registered_workshops.all():
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
                targets = mailer.user_selection.all()
                mails = []
                for target in targets:
                    mails.append(target.account.email)
                MailerThread(mailer.subject, mails, mailer.HTML_body).start()

    execute_mailer.short_description = 'Send selected mails'
    execute_mailer.allow_tags = True
    actions = ['execute_mailer']


admin.site.register(models.Mailer, MailerAdmin)


class PaymentAdmin(admin.ModelAdmin):
    rdfields = []
    for field in models.Payment._meta.get_fields():
        rdfields.append(field.__str__().split('.')[-1])

    readonly_fields = rdfields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    class Meta:
        model = models.Payment
        fields = '__all__'


admin.site.register(models.Payment, PaymentAdmin)
