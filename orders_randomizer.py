from store.models import Order, OrderItem, Product
from random import randint
from django.utils import timezone

# Fetch all products
products = list(Product.objects.all())

# Create orders for each user
for user in User.objects.all():
    order = Order.objects.create(
        user=user,
        address=user.profile.address,
        city=user.profile.city,
        state=user.profile.state,
        zipcode=user.profile.zipcode,
        country=user.profile.country,
        phone=user.profile.phone_number,
        payment_method='credit_card',
        delivery_date=timezone.now().date(),
        status='pending',
        total=0  # This will be calculated after adding items
    )

    # Add random products to the order
    for _ in range(randint(1, 5)):
        product = products[randint(0, len(products) - 1)]
        quantity = randint(1, 3)
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )
        order.total += order_item.get_cost()

    order.save()
