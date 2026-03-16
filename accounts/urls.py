from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('seller-register/', views.SellerRegisterView.as_view(), name='seller_register'),

    path("seller-management/", views.SellerManagementView.as_view(), name="seller_management"),
    path("approve/<int:pk>/", views.approve_seller, name="approve_seller"),
    path("block/<int:pk>/", views.block_seller, name="block_seller"),

    path("seller/complaints/", views.SellerComplaintView.as_view(), name="seller_complaints"),

    path("complaint/<int:item_id>/", views.add_complaint, name="add_complaint"),
    path("complaint/<int:pk>/edit/", views.edit_complaint, name="edit_complaint"),
    path(
    "complaint/delete/<int:pk>/",
    views.delete_complaint,
    name="delete_complaint"
    ),

    

    path("complaints/", views.ComplaintManagementView.as_view(), name="complaint_management"),
    path("complaints/<int:seller_id>/", views.ComplaintManagementView.as_view(), name="seller_complaints_admin"),

    path("dashboard/", views.CustomerDashboardView.as_view(), name="customer_dashboard"),
    path("complaints/list/", views.MyComplaintsView.as_view(), name="my_complaints"),
]
