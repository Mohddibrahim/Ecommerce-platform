from django.urls import path
from . import views

urlpatterns = [

    # Seller Dashboard
    path('seller/dashboard/', views.SellerProductListView.as_view(), name='seller_products'),
    path('seller/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('seller/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('seller/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    # Public Products
    path('', views.ProductListView.as_view(), name='product_list'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    
    
    path("review/<int:item_id>/", views.add_review, name="add_review"),


   path('delete_review/<int:pk>/',views.delete_review,name='delete_review'),
   path('edit_review/<int:pk>/',views.edit_review,name='edit_review'),
   
   
   
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/add/", views.CategoryCreateView.as_view(), name="category_add"),
    
    
    path("categories/<int:pk>/edit/", views.CategoryEditView.as_view(), name="category_edit"),
path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),

path("seller/<int:pk>/request-promotion/", views.request_promotion, name="request_promotion"),



  path("reviews/", views.MyReviewsView.as_view(), name="my_reviews"),


path("promotion-management/", views.PromotionManagementView.as_view(), name="promotion_management"),


path("promotion/<int:pk>/approve/", views.approve_promotion, name="approve_promotion"),
path("promotion/<int:pk>/reject/", views.reject_promotion, name="reject_promotion"),


]