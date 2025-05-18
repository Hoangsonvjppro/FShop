from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Category, Brand, Product, ProductImage


def home(request):
    """Trang chủ với các sản phẩm nổi bật, mới nhất."""
    categories = Category.objects.all()
    new_products = Product.objects.filter(available=True, is_deleted=False).order_by('-created_at')[:8]
    featured_products = Product.objects.filter(available=True, is_deleted=False).order_by('?')[:4]
    
    # Lấy sản phẩm cho từng danh mục
    category_products = {}
    for category in categories:
        category_products[category] = Product.objects.filter(
            category=category, 
            available=True, 
            is_deleted=False
        ).order_by('-created_at')[:4]
    
    context = {
        'categories': categories,
        'new_products': new_products,
        'featured_products': featured_products,
        'category_products': category_products,
    }
    return render(request, 'products/home.html', context)


def product_list(request, category_slug=None, brand_slug=None, room_type=None, material=None):
    """Danh sách sản phẩm với lọc theo danh mục, thương hiệu, loại phòng, chất liệu."""
    category = None
    brand = None
    categories = Category.objects.all()
    brands = Brand.objects.all()
    room_types = dict(Product.ROOM_CHOICES)
    material_types = dict(Product.MATERIAL_CHOICES)
    
    products = Product.objects.filter(available=True, is_deleted=False)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    if brand_slug:
        brand = get_object_or_404(Brand, slug=brand_slug)
        products = products.filter(brand=brand)
    
    if room_type:
        products = products.filter(room_type=room_type)
    
    if material:
        products = products.filter(material=material)
    
    # Sắp xếp sản phẩm
    sort = request.GET.get('sort', 'default')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name_asc':
        products = products.order_by('name')
    elif sort == 'name_desc':
        products = products.order_by('-name')
    else:
        products = products.order_by('-created_at')
    
    context = {
        'category': category,
        'brand': brand,
        'categories': categories,
        'brands': brands,
        'room_types': room_types,
        'material_types': material_types,
        'products': products,
        'room_type_selected': room_type,
        'material_selected': material,
        'sort': sort,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, id, slug):
    """Chi tiết sản phẩm."""
    product = get_object_or_404(Product, id=id, slug=slug, available=True, is_deleted=False)
    
    # Lấy tất cả ảnh sản phẩm
    product_images = ProductImage.objects.filter(product=product)
    
    # Lấy sản phẩm liên quan
    related_products = Product.objects.filter(
        category=product.category,
        available=True,
        is_deleted=False
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'product_images': product_images,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)


def search(request):
    """Tìm kiếm sản phẩm."""
    query = request.GET.get('q', '')
    products = []
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(brand__name__icontains=query),
            available=True,
            is_deleted=False
        ).distinct()
    
    context = {
        'query': query,
        'products': products,
    }
    return render(request, 'products/search_results.html', context) 