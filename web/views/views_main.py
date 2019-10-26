# coding:utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.template.response import TemplateResponse
from django.conf import settings
from django.contrib import messages
# logging
import logging
logger = logging.getLogger("django")


# Create your views here.
@login_required
def main(request):
    msg = "Hello Django Test"
    logger.info(msg)
    messages.info(request, msg)
    output = {
        "msg": msg,
        "user": request.user,
    }
    return TemplateResponse(request, "web/main.html", output)


class Main(TemplateView):
    template_name = "web/main.html"

    def get(self, request, *args, **kwargs):
        msg = "MAIN CLASS GET"
        logger.info(msg)
        messages.info(request, msg)

    def post(self, request, *args, **kwargs):
        msg = "MAIN CLASS POST"
        logger.info(msg)
        messages.info(request, msg)
        return redirect('web:main')

@login_required
def test(request):
    msg = "Hello Django Test"
    logger.info(msg)
    messages.info(request, msg)
    output = {
        "msg": msg,
        "user": request.user,
    }
    return TemplateResponse(request, "web/main.html", output)