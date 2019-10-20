# coding:utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.conf import settings
from django.contrib import messages
# logging
import logging
logger = logging.getLogger("django")


# Create your views here.
@login_required
def main(request):
    output = {
        "msg": "Hello Django"
    }
    return TemplateResponse(request, "web/main.html", output)


@login_required
def test(request):
    msg = "Hello Django Test"
    logger.info(msg)
    messages.info(request, msg)
    output = {
        "msg": msg
    }
    return TemplateResponse(request, "web/main.html", output)