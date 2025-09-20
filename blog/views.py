from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Prefetch
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse

from .forms import blogForm, CommentForm, ReplyForm
from .models import Blog, Comment, Reply


def _is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def _get_comments_queryset(blog):
    replies = Reply.objects.select_related('user').prefetch_related('likes').order_by('datetime_created')
    return blog.comments.filter(is_active=True, parent__isnull=True).select_related('user').prefetch_related('likes',
        Prefetch('reply_set', queryset=replies)
    ).order_by('-datetime_created')


def _render_comments_fragment(request, blog, comments=None):
    if comments is None:
        comments = _get_comments_queryset(blog)
    return render_to_string(
        'blog/partials/comment_thread.html',
        {'blog': blog, 'comments': comments},
        request=request,
    )


def _comments_payload(request, blog):
    comments = list(_get_comments_queryset(blog))
    html = _render_comments_fragment(request, blog, comments=comments)
    return html, len(comments)


def blog_list_view(request):
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', 'newest')

    blogs = Blog.objects.all()

    if search_query:
        blogs = blogs.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

    if sort_by == 'newest':
        blogs = blogs.order_by('-created_at')
    elif sort_by == 'oldest':
        blogs = blogs.order_by('created_at')
    elif sort_by == 'most_commented':
        blogs = blogs.annotate(comment_count=Count('comments')).order_by('-comment_count')
    elif sort_by == 'most_liked':
        blogs = blogs.annotate(like_count=Count('likes')).order_by('-like_count')
    elif sort_by == 'most_viewed':
        blogs = blogs.order_by('-views')

    paginator = Paginator(blogs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for blog in page_obj:
        blog.created_at_jalali = blog.jalali_created

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'blog/blog_list.html', context)


def blog_detail_view(request, pk):
    blog = get_object_or_404(Blog, pk=pk)

    if request.method == 'GET' and not _is_ajax(request):
        blog.views = blog.views + 1
        blog.save(update_fields=['views'])

    comments = list(_get_comments_queryset(blog))
    comment_form = CommentForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            if _is_ajax(request):
                return JsonResponse({'redirect': reverse('login')}, status=403)
            return redirect('login')

        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            parent_id = request.POST.get('parent')
            new_comment = comment_form.save(commit=False)
            new_comment.blog = blog
            new_comment.user = request.user
            if parent_id:
                new_comment.parent = get_object_or_404(Comment, id=parent_id, blog=blog)
            new_comment.save()

            if _is_ajax(request):
                html, count = _comments_payload(request, blog)
                return JsonResponse({'html': html, 'focus': f'comment-{new_comment.id}', 'count': count})

            return redirect(f"{blog.get_absolute_url()}#comment-{new_comment.id}")

        if _is_ajax(request):
            return JsonResponse({'errors': comment_form.errors}, status=400)

    context = {
        'blog': blog,
        'comments': comments,
        'comment_count': len(comments),
        'comment_form': comment_form,
        'is_liked': request.user.is_authenticated and request.user in blog.likes.all(),
    }
    return render(request, 'blog/blog_detail.html', context)


@login_required
def like_blog_view(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.user in blog.likes.all():
        blog.likes.remove(request.user)
        liked = False
    else:
        blog.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'total_likes': blog.total_likes})


@login_required
def blog_create_view(request):
    if request.method == 'POST':
        form = blogForm(request.POST, request.FILES)
        if form.is_valid():
            new_blog = form.save(commit=False)
            new_blog.author = request.user
            new_blog.save()
            if _is_ajax(request):
                return JsonResponse({'success': True, 'url': new_blog.get_absolute_url()})
            return redirect('blog_list')
        elif _is_ajax(request):
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = blogForm()
    return render(request, 'blog/blog_create.html', {'form': form})


@login_required
def blog_update_view(request, pk):
    blog = get_object_or_404(Blog, pk=pk)

    if blog.author != request.user:
        return HttpResponseForbidden('شما اجازه ویرایش این نوشته را ندارید.')

    if request.method == 'POST':
        form = blogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('blog_detail', pk=pk)
    else:
        form = blogForm(instance=blog)

    return render(request, 'blog/blog_update.html', {'form': form, 'blog': blog})


@login_required
def blog_delete_view(request, pk):
    blog = get_object_or_404(Blog, pk=pk)

    if blog.author != request.user:
        return HttpResponseForbidden('شما اجازه حذف این نوشته را ندارید.')

    if request.method == 'POST':
        blog.delete()
        return redirect('blog_list')
    return render(request, 'blog/blog_delete.html', {'blog': blog})


@login_required
def comment_edit_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.user != request.user:
        if _is_ajax(request):
            return JsonResponse({'error': 'forbidden'}, status=403)
        return HttpResponseForbidden('شما اجازه ویرایش این دیدگاه را ندارید.')

    if request.method == 'POST':
        new_text = request.POST.get('text', '').strip()
        if not new_text:
            if _is_ajax(request):
                return JsonResponse({'errors': {'text': ['متن نمی‌تواند خالی باشد.']}}, status=400)
            return redirect(f"{comment.blog.get_absolute_url()}#comment-{comment.id}")
        comment.text = new_text
        comment.save()
        if _is_ajax(request):
            html, count = _comments_payload(request, comment.blog)
            return JsonResponse({'html': html, 'focus': f'comment-{comment.id}', 'count': count})
        return redirect(f"{comment.blog.get_absolute_url()}#comment-{comment.id}")

    if _is_ajax(request):
        return JsonResponse({'error': 'invalid request'}, status=405)
    return redirect(f"{comment.blog.get_absolute_url()}#comment-{comment.id}")

@login_required
def comment_delete_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.user != request.user:
        if _is_ajax(request):
            return JsonResponse({'error': 'forbidden'}, status=403)
        return HttpResponseForbidden('شما اجازه حذف این دیدگاه را ندارید.')

    blog = comment.blog
    if request.method == 'POST':
        comment.delete()
        if _is_ajax(request):
            html, count = _comments_payload(request, blog)
            return JsonResponse({'html': html, 'focus': 'commentsList', 'count': count})
        return redirect(f"{blog.get_absolute_url()}#comments")

    if _is_ajax(request):
        return JsonResponse({'error': 'invalid request'}, status=405)
    return redirect(f"{blog.get_absolute_url()}#comments")

@login_required
def like_comment_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'total_likes': comment.total_likes})


@login_required
def create_reply(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.comment = comment
            reply.user = request.user
            reply.save()
            if _is_ajax(request):
                html, count = _comments_payload(request, comment.blog)
                return JsonResponse({'html': html, 'focus': f'reply-{reply.id}', 'count': count})
            return redirect('blog_detail', comment.blog.id)
        if _is_ajax(request):
            return JsonResponse({'errors': form.errors}, status=400)
    if _is_ajax(request):
        return JsonResponse({'error': 'invalid request'}, status=405)
    return redirect('blog_detail', comment.blog.id)

@login_required
def edit_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    if reply.user != request.user:
        if _is_ajax(request):
            return JsonResponse({'error': 'forbidden'}, status=403)
        return HttpResponseForbidden('شما اجازه انجام این عملیات را ندارید.')

    if request.method == 'POST':
        form = ReplyForm(request.POST, instance=reply)
        if form.is_valid():
            form.save()
            if _is_ajax(request):
                html, count = _comments_payload(request, reply.comment.blog)
                return JsonResponse({'html': html, 'focus': f'reply-{reply.id}', 'count': count})
            return redirect('blog_detail', reply.comment.blog.id)
        if _is_ajax(request):
            return JsonResponse({'errors': form.errors}, status=400)
    if _is_ajax(request):
        return JsonResponse({'error': 'invalid request'}, status=405)
    return redirect('blog_detail', reply.comment.blog.id)

@login_required
def delete_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    if reply.user != request.user:
        if _is_ajax(request):
            return JsonResponse({'error': 'forbidden'}, status=403)
        return HttpResponseForbidden('شما اجازه انجام این عملیات را ندارید.')

    blog = reply.comment.blog
    if request.method == 'POST':
        reply.delete()
        if _is_ajax(request):
            html, count = _comments_payload(request, blog)
            return JsonResponse({'html': html, 'focus': f'comment-{reply.comment_id}', 'count': count})
        return redirect('blog_detail', blog.id)
    if _is_ajax(request):
        return JsonResponse({'error': 'invalid request'}, status=405)
    return redirect('blog_detail', blog.id)

@login_required
def like_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    if request.user in reply.likes.all():
        reply.likes.remove(request.user)
        liked = False
    else:
        reply.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'total_likes': reply.total_likes})












