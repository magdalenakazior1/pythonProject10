from django.contrib import admin
from .models import Profile, Category, Product, Order, OrderItem, Review, Payment, Shipping, Discount, ProductImage, Log

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Payment)
admin.site.register(Shipping)
admin.site.register(Discount)
admin.site.register(ProductImage)
admin.site.register(Log)
admin.site.register(Profile)