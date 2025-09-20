# Use Login Required in blog Store Project

## Update settings.py File in config folder
```bash
# Email Config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = "fake.poulstar@gmail.com"
EMAIL_HOST_PASSWORD = "ftgtgsssfukhiyik"
```

## blog app
- ### Update views.py file
```bash
from django.shortcuts import render, get_object_or_404, redirect
from . import models
from .forms import blogForm, CommentForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

def blog_list_view(request):
    blog = models.blog.objects.all()
    paginator = Paginator(blog, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'blog/blog_list.html', context)

def blog_detail_view(request, pk):
    blog = get_object_or_404(models.blog, pk=pk)
    comments = blog.comments.all()
    if request.method=="POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.blog = blog
            new_comment.user = request.user
            new_comment.save()
            comment_form = CommentForm()
    else:
        comment_form = CommentForm()
    context = {
        'blog': blog,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'blog/blog_detail.html', context)

@login_required
def blog_create_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method=='POST':
        form = blogForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('blog_list')
    else:
        form = blogForm()
    return render(request, 'blog/blog_create.html', { 'form': form } )

@login_required
def blog_update_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('blog_list')
    blog = get_object_or_404(models.blog, pk=pk)
    if request.method == 'GET':
        form = blogForm(instance=blog)
        return render(request, 'blog/blog_update.html', { 'form': form , 'blog': blog})
    elif request.method == 'POST':
        form = blogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('blog_list')

@login_required
def blog_delete_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    blog = get_object_or_404(models.blog, pk=pk)
    if request.method=='POST':
        blog.delete()
        return redirect('blog_list')
    return render(request, 'blog/blog_delete.html', { 'blog': blog })  
```


## Run Your App
- ### In Windows
```bash
py manage.py runserver
```
- ### In MacOS
```bash
python manage.py runserver
```
- ### In Linux
```bash
python3 manage.py runserver
```
