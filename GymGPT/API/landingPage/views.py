from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request=request,
                  template_name='landing/index.html',
                  context={})

def TermsAndCondition(request):
    return render(request=request,
                  template_name='landing/termsCondition.html',
                  context={})

def aboutUs(request):
    return render(request=request,
                  template_name='landing/aboutus.html',
                  context={})

