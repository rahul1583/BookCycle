from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Book, Category, Review
from transactions.models import Transaction, Wishlist
from .forms import ReviewForm
from django.utils import timezone
from django.views.decorators.http import require_POST

def home(request):
    featured_books = Book.objects.filter(availability_status='available')[:8]
    categories = Category.objects.all()
    return render(request, 'home.html', {
        'featured_books': featured_books,
        'categories': categories,
    })

def book_list(request):
    books = Book.objects.all()
    categories = Category.objects.all()
    
    # Get filter parameters
    category = request.GET.get('category')
    search = request.GET.get('search')
    availability = request.GET.get('availability')
    sort = request.GET.get('sort', 'newest')
    
    # Apply filters
    if category:
        books = books.filter(category__slug=category)
    if search:
        books = books.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(description__icontains=search)
        )
    if availability:
        if availability == 'available':
            books = books.filter(availability_status='available')
        elif availability == 'borrowed':
            books = books.filter(availability_status__in=['borrowed', 'rented'])
    
    # Apply sorting
    if sort == 'newest':
        books = books.order_by('-created_at')
    elif sort == 'rating':
        books = books.order_by('-rating')
    elif sort == 'title':
        books = books.order_by('title')
    elif sort == 'popular':
        books = books.order_by('-total_reviews')
    
    # Add book count to categories
    for category in categories:
        category.book_count = Book.objects.filter(category=category).count()
    
    # Pagination
    paginator = Paginator(books, 12)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    
    context = {
        'books': books,
        'categories': categories,
        'selected_categories': [category] if category else [],
        'availability': availability,
        'sort': sort,
        'search': search,
    }
    
    return render(request, 'books/book_list.html', context)

@login_required
def dashboard(request):
    # Get active transactions (completed borrow/rent transactions)
    active_transactions = Transaction.objects.filter(
        user=request.user,
        status='completed',
        transaction_type__in=['borrow', 'rent']
    ).order_by('-created_at')

    # Get borrowed books (books with active transactions)
    borrowed_books = Book.objects.filter(
        transactions__user=request.user,
        transactions__status='completed',
        transactions__transaction_type__in=['borrow', 'rent']
    ).distinct()

    # Get total number of books borrowed (including returned ones)
    total_borrowed = Transaction.objects.filter(
        user=request.user,
        transaction_type__in=['borrow', 'rent']
    ).count()

    # Get wishlist books
    wishlist = Wishlist.objects.get_or_create(user=request.user)[0]
    wishlist_books = wishlist.books.all()

    # Get recent reviews
    recent_reviews = Review.objects.filter(user=request.user).order_by('-created_at')[:5]

    context = {
        'active_transactions': active_transactions,
        'borrowed_books': borrowed_books,
        'total_borrowed': total_borrowed,
        'wishlist_books': wishlist_books,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'books/dashboard.html', context)

def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug)
    reviews = book.reviews.all().order_by('-created_at')
    is_wishlisted = False
    
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.get_or_create(user=request.user)[0]
        is_wishlisted = book in wishlist.books.all()
    
    return render(request, 'books/book_detail.html', {
        'book': book,
        'reviews': reviews,
        'is_wishlisted': is_wishlisted,
    })

@login_required
def borrow_book(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if book.availability_status != 'available' or book.quantity <= 0:
        messages.error(request, 'This book is not available for borrowing.')
        return redirect('books:book_detail', slug=book.slug)
    
    transaction = Transaction.objects.create(
        transaction_type='borrow',
        book=book,
        user=request.user,
        amount=0,
        due_date=timezone.now() + timezone.timedelta(days=14),
        status='completed'
    )
    
    # Update book availability and quantity
    book.quantity -= 1
    if book.quantity == 0:
        book.availability_status = 'borrowed'
    book.save()
    
    messages.success(request, f'Successfully borrowed {book.title}.')
    return redirect('books:book_detail', slug=book.slug)

@login_required
def rent_book(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if book.availability_status != 'available' or not book.rental_price or book.quantity <= 0:
        messages.error(request, 'This book is not available for renting.')
        return redirect('books:book_detail', slug=book.slug)
    
    transaction = Transaction.objects.create(
        transaction_type='rent',
        book=book,
        user=request.user,
        amount=book.rental_price,
        due_date=timezone.now() + timezone.timedelta(days=7),
        status='completed'
    )
    
    # Update book availability and quantity
    book.quantity -= 1
    if book.quantity == 0:
        book.availability_status = 'rented'
    book.save()
    
    messages.success(request, f'Successfully rented {book.title}.')
    return redirect('books:book_detail', slug=book.slug)

@login_required
def purchase_book(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if book.availability_status != 'available' or book.quantity <= 0:
        messages.error(request, 'This book is not available for purchase.')
        return redirect('books:book_detail', slug=book.slug)
    
    transaction = Transaction.objects.create(
        transaction_type='purchase',
        book=book,
        user=request.user,
        amount=book.price,
        status='completed'
    )
    
    # Update book availability and quantity
    book.quantity -= 1
    if book.quantity == 0:
        book.availability_status = 'sold'
    book.save()
    
    messages.success(request, f'Successfully purchased {book.title}.')
    return redirect('books:book_detail', slug=book.slug)

@login_required
def return_book(request, slug):
    book = get_object_or_404(Book, slug=slug)
    transaction = Transaction.objects.filter(
        book=book,
        user=request.user,
        transaction_type__in=['borrow', 'rent'],
        status='completed'
    ).first()
    
    if not transaction:
        messages.error(request, 'No active transaction found for this book.')
        return redirect('books:book_detail', slug=book.slug)
    
    transaction.transaction_type = 'return'
    transaction.status = 'completed'
    transaction.return_date = timezone.now()
    transaction.save()
    
    # Update book availability and quantity
    book.quantity += 1
    if book.quantity > 0:
        book.availability_status = 'available'
    book.save()
    
    messages.success(request, f'Successfully returned {book.title}.')
    return redirect('books:book_detail', slug=book.slug)

@login_required
def add_review(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            messages.success(request, 'Review added successfully.')
            return redirect('books:book_detail', slug=book.slug)
    else:
        form = ReviewForm()
    
    return render(request, 'books/add_review.html', {
        'form': form,
        'book': book,
    })

@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.get_or_create(user=request.user)[0]
    return render(request, 'books/wishlist.html', {
        'wishlist': wishlist,
    })

@login_required
def add_to_wishlist(request, slug):
    book = get_object_or_404(Book, slug=slug)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    if book in wishlist.books.all():
        messages.info(request, f'{book.title} is already in your wishlist.')
    else:
        wishlist.books.add(book)
        messages.success(request, f'{book.title} added to your wishlist.')
    
    return redirect('books:book_detail', slug=book.slug)

@login_required
def remove_from_wishlist(request, slug):
    book = get_object_or_404(Book, slug=slug)
    wishlist = Wishlist.objects.filter(user=request.user).first()
    
    if wishlist and book in wishlist.books.all():
        wishlist.books.remove(book)
        messages.success(request, f'{book.title} removed from your wishlist.')
    else:
        messages.info(request, f'{book.title} is not in your wishlist.')
    
    return redirect('books:book_detail', slug=book.slug)

@require_POST
def newsletter_subscribe(request):
    email = request.POST.get('email')
    if email:
        # Here you would typically save the email to your newsletter subscribers database
        # For now, we'll just show a success message
        messages.success(request, 'Thank you for subscribing to our newsletter!')
    else:
        messages.error(request, 'Please provide a valid email address.')
    return redirect('home')

def about(request):
    return render(request, 'about.html')
