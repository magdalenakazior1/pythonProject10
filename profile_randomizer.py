from django.contrib.auth import get_user_model
from store.models import Profile

User = get_user_model()

# Create 48 users
for i in range(1, 49):
    user = User.objects.create_user(
        username=f'user{i}',
        email=f'user{i}@example.com',
        password='password123',
        first_name=f'FirstName{i}',
        last_name=f'LastName{i}'
    )
    Profile.objects.create(
        user=user,
        address=f'{i} Main Street',
        city=f'City{i}',
        state='StateName',
        zipcode=f'{10000 + i}',
        country='CountryName',
        phone_number=f'123456789{i}'
    )
