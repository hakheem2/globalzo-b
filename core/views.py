# core/views.py

from django.shortcuts import render


def home(request):
   return render(request, "pages/home.html")

def about(request):
   return render(request, "pages/about.html")

def services(request):
   return render(request, "pages/services.html")

def contact(request):
   return render(request, "pages/contact.html")

def faq(request):
   return render(request, "pages/faq.html")

def quote(request):
   return render(request, "pages/quote.html")

def track(request):
   return render(request, "pages/track.html")