# coding: utf-8


from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, resolve_url
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _

from .forms import (CustomPasswordResetForm, CustomSetPasswordForm,
                    CustomUserProfileForm)


# User
def signup(request, *args, **kwargs):
    return render(request, "website/page.html", kwargs)


@csrf_protect
def password_reset(request, is_admin_site=False,
                   template_name="website/reset.html",
                   subject_template_name="website/mail/password-reset-subject.txt",
                   text_email_template_name="website/mail/password-reset.txt",
                   html_email_template_name="website/mail/password-reset.html",
                   password_reset_form=CustomPasswordResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect=None,
                   from_email=None,
                   current_app=None,
                   extra_context=None):

    if post_reset_redirect is None:
        post_reset_redirect = reverse('password-reset-done')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)

    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': text_email_template_name,
                'html_email_template_name': html_email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
            }
            if is_admin_site:
                opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)
            return redirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form': form,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context, current_app=current_app)


@csrf_protect
@login_required
def profile(request, *args, **kwargs):
    feedback = {}
    if request.method == 'POST':
        form = CustomUserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            feedback['form'] = _(u'Succesfully updated profile')
            form.save()

        # skip password_form if the user does not try to change it
        if not (request.POST['new_password1'] or request.POST['new_password2']):
            data = None
        else:
            data = request.POST
        password_form = CustomSetPasswordForm(request.user, data)
        if password_form.is_valid():
            feedback['password_form'] = _(u'Succesfully updated password')
            password_form.save()
    else:
        form = CustomUserProfileForm(instance=request.user)
        password_form = CustomSetPasswordForm(user=request.user)

    context = {'form': form,
               'password_form': password_form,
               'feedback': feedback}
    return render(request, 'app/profile.html', context)
