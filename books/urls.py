from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.book_list, name='book_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('book/<slug:slug>/', views.book_detail, name='book_detail'),
    path('book/<slug:slug>/borrow/', views.borrow_book, name='borrow_book'),
    path('book/<slug:slug>/rent/', views.rent_book, name='rent_book'),
    path('book/<slug:slug>/purchase/', views.purchase_book, name='purchase_book'),
    path('book/<slug:slug>/return/', views.return_book, name='return_book'),
    path('book/<slug:slug>/review/', views.add_review, name='add_review'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<slug:slug>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<slug:slug>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
] 