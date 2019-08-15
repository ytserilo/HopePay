from django.urls import path
from .views import *

urlpatterns = [
    path('edit_product/<int:id>/', EditProduct.as_view()),
    path('products/', Products.as_view()),
    path('add_product/', AddProduct.as_view()),
    path('about_product/<int:id>/', AboutProduct.as_view()),
    path('confirm_rate/<int:id>/', ConfirmRate.as_view()),
    path('delete_product/<int:id>/', DeleteProduct.as_view()),
    path('change_status/<int:id>/', ActivateOrDeactive.as_view()),

]
