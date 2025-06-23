from django.core.management.base import BaseCommand
from django.utils import timezone
from books.models import Category, Book
from decimal import Decimal
import random
from django.utils.text import slugify
import requests
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Adds sample categories and books to the database'

    def handle(self, *args, **kwargs):
        # Create categories
        categories = [
            {'name': 'Fiction', 'description': 'Fiction books including novels and short stories', 'icon': 'fas fa-book'},
            {'name': 'Non-Fiction', 'description': 'Non-fiction books including biographies and history', 'icon': 'fas fa-book-open'},
            {'name': 'Science Fiction', 'description': 'Science fiction and fantasy books', 'icon': 'fas fa-rocket'},
            {'name': 'Mystery', 'description': 'Mystery and thriller books', 'icon': 'fas fa-search'},
            {'name': 'Romance', 'description': 'Romance novels and love stories', 'icon': 'fas fa-heart'},
            {'name': 'Biography', 'description': 'Biographies and autobiographies', 'icon': 'fas fa-user'},
            {'name': 'History', 'description': 'Historical books and accounts', 'icon': 'fas fa-landmark'},
            {'name': 'Poetry', 'description': 'Poetry collections and anthologies', 'icon': 'fas fa-pen-fancy'},
        ]

        # Clear existing categories and books
        Book.objects.all().delete()
        Category.objects.all().delete()

        for category_data in categories:
            category = Category.objects.create(
                name=category_data['name'],
                description=category_data['description'],
                icon=category_data['icon']
            )
            self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))

        # Sample books data
        books = [
            {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'category': 'Fiction',
                'description': 'A story of decadence and excess, Gatsby explores the darker aspects of the Jazz Age.',
                'isbn': '9780743273565',
                'publication_date': '1925-04-10',
                'publisher': 'Scribner',
                'pages': 180,
                'language': 'English',
                'price': Decimal('14.99'),
                'rental_price': Decimal('2.99'),
                'availability_status': 'available',
                'quantity': 3,
                'rating': Decimal('4.5'),
                'total_reviews': 150
            },
            {
                'title': '1984',
                'author': 'George Orwell',
                'category': 'Science Fiction',
                'description': 'A dystopian social science fiction novel that examines the consequences of totalitarianism.',
                'isbn': '9780451524935',
                'publication_date': '1949-06-08',
                'publisher': 'Signet Classic',
                'pages': 328,
                'language': 'English',
                'price': Decimal('12.99'),
                'rental_price': Decimal('2.49'),
                'availability_status': 'available',
                'quantity': 5,
                'rating': Decimal('4.8'),
                'total_reviews': 200
            },
            {
                'title': 'The Silent Patient',
                'author': 'Alex Michaelides',
                'category': 'Mystery',
                'description': 'A woman shoots her husband dead. She never speaks another word. A criminal psychotherapist is determined to get her to talk.',
                'isbn': '9781250301697',
                'publication_date': '2019-02-05',
                'publisher': 'Celadon Books',
                'pages': 336,
                'language': 'English',
                'price': Decimal('16.99'),
                'rental_price': Decimal('3.99'),
                'availability_status': 'available',
                'quantity': 2,
                'rating': Decimal('4.2'),
                'total_reviews': 120
            },
            {
                'title': 'Pride and Prejudice',
                'author': 'Jane Austen',
                'category': 'Romance',
                'description': 'A classic romance following the spirited Elizabeth Bennet as she navigates love and marriage.',
                'isbn': '9780141439518',
                'publication_date': '1813-01-28',
                'publisher': 'Penguin Classics',
                'pages': 432,
                'language': 'English',
                'price': Decimal('9.99'),
                'rental_price': Decimal('1.99'),
                'availability_status': 'available',
                'quantity': 4,
                'rating': Decimal('4.7'),
                'total_reviews': 180
            },
            {
                'title': 'Steve Jobs',
                'author': 'Walter Isaacson',
                'category': 'Biography',
                'description': 'The biography of Apple co-founder Steve Jobs, based on more than forty interviews with Jobs.',
                'isbn': '9781451648539',
                'publication_date': '2011-10-24',
                'publisher': 'Simon & Schuster',
                'pages': 656,
                'language': 'English',
                'price': Decimal('24.99'),
                'rental_price': Decimal('4.99'),
                'availability_status': 'available',
                'quantity': 2,
                'rating': Decimal('4.6'),
                'total_reviews': 160
            },
            {
                'title': 'Sapiens',
                'author': 'Yuval Noah Harari',
                'category': 'Non-Fiction',
                'description': 'A brief history of humankind, from ancient humans to the present day.',
                'isbn': '9780062316097',
                'publication_date': '2015-02-10',
                'publisher': 'Harper',
                'pages': 443,
                'language': 'English',
                'price': Decimal('21.99'),
                'rental_price': Decimal('4.49'),
                'availability_status': 'available',
                'quantity': 3,
                'rating': Decimal('4.4'),
                'total_reviews': 140
            },
            {
                'title': 'The Iliad',
                'author': 'Homer',
                'category': 'Poetry',
                'description': 'An epic poem set during the Trojan War, the ten-year siege of the city of Troy.',
                'isbn': '9780140275360',
                'publication_date': '1998-11-01',
                'publisher': 'Penguin Classics',
                'pages': 704,
                'language': 'English',
                'price': Decimal('15.99'),
                'rental_price': Decimal('3.49'),
                'availability_status': 'available',
                'quantity': 2,
                'rating': Decimal('4.3'),
                'total_reviews': 90
            },
            {
                'title': 'Guns, Germs, and Steel',
                'author': 'Jared Diamond',
                'category': 'History',
                'description': 'A book that attempts to explain why Eurasian civilizations have survived and conquered others.',
                'isbn': '9780393061314',
                'publication_date': '1997-03-01',
                'publisher': 'W. W. Norton & Company',
                'pages': 480,
                'language': 'English',
                'price': Decimal('19.99'),
                'rental_price': Decimal('3.99'),
                'availability_status': 'available',
                'quantity': 3,
                'rating': Decimal('4.5'),
                'total_reviews': 170
            },
            {
                'title': 'The Midnight Library',
                'author': 'Matt Haig',
                'category': 'Fiction',
                'description': 'Between life and death there is a library, and within that library, the shelves go on forever. Every book provides a chance to try another life you could have lived.',
                'isbn': '9780525559474',
                'publication_date': '2020-09-29',
                'publisher': 'Viking',
                'pages': 304,
                'language': 'English',
                'price': Decimal('22.99'),
                'rental_price': Decimal('4.99'),
                'availability_status': 'available',
                'quantity': 4,
                'rating': Decimal('4.6'),
                'total_reviews': 180
            },
            {
                'title': 'Project Hail Mary',
                'author': 'Andy Weir',
                'category': 'Science Fiction',
                'description': 'A lone astronaut must save the earth from disaster in this incredible new science-based thriller from the #1 New York Times bestselling author of The Martian.',
                'isbn': '9780593135204',
                'publication_date': '2021-05-04',
                'publisher': 'Ballantine Books',
                'pages': 496,
                'language': 'English',
                'price': Decimal('24.99'),
                'rental_price': Decimal('4.99'),
                'availability_status': 'available',
                'quantity': 3,
                'rating': Decimal('4.8'),
                'total_reviews': 220
            },
            {
                'title': 'The Seven Husbands of Evelyn Hugo',
                'author': 'Taylor Jenkins Reid',
                'category': 'Romance',
                'description': 'An entrancing novel about love, fame, and the cost of living in the spotlight, following the life of a legendary Hollywood actress.',
                'isbn': '9781501161933',
                'publication_date': '2017-06-13',
                'publisher': 'Washington Square Press',
                'pages': 400,
                'language': 'English',
                'price': Decimal('16.99'),
                'rental_price': Decimal('3.49'),
                'availability_status': 'available',
                'quantity': 5,
                'rating': Decimal('4.7'),
                'total_reviews': 250
            },
            {
                'title': 'Atomic Habits',
                'author': 'James Clear',
                'category': 'Non-Fiction',
                'description': 'A revolutionary system to get 1 percent better every day, showing how small changes in daily routines can transform your life.',
                'isbn': '9780735211292',
                'publication_date': '2018-10-16',
                'publisher': 'Avery',
                'pages': 320,
                'language': 'English',
                'price': Decimal('19.99'),
                'rental_price': Decimal('3.99'),
                'availability_status': 'available',
                'quantity': 6,
                'rating': Decimal('4.9'),
                'total_reviews': 300
            },
            {
                'title': 'The Thursday Murder Club',
                'author': 'Richard Osman',
                'category': 'Mystery',
                'description': 'Four unlikely friends meet weekly in their retirement village to discuss unsolved crimes; when a real murder occurs, they find themselves in the middle of their first live case.',
                'isbn': '9781984880963',
                'publication_date': '2020-09-03',
                'publisher': 'Penguin',
                'pages': 384,
                'language': 'English',
                'price': Decimal('18.99'),
                'rental_price': Decimal('3.99'),
                'availability_status': 'available',
                'quantity': 4,
                'rating': Decimal('4.5'),
                'total_reviews': 190
            },
            {
                'title': 'The Code Breaker',
                'author': 'Walter Isaacson',
                'category': 'Biography',
                'description': 'The story of Jennifer Doudna and her colleagues\' development of CRISPR gene-editing technology.',
                'isbn': '9781982115852',
                'publication_date': '2021-03-09',
                'publisher': 'Simon & Schuster',
                'pages': 560,
                'language': 'English',
                'price': Decimal('26.99'),
                'rental_price': Decimal('5.49'),
                'availability_status': 'available',
                'quantity': 3,
                'rating': Decimal('4.7'),
                'total_reviews': 160
            },
            {
                'title': 'The 1619 Project',
                'author': 'Nikole Hannah-Jones',
                'category': 'History',
                'description': 'A groundbreaking reframing of American history that places slavery and its continuing legacy at the center of our national narrative.',
                'isbn': '9780593230572',
                'publication_date': '2021-11-16',
                'publisher': 'One World',
                'pages': 624,
                'language': 'English',
                'price': Decimal('27.99'),
                'rental_price': Decimal('5.99'),
                'availability_status': 'available',
                'quantity': 4,
                'rating': Decimal('4.8'),
                'total_reviews': 210
            },
            {
                'title': 'Milk and Honey',
                'author': 'Rupi Kaur',
                'category': 'Poetry',
                'description': 'A collection of poetry and prose about survival, love, loss, and femininity.',
                'isbn': '9781449474256',
                'publication_date': '2015-10-06',
                'publisher': 'Andrews McMeel Publishing',
                'pages': 208,
                'language': 'English',
                'price': Decimal('14.99'),
                'rental_price': Decimal('2.99'),
                'availability_status': 'available',
                'quantity': 5,
                'rating': Decimal('4.6'),
                'total_reviews': 280
            },
            {
                'title': 'Tomorrow, and Tomorrow, and Tomorrow',
                'author': 'Gabrielle Zevin',
                'category': 'Fiction',
                'description': 'A modern tale about the friendship between two creative partners who design video games, spanning thirty years of success, jealousy, and connection.',
                'isbn': '9780593321201',
                'publication_date': '2022-07-05',
                'publisher': 'Knopf',
                'pages': 416,
                'language': 'English',
                'price': Decimal('25.99'),
                'rental_price': Decimal('4.99'),
                'availability_status': 'available',
                'quantity': 4,
                'rating': Decimal('4.7'),
                'total_reviews': 190
            },
            {
                'title': 'Dune',
                'author': 'Frank Herbert',
                'category': 'Science Fiction',
                'description': 'Set on the desert planet Arrakis, Dune is the story of the boy Paul Atreides, heir to a noble family tasked with ruling an inhospitable world.',
                'isbn': '9780441172719',
                'publication_date': '1990-09-01',
                'publisher': 'Ace',
                'pages': 896,
                'language': 'English',
                'price': Decimal('18.99'),
                'rental_price': Decimal('3.99'),
                'availability_status': 'available',
                'quantity': 5,
                'rating': Decimal('4.7'),
                'total_reviews': 280
            },
            {
                'title': 'The Paris Apartment',
                'author': 'Lucy Foley',
                'category': 'Mystery',
                'description': 'A woman arrives at her brother\'s apartment in Paris only to find him missing, and every one of his neighbors could be a suspect.',
                'isbn': '9780063003057',
                'publication_date': '2022-02-22',
                'publisher': 'William Morrow',
                'pages': 368,
                'language': 'English',
                'price': Decimal('23.99'),
                'rental_price': Decimal('4.49'),
                'availability_status': 'available',
                'quantity': 3,
                'rating': Decimal('4.3'),
                'total_reviews': 150
            },
            {
                'title': 'Book Lovers',
                'author': 'Emily Henry',
                'category': 'Romance',
                'description': 'A literary agent and an editor keep running into each other in a small town, defying the typical small-town romance tropes.',
                'isbn': '9780593440872',
                'publication_date': '2022-05-03',
                'publisher': 'Berkley',
                'pages': 384,
                'language': 'English',
                'price': Decimal('17.99'),
                'rental_price': Decimal('3.49'),
                'availability_status': 'available',
                'quantity': 4,
                'rating': Decimal('4.6'),
                'total_reviews': 170
            },
            {
                'title': 'Finding Me',
                'author': 'Viola Davis',
                'category': 'Biography',
                'description': 'The memoir of actress and producer Viola Davis, from her roots in poverty to her rise as an award-winning artist.',
                'isbn': '9780063037328',
                'publication_date': '2022-04-26',
                'publisher': 'HarperOne',
                'pages': 304,
                'language': 'English',
                'price': Decimal('24.99'),
                'rental_price': Decimal('4.99'),
                'availability_status': 'available',
                'quantity': 3,
                'rating': Decimal('4.8'),
                'total_reviews': 200
            },
            {
                'title': 'Think Again',
                'author': 'Adam Grant',
                'category': 'Non-Fiction',
                'description': 'Learn to rethink your opinions and open other people\'s minds, exploring how to embrace the joy of being wrong.',
                'isbn': '9781984878106',
                'publication_date': '2021-02-02',
                'publisher': 'Viking',
                'pages': 320,
                'language': 'English',
                'price': Decimal('20.99'),
                'rental_price': Decimal('4.29'),
                'availability_status': 'available',
                'quantity': 4,
                'rating': Decimal('4.6'),
                'total_reviews': 230
            },
            {
                'title': 'The Dawn of Everything',
                'author': 'David Graeber & David Wengrow',
                'category': 'History',
                'description': 'A new history of humanity that challenges our most fundamental assumptions about social evolution.',
                'isbn': '9780374157357',
                'publication_date': '2021-11-09',
                'publisher': 'Farrar, Straus and Giroux',
                'pages': 704,
                'language': 'English',
                'price': Decimal('28.99'),
                'rental_price': Decimal('5.99'),
                'availability_status': 'available',
                'quantity': 3,
                'rating': Decimal('4.5'),
                'total_reviews': 180
            },
            {
                'title': 'Call Us What We Carry',
                'author': 'Amanda Gorman',
                'category': 'Poetry',
                'description': 'A collection of poems exploring history, language, identity, and erasure through an imaginative and intimate collage.',
                'isbn': '9780593465066',
                'publication_date': '2021-12-07',
                'publisher': 'Viking Books',
                'pages': 240,
                'language': 'English',
                'price': Decimal('19.99'),
                'rental_price': Decimal('3.99'),
                'availability_status': 'available',
                'quantity': 4,
                'rating': Decimal('4.7'),
                'total_reviews': 160
            }
        ]

        # Create books with cover images
        for book_data in books:
            category = Category.objects.get(name=book_data.pop('category'))
            
            # Generate a unique filename for the cover image
            filename = f"{slugify(book_data['title'])}.jpg"
            image_path = os.path.join(settings.MEDIA_ROOT, 'book_covers', filename)
            
            # Download a placeholder cover image
            try:
                # Using a placeholder image service with book dimensions
                response = requests.get(f'https://picsum.photos/400/600')
                if response.status_code == 200:
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    book_data['cover_image'] = f'book_covers/{filename}'
                else:
                    self.stdout.write(self.style.WARNING(f'Failed to download cover image for {book_data["title"]}'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error downloading cover image for {book_data["title"]}: {str(e)}'))
            
            # Create the book
            book = Book.objects.create(category=category, **book_data)
            self.stdout.write(self.style.SUCCESS(f'Created book: {book.title}'))

        self.stdout.write(self.style.SUCCESS('Successfully added sample data')) 