from django.shortcuts import render
from .utils import *

class Products(ProductsMixin):
    pass

class AddProduct(AddProductMixin):
    pass

class AboutProduct(AboutProductMixin):
    pass

class ConfirmRate(ConfirmRateMixin):
    pass

class DeleteProduct(DeleteProductMixin):
    pass

class ActivateOrDeactive(ActivateOrDeactiveMixin):
    pass

class EditProduct(UpdateProductMixin):
    pass
