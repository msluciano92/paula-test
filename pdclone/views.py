from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import logout
from .models import Post, Community, CustomUser, Comment
from .forms import CommunityForm, PostForm, CustomUserForm, CommentForm, EditPostForm
from django.db.models import Count
from django.urls import reverse
from django.contrib import messages

# Create your views here.
def posts(request):
    queryset = request.GET.get("buscar")
    if queryset: posts = Post.objects.filter(title__contains= queryset)
    else:
        posts = Post.objects.all()
    context = {'posts':posts}
    return render(request, 'posts.html', context)

def create_posts(request):
    comunidad = None
    if request.method == 'POST':
        form = PostForm(request.POST)
        if not request.user.is_authenticated: return redirect('posts')
        if form.is_valid():
            # Crear la publicación si el formulario es válido
            if (request.user.is_authenticated):
                author = CustomUser.objects.get(username=request.user.username)
            try:
                comunidad = Community.objects.get(name=form.cleaned_data['community'])
            except Community.DoesNotExist:
                messages.error(request, 'La comunidad no existe. Por favor, introduce una comunidad válida.')
                
            if comunidad:    
                post = Post(
                    title=form.cleaned_data['title'],
                    body=form.cleaned_data['body'],
                    url=form.cleaned_data['url'],
                    author_id=author.id,
                    community=comunidad
                )
                post.save()
                return redirect('posts')
        else: return redirect('posts')    
    else:
        form = PostForm()  # Crear una instancia del formulario en caso de GET request

    return render(request, 'create_posts.html', {'form': form})

def communities(request, filter):
    allCommunities = Community.objects.all()
    if (request.user.is_authenticated):
        user = CustomUser.objects.get(username=request.user.username)
        communitiesSubscribed = user.community_set.all()

        if (filter == 'local'): communities = allCommunities
        elif (filter == 'suscrito'): communities = communitiesSubscribed
        else: return redirect('/')

        communities_subscribed = []
        for c in communities:
            posts = c.posts.all()
            numComments = 0
            for p in posts:
                numComments += p.comments.all().count()
            if c in communitiesSubscribed: communities_subscribed.append([c, True, posts.count(), numComments])
            else: communities_subscribed.append([c, False, posts.count(), numComments])  
        return render(request, 'communities.html', {'communities':communities_subscribed,
                                                    'local':(filter == 'local')})
    else:

        if (filter == 'local'): communities = allCommunities
        elif (filter == 'suscrito'): communities = Community.objects.none()
        else: return redirect('/')

        communities_subscribed = []
        for c in communities:
            posts = c.posts.all()
            numComments = 0
            for p in posts:
                numComments += p.comments.all().count()
            communities_subscribed.append([c, False, posts.count(), numComments])
        return render(request, 'communities.html', {'communities':communities_subscribed,
                                                    'local':(filter == 'local')})

def create_community(request):
    if (request.method == 'GET'):
        form = CommunityForm()
        return render(request, 'create_community.html', {'form': form})
    elif (request.method == 'POST'):
        
        form = CommunityForm(request.POST, request.FILES)
        if (form.is_valid()):
            form.save()
        return redirect('/communities/local')
    else:
        return render(request, 'create_community.html')

def login(request):
    if (request.user.is_authenticated):
        try:
            user = CustomUser.objects.get(username=request.user.username)
        except CustomUser.DoesNotExist:
            user = CustomUser(username=request.user.username, name=request.user.username)
            user.save()

    return redirect("/")

def logout_view(request):
    logout(request)
    return redirect("/")

def user_view(request, username, filter, orden):
    try:
        showPosts = True
        showComments = True
        showSaved = False
        if (filter == 'resumen'): 
            showPosts = showComments = True
            showSaved = False
        elif (filter == 'comentarios'): 
            showPosts = False
            showComments = True
            showSaved = False
        elif (filter == 'publicaciones'):
            showPosts = True
            showComments = False
            showSaved = False
        elif (filter == 'guardados'):
            if (not (request.user.is_authenticated and request.user.username == username)): return redirect('/')
            showPosts = showComments = False
            showSaved = True        
        else: return redirect('/')

        user = CustomUser.objects.get(username=username)
        posts = user.posts.all().order_by(orden)
        savedPosts = user.post_set.all().order_by(orden)
        if(orden == '-points'): orden = '-upvotes'
        comments = user.comments.all().order_by(orden)
        savedComments = user.comment_set.all().order_by(orden)
        return render(request, 'user.html', 
                      {'userL':user,
                       'showBanner':user.banner is not None and user.banner,
                       'showAvatar':user.avatar is not None and user.avatar,
                       'showName':(user.name != ' ' and user.name != ''),
                       'showDescription':(user.description != ' ' and user.description != ''),
                       'isUser': (request.user.is_authenticated and request.user.username == username),
                       'showPosts': showPosts,
                       'showComments': showComments,
                       'showSaved': showSaved,
                       'posts': posts,
                       'comments': comments,
                       'savedC': savedComments,
                       'savedP': savedPosts})
    except CustomUser.DoesNotExist:
        return redirect('/')  

def edit_profile(request):
    if (request.user.is_authenticated):
        try:
            user = CustomUser.objects.get(username=request.user.username)
        except CustomUser.DoesNotExist:
            return redirect('/') 
        
        if (request.method == 'GET'):
            form = CustomUserForm(instance=user)
            return render(request, 'edit_profile.html', {'user': user, 'form':form, 'isUser': request.user.is_authenticated})   
        elif (request.method == 'POST'):
            form = CustomUserForm(request.POST, request.FILES, instance=user)
            if (form.is_valid()):
                form.save()
            return redirect('/u/${request.user.username}/resumen/-created_date')
        else: return redirect('/')    
    else:
        return redirect('/')  

def subscribe(request, id):
    if (request.user.is_authenticated):
        community = Community.objects.get(id=id)
        user = CustomUser.objects.get(username=request.user.username)
        community.subscribers.add(user)
    return redirect("/communities/suscrito")

def unsubscribe(request, id):
    if (request.user.is_authenticated):
        community = Community.objects.get(id=id)
        user = CustomUser.objects.get(username=request.user.username)
        community.subscribers.remove(user)
    return redirect("/communities/suscrito")

def post(request, post_id):
    post = Post.objects.get(id=post_id)
    comments = post.comments.all()
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        print(form)
        if form.is_valid():
            # Crear la publicación si el formulario es válido
            if (request.user.is_authenticated):
                author = CustomUser.objects.get(username=request.user.username)
        
            comment = Comment(
                body=form.cleaned_data['body'],
                author_id=author.id,
                post=post_id
            )
            comment.save()
            print(comment)
    else:
        form = CommentForm()  # Crear una instancia del formulario en caso de GET request

    return render(request, 'single_post.html', {'post': post, 'comments': comments, "form": CommentForm()})

def community(request, id, show, order):
    try:
        community = Community.objects.get(id=id)
        posts = community.posts.all()
        data = Comment.objects.none()
        showPosts = False
        if (show == 'posts'): 
            showPosts = True
            data = posts
        elif (show == 'comments'): 
            showPosts = False
            for p in posts:
                comments = p.comments.all()
                data = data | comments

        else: return redirect('/communities/local')
        data = data.order_by(order)
        return render(request, 'community.html', {'community':community,
                                                'showBanner':community.banner is not None and community.banner,
                                                'showAvatar':community.avatar is not None and community.avatar,
                                                'showName':(community.name is not None and community.name != ''),
                                                'showPosts':showPosts,
                                                'data':data,
                                                'order': order})
    except Community.DoesNotExist: 
        return redirect('/communities/local')

def comments(request):
    queryset = request.GET.get("buscar")
    if queryset: comments = Comment.objects.filter(body__contains=queryset)
    else:
        comments = Comment.objects.all()
    return render(request, 'comments.html', {'comments': comments})

def upvote_comment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    comment.upvotes += 1
    comment.finalvotes += 1
    comment.save()

    return redirect('comments')

def downvote_comment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    comment.downvotes += 1
    comment.finalvotes -= 1
    comment.save()
    return redirect('comments')

def upvote(request, post_id, page):
    post = Post.objects.get(id=post_id)
    post.points += 1
    post.save()
    if (page == 'single_post'):
        return redirect('single_post', post_id=post_id)
    else:
        return redirect('posts')

def downvote(request, post_id, page):
    post = Post.objects.get(id=post_id)
    post.points -= 1
    post.save()
    if (page == 'single_post'):
        return redirect('single_post', post_id=post_id)
    else:
        return redirect('posts')    

def order_post(request, orden):
    if (orden == 'coments'):
        posts_con_comentarios = Post.objects.annotate(comentarios_count=Count('comments'))
        posts = posts_con_comentarios.order_by('-comentarios_count')
    else:
        posts = Post.objects.all().order_by(orden)
    context = {'posts':posts}
    return render(request, 'posts.html', context)

def order_coment(request,orden):
    comments = Comment.objects.all().order_by(orden)
    return render(request, 'comments.html', {'comments': comments})

def post_subscrit(request, filter):
    allCommunities = Community.objects.all()
    if (request.user.is_authenticated):
        user = CustomUser.objects.get(username=request.user.username)
        communitiesSubscribed = user.community_set.all()

        if (filter == 'local'): communities = allCommunities
        elif (filter == 'suscrito'): communities = communitiesSubscribed
        else: return redirect('/')
        posts = []
        communities_subscribed = []
        for c in communities:
            if c in communitiesSubscribed: 
                posts += list(c.posts.all())
                #communities_subscribed.append([c, True, posts.count(), numComments])
            #else: communities_subscribed.append([c, False, posts.count(), numComments])  
        #return render(request, 'communities.html', {'communities':communities_subscribed,
         #                                           'local':(filter == 'local')})
    else:
        posts = Post.objects.all()
        #return render(request, 'communities.html', {'communities':communities_subscribed,
         #                                           'local':(filter == 'local')})
    context = {'posts':posts}
    return render(request, 'posts.html', context)

def coment_suscrit(request, filter):
    allCommunities = Community.objects.all()
    if (request.user.is_authenticated):
        user = CustomUser.objects.get(username=request.user.username)
        communitiesSubscribed = user.community_set.all()

        if (filter == 'local'): communities = allCommunities
        elif (filter == 'suscrito'): communities = communitiesSubscribed
        else: return redirect('/')
        comments = []
        communities_subscribed = []
        for c in communities:
            if c in communitiesSubscribed: 
                posts = c.posts.all()
                for p in posts:
                    comments += list(p.comments.all())
                #communities_subscribed.append([c, True, posts.count(), numComments])
            #else: communities_subscribed.append([c, False, posts.count(), numComments])  
        #return render(request, 'communities.html', {'communities':communities_subscribed,
         #                                           'local':(filter == 'local')})
    else:
        comments = Comment.objects.all()
        #return render(request, 'communities.html', {'communities':communities_subscribed,
         #                                           'local':(filter == 'local')})
    return render(request, 'comments.html', {'comments': comments})

def order_post(request, orden):
    if (orden == 'coments'):
        posts_con_comentarios = Post.objects.annotate(comentarios_count=Count('comments'))
        posts = posts_con_comentarios.order_by('-comentarios_count')
    else:
        posts = Post.objects.all().order_by(orden)
    context = {'posts':posts}
    return render(request, 'posts.html', context)

def order_coment(request,orden):
    comments = Comment.objects.all().order_by(orden)
    return render(request, 'comments.html', {'comments': comments})

def post_subscrit(request, filter):
    allCommunities = Community.objects.all()
    if (request.user.is_authenticated):
        user = CustomUser.objects.get(username=request.user.username)
        communitiesSubscribed = user.community_set.all()

        if (filter == 'local'): communities = allCommunities
        elif (filter == 'suscrito'): communities = communitiesSubscribed
        else: return redirect('/')
        posts = []
        communities_subscribed = []
        for c in communities:
            if c in communitiesSubscribed: 
                posts += list(c.posts.all())
                #communities_subscribed.append([c, True, posts.count(), numComments])
            #else: communities_subscribed.append([c, False, posts.count(), numComments])  
        #return render(request, 'communities.html', {'communities':communities_subscribed,
         #                                           'local':(filter == 'local')})
    else:
        posts = Post.objects.all()
        #return render(request, 'communities.html', {'communities':communities_subscribed,
         #                                           'local':(filter == 'local')})
    context = {'posts':posts}
    return render(request, 'posts.html', context)

def coment_suscrit(request, filter):
    allCommunities = Community.objects.all()
    if (request.user.is_authenticated):
        user = CustomUser.objects.get(username=request.user.username)
        communitiesSubscribed = user.community_set.all()

        if (filter == 'local'): communities = allCommunities
        elif (filter == 'suscrito'): communities = communitiesSubscribed
        else: return redirect('/')
        comments = []
        communities_subscribed = []
        for c in communities:
            if c in communitiesSubscribed: 
                posts = c.posts.all()
                for p in posts:
                    comments += list(p.comments.all())
                #communities_subscribed.append([c, True, posts.count(), numComments])
            #else: communities_subscribed.append([c, False, posts.count(), numComments])  
        #return render(request, 'communities.html', {'communities':communities_subscribed,
         #                                           'local':(filter == 'local')})
    else:
        comments = Comment.objects.all()
        #return render(request, 'communities.html', {'communities':communities_subscribed,
         #                                           'local':(filter == 'local')})
    return render(request, 'comments.html', {'comments': comments})

def create_comment(request, post_id):
    if request.method == 'POST':
        if not request.user.is_authenticated: return redirect('posts')
        form = CommentForm(request.POST)
        if form.is_valid():
            # Crear la publicación si el formulario es válido
            if (request.user.is_authenticated):
                author = CustomUser.objects.get(username=request.user.username)

            post_parent = Post.objects.get(id=post_id)
            comment = Comment(
                body=form.cleaned_data['body'],
                author_id=author.id,
                post=post_parent
            )
            comment.save()
    else:
        form = CommentForm()  # Crear una instancia del formulario en caso de GET request

    return redirect('single_post', post_id=post_id)

def saveComment(request, id):
    if (request.user.is_authenticated):
        loggedUser = CustomUser.objects.get(username = request.user.username)
        comment = Comment.objects.get(id=id)
        users = comment.savedBy.all()
        hasSaved = False

        for u in users:
            if u.username == request.user.username: hasSaved = True

        if hasSaved: comment.savedBy.remove(loggedUser)
        else: comment.savedBy.add(loggedUser)    
    return redirect(request.GET.get('next'))

def savePost(request, id):
    if (request.user.is_authenticated):
        loggedUser = CustomUser.objects.get(username = request.user.username)
        post = Post.objects.get(id=id)
        users = post.savedBy.all()
        hasSaved = False

        for u in users:
            if u.username == request.user.username: hasSaved = True

        if hasSaved: post.savedBy.remove(loggedUser)
        else: post.savedBy.add(loggedUser)    
    return redirect(request.GET.get('next'))

def reply_comment(request, post_id, comment_id):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            if (request.user.is_authenticated):
                author = CustomUser.objects.get(username=request.user.username)

            post_parent = Post.objects.get(id=post_id)
            comment_parent = Comment.objects.get(id=comment_id)
            comment = Comment(
                body=form.cleaned_data['body'],
                author_id=author.id,
                post=post_parent,
                parent_comment=comment_parent
            )
            comment.save()
            return redirect('comments')
    else:
        form = CommentForm()  # Crear una instancia del formulario en caso de GET request
        context = Comment.objects.get(id=comment_id)

    return render(request, 'reply_comments.html', {'form': form, 'comment': context})

def edit_comment(request, post_id, comment_id):
    context = Comment.objects.get(id=comment_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment.objects.get(id=comment_id)
            if (request.user.is_authenticated and request.user.username==comment.author.username):
                comment.body=form.cleaned_data['body']
                comment.save()
            return redirect('comments')
    else:
        form = CommentForm()

    return render(request, 'edit_comment.html', {'form': form, 'comment': context})

def delete_comment(request, post_id, comment_id):
    comment = Comment.objects.get(id=comment_id)
    if (request.user.is_authenticated and request.user.username==comment.author.username):
        comment.delete()
    return redirect('comments')

def editar_post(request, post_id):
    post = Post.objects.get(id=post_id)  # Obtener el post existente
    if request.method == 'POST':
        form = EditPostForm(request.POST)
        if form.is_valid():
            post.url = form.cleaned_data['url']
            post.title = form.cleaned_data['title']
            post.body = form.cleaned_data['body']
            comunityName = form.cleaned_data['community']
            community = Community.objects.get(name=comunityName)    
            post.community = community
            post.save()
            return redirect('posts')
    else:
        form = EditPostForm(initial={
            'url': post.url,
            'title': post.title,
            'body': post.body,
            'community': post.community.name,
        })

    return render(request, 'editar_post.html', {'form': form, 'post': post})

def confirmar_eliminar_post(request, post_id, page):
    post = Post.objects.get(id=post_id)
    if page == 1:
        return render(request, 'confirmar_eliminar_post_posts.html', {'post': post})
    else:
        return render(request, 'confirmar_eliminar_post_post.html', {'post': post})
    
    

def eliminar_post(request, post_id):
    post = Post.objects.get(id=post_id)
    post.delete()
    return redirect(reverse('posts'))

def order_singlepost(request, orden, post_id):
    post = Post.objects.get(id=post_id)
    comments = post.comments.all().order_by(orden)
    return redirect('single_post', post_id=post_id,)
    #return render(request, 'single_post.html', {'post': post, 'comments': comments, "form": CommentForm()})


def search_post(request, search):
    posts = Post.objects.all().filter(title = search)
    context = {'posts':posts}
    return render(request, 'posts.html', context)