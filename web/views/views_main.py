from django.template.response import TemplateResponse

# Create your views here.


def main(request):
    output = {
        "message": "Hello Django"
    }
    return TemplateResponse(request, "web/main.html", output)


def test(request):
    output = {
        "message": "Hello Django Test"
    }
    return TemplateResponse(request, "web/main.html", output)