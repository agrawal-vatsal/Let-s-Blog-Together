from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, DeleteView, DetailView, CreateView

from .forms import PostForm, CommentForm, UserForm, loginForm, UserPasswordForm, UserCommentForm
from .models import Post, Comment, BlogUser


# Create your views here.
class AboutView(TemplateView):
    template_name = 'about.html'


class PostListView(ListView):
    model = Post
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(publish_date__isnull=False).order_by('-publish_date')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs);
        authorized = False
        if self.request.user.is_authenticated:
            blogUser = BlogUser.objects.get(user_id=self.object.author.user_id)
            if blogUser.user_id == self.request.user.id:
                authorized = True
        context['authorized'] = authorized
        return context


@login_required
def PostUpdateView(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author.user_id != request.user.id:
        return HttpResponse("You are not authorized for updating a post that is not created by you.")
    form = PostForm(initial={'title': post.title, 'text': post.text}, auto_id=False)
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post.title = form.cleaned_data['title']
            post.text = form.cleaned_data['text']
            post.save()
            return redirect('post_detail', pk=pk)
    return render(request, 'blog/post_form.html', {'form': form})


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    context_object_name = 'form'


    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = BlogUser.objects.get(user_id=self.request.user.id)
        post.save()
        return HttpResponseRedirect(reverse('post_detail', kwargs={'pk': post.pk}))


class PostDeleteView(UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('post_list')

    def post(self, request, *args, **kwargs):
        if self.request.POST.get("confirm_delete"):
            dataset = self.object
            dataset.delete()
            return HttpResponseRedirect(self.success_url)
        elif self.request.POST.get("cancel"):
            return HttpResponseRedirect(self.success_url)
        else:
            return self.get(self, *args, **kwargs)

    def test_func(self):
        self.object = self.get_object()
        return self.object.author.user_id == self.request.user.id


class DraftListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/post_draft_list.html'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(author__user_id=self.request.user.id).filter(publish_date__isnull=True).order_by(
            'create_date')


def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        if request.user.is_authenticated:
            form = UserCommentForm(request.POST)
        else:
            form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            if request.user.is_authenticated:
                blogUser = BlogUser.objects.get(user_id=request.user.id)
                comment.author = blogUser.user.get_full_name()
                if post.author == blogUser:
                    comment.approve()
            comment.save()
            return redirect('post_detail', pk=pk)
    else:
        if request.user.is_authenticated:
            form = UserCommentForm()
        else:
            form = CommentForm()
    return render(request, 'blog/comment_form.html', {'form': form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if check_authority(request, comment.post):
        comment.approve()
        return redirect('post_detail', pk=comment.post.pk)
    else:
        return HttpResponse("You are not authorized to approve a comment")


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    if check_authority(request, comment.post):
        comment.delete()
        return redirect('post_detail', pk=post_pk)
    else:
        return HttpResponse("You are not authorized to remove a comment")


@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if check_authority(request, post):
        post.publish()
        return redirect('post_detail', pk=pk)
    else:
        return HttpResponse("You are not authorized to publish this post")


def signUp(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        pform = UserPasswordForm(request.POST)
        if form.is_valid() and pform.is_valid():
            user = form.save(commit=False)
            password = pform.cleaned_data['password1']
            user.set_password(raw_password=password)
            user.save()
            blogUser = BlogUser()
            blogUser.user = user
            blogUser.save()
            username = form.cleaned_data.get('username')
            loginUser = authenticate(username=username, password=password)
            if loginUser:
                login(request, loginUser)
                return HttpResponseRedirect(reverse('post_list'))

    else:
        form = UserForm()
        pform = UserPasswordForm()
    return render(request, 'registration/signup.html', {'form': form, 'pform': pform})


def logIn(request):
    if request.method == "POST":
        form = loginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect(reverse('post_list'))
            else:
                return render(request, 'registration/login.html', {
                    'form': form,
                    'invalid': True
                })
    else:
        form = loginForm()
    return render(request, 'registration/login.html', {
        'form': form,
        'invalid': False
    })


@login_required
def logOut(request):
    logout(request)
    return HttpResponseRedirect(reverse('post_list'))


def check_authority(request, post):
    return post.author.user_id == request.user.id


class userView(ListView, LoginRequiredMixin):
    template_name = 'registration/user_page.html'
    login_url = '/login/'
    model = Post
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(author__user_id=self.request.user.id).filter(publish_date__isnull=False).order_by(
            '-publish_date')
