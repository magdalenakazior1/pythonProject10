from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.urls import reverse, reverse_lazy
from .models import Product, OrderItem, Order, Profile, Category, Review, Cart, CartItem
from .forms import ProductForm, UserForm, ProfileForm, CategoryForm, ReviewForm, CustomUserCreationForm
from django.contrib import messages

# Custom decorator to check if the user is staff
def staff_required(user):
    return user.is_staff

# Home view
def home(request):
    return render(request, 'store/home.html')

# Product listing view
def product_list(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    if selected_category:
        products = Product.objects.filter(category__id=selected_category)
    else:
        products = Product.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
    }
    return render(request, 'store/product_list.html', context)

# Add product to cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'price': product.price})

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f'{product.name} was added to your cart.')
    return redirect('store:view_cart')  # Updated to include 'store:' for namespacing

# View cart
@login_required
def view_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    return render(request, 'store/cart.html', {'cart': cart})

# Update cart item quantity
@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('store:view_cart')  # Updated to include 'store:' for namespacing

# Delete cart item
@login_required
def delete_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('store:view_cart')

# Checkout view
@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('store:view_cart')  # Updated to include 'store:' for namespacing

    if request.method == 'POST':
        order = Order.objects.create(user=request.user)
        for item in cart.items.all():
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.price)
        cart.items.all().delete()  # Clear the cart
        messages.success(request, 'Order placed successfully.')
        return redirect('store:home')

    return render(request, 'store/checkout.html', {'cart': cart})

@login_required
def place_order(request):
    if request.method == 'POST':
        # Retrieve data from the form
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        zipcode = request.POST['zipcode']
        country = request.POST['country']
        phone = request.POST['phone']
        payment_method = request.POST['payment_method']
        delivery_date = request.POST['delivery_date']

        # Create the order
        order = Order.objects.create(
            user=request.user,
            address=address,
            city=city,
            state=state,
            zipcode=zipcode,
            country=country,
            phone=phone,
            payment_method=payment_method,
            delivery_date=delivery_date,
            status='processing'
        )

        # Move items from cart to order
        cart = Cart.objects.get(user=request.user)
        for item in cart.items.all():
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.price)

        # Clear the cart
        cart.items.all().delete()

        # Redirect to order confirmation
        messages.success(request, 'Order placed successfully!')
        return redirect('store:order_confirmation')

    return redirect('store:view_cart')  # Updated to include 'store:' for namespacing

@login_required
def order_confirmation(request):
    return render(request, 'store/order_confirmation.html')

# Admin panel view (staff only)
@login_required
@user_passes_test(staff_required)
def admin_panel(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        category_id = request.POST.get('category_id')
        product = get_object_or_404(Product, id=product_id)
        category = get_object_or_404(Category, id=category_id)
        product.category = category
        product.save()
        messages.success(request, 'Product category updated successfully.')
        return redirect('store:admin_panel')
    return render(request, 'store/admin_panel.html', {'products': products, 'categories': categories})

# Add product view (staff only)
@login_required
@user_passes_test(staff_required)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully.')
            return redirect('store:admin_panel')
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})

# Edit product view (staff only)
@login_required
@user_passes_test(staff_required)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('store:admin_panel')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/edit_product.html', {'form': form, 'product': product})

# User profile view
@login_required
def profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=profile)

    # Determine account type based on user permissions
    if request.user.is_superuser:
        account_type = "Administrator"
    elif request.user.is_staff:
        account_type = "Staff"
    else:
        account_type = "Regular User"

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated.')
            return redirect('store:profile')

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'account_type': account_type,  # Pass the account type to the template
    }

    return render(request, 'store/profile.html', context)

# User registration view
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            account_type = form.cleaned_data.get('account_type')

            if account_type == 'admin':
                user.is_superuser = True
                user.is_staff = True
            elif account_type == 'staff':
                user.is_staff = True

            user.save()
            login(request, user)
            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('store:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Custom login view
class CustomLoginView(LoginView):
    template_name = 'store/login.html'  # Updated to use your custom login template

    def get_success_url(self):
        messages.success(self.request, 'Login successful.')
        return reverse('store:home')

# Custom logout view
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('store:home')  # Redirect to home page after logout

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Logout was successful.')
        return super().dispatch(request, *args, **kwargs)

# Add category view (staff only)
@login_required
@user_passes_test(staff_required)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('store:admin_panel')
    else:
        form = CategoryForm()
    return render(request, 'store/add_category.html', {'form': form})

# Edit category view (staff only)
@login_required
@user_passes_test(staff_required)
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('store:admin_panel')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'store/edit_category.html', {'form': form, 'category': category})

# Delete category view (staff only)
@login_required
@user_passes_test(staff_required)
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('store:admin_panel')
    return render(request, 'store/delete_category.html', {'category': category})
