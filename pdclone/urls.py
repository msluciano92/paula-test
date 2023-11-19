from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.posts, name='posts'),
    path('create_posts/', views.create_posts,  name='create_posts'),
    path('communities/<str:filter>', views.communities),
    path('create_community/', views.create_community),
    path('login/', views.login),
    path('logout/', views.logout_view),
    path('u/<str:username>/<str:filter>/<str:orden>', views.user_view),
    path('c/<str:id>/<str:show>/<str:order>', views.community),
    path('edit_profile/', views.edit_profile),
    path('subscribe/<str:id>', views.subscribe),
    path('unsubscribe/<str:id>', views.unsubscribe),
    path('post/<int:post_id>/', views.post, name='single_post'),
    path('comments/', views.comments, name='comments'),
    path('comment/<int:comment_id>/upvote_comment', views.upvote_comment, name='upvote_comment'),
    path('comment/<int:comment_id>/downvote_comment', views.downvote_comment, name='downvote_comment'),
    path('post/<int:post_id>/upvote/<str:page>', views.upvote, name='upvote'),
    path('post/<int:post_id>/downvote/<str:page>', views.downvote, name='downvote'),
    path('post/<int:post_id>/create_comment/', views.create_comment, name='create_comment'),
    path('savecomment/<int:id>', views.saveComment, name='savecomment'),
    path('savepost/<int:id>', views.savePost, name='savepost'),
    path('comment/<int:post_id>/<int:comment_id>/reply', views.reply_comment, name='reply_comment'),
    path('comment/<int:post_id>/<int:comment_id>/edit', views.edit_comment, name='edit_comment'),
    path('comment/<int:post_id>/<int:comment_id>/delete', views.delete_comment, name='delete_comment'),
    path('editar_post/<int:post_id>', views.editar_post, name='editar_post'),
    path('post/order_post/<str:orden>/', views.order_post, name = 'order_post'),
    path('post/order_coment/<str:orden>/', views.order_coment, name = 'order_coment'),
    path('post_subscrit/<str:filter>', views.post_subscrit, name = 'post_subscrit'),
    path('coment_suscrit/<str:filter>', views.coment_suscrit, name = 'coment_suscrit'),
    path('eliminar_post/<int:post_id>/', views.eliminar_post, name='eliminar_post'),
    path('confirmar_eliminar_post/<int:post_id>/<int:page>/', views.confirmar_eliminar_post, name='confirmar_eliminar_post'),
    path('single_post/order_singlepost/<str:orden>/<int:post_id>/', views.order_singlepost, name = 'order_singlepost'),
    path('post/search_post/<str:search>/', views.order_post, name = 'search_post'), 

]

