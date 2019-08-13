from django.shortcuts import render

# Create your views here.

#跳转到主页面
def index(request):
    return render(request,'index.html')

def RTFdocs(request):
    return render(request, 'RTFdocs.html')
