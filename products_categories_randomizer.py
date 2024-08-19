from store.models import Category, Product

# Create a category
category = Category.objects.create(name='Electronics')

# Create 50 products
for i in range(1, 51):
    Product.objects.create(
        name=f'Product {i}',
        description=f'This is the description for Product {i}. It is a high-quality electronic product.',
        price=round(10.99 + i, 2),
        stock=randint(10, 100),
        category=category,
        image_url='https://via.placeholder.com/150'
    )
