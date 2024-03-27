from django.shortcuts import render, redirect
from .models import Profile, Post, Relationship
from .forms import UserRegisterForm, PostForm, ProfileUpdateForm, UserUpdateForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from project.serializer import ProfileSerializer
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

@login_required
def home(request):
	posts = Post.objects.all()
	if request.method == 'POST':
		form = PostForm(request.POST)
		if form.is_valid():
			post = form.save(commit=False)
			post.user = request.user
			post.save()
			return redirect('home')
	else:
		form = PostForm()

	context = {'posts':posts, 'form' : form }
	return render(request, 'twitter/newsfeed.html', context)

def register(request):
	if request.method == 'POST':
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			new_user = form.save(commit=False)
			new_user.save()
			Profile.objects.create(user=new_user)
			return redirect('home')
	else:
		form = UserRegisterForm()

	context = {'form': form}
	return render(request, 'twitter/register.html', context)


def delete(request, post_id):
	post = Post.objects.get(id=post_id)
	post.delete()
	return redirect('home')


def profile(request, username):
	user = User.objects.get(username=username)
	posts = user.posts.all()
	context = {'user':user, 'posts':posts}
	return render(request, 'twitter/profile.html', context)

@login_required
def editar(request):
	if request.method == 'POST':
		u_form = UserUpdateForm(data=request.POST, instance=request.user)
		p_form = ProfileUpdateForm(data=request.POST, files=request.FILES, instance=request.user.profile)

		if u_form.is_valid() and p_form.is_valid():
			u_form.save()
			p_form.save()
	else:
		u_form = UserUpdateForm(instance=request.user)
		p_form = ProfileUpdateForm()

	context = {'u_form':u_form, 'p_form':p_form}
	return render(request, 'twitter/editar.html', context)

@login_required
def follow(request, username):
	current_user = request.user
	to_user = User.objects.get(username=username)
	to_user_id = to_user
	rel = Relationship(from_user=current_user, to_user=to_user_id)
	rel.save()
	return redirect('home')

@login_required
def unfollow(request, username):
	current_user = request.user
	to_user = User.objects.get(username=username)
	to_user_id = to_user.id
	rel = Relationship.objects.get(from_user=current_user.id, to_user=to_user_id)
	rel.delete()
	return redirect('home')


class ProfileViewSet(viewsets.ModelViewSet):
	queryset = Profile.objects.all()
	serializer_class = ProfileSerializer
	authentication_classes = [BasicAuthentication]
	permission_classes = [IsAuthenticated]




def ProfileLike(request, pk):
    post = get_object_or_404(Profile, id=request.POST.get('Profile_id'))
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    return HttpResponseRedirect(reverse('Profile-detail', args=[str(pk)]))

class ProfileDetailView(viewsets.ModelViewSet):
    model = Profile
    # template_name = MainApp/Profile_detail.html
    # context_object_name = 'object'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        likes_connected = get_object_or_404(Profile, id=self.kwargs['pk'])
        liked = False
        if likes_connected.likes.filter(id=self.request.user.id).exists():
            liked = True
        data['number_of_likes'] = likes_connected.number_of_likes()
        data['post_is_liked'] = liked
        return data