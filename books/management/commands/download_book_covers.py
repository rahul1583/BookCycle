from django.core.management.base import BaseCommand
from django.conf import settings
from books.models import Book
import requests
import os
from django.utils.text import slugify
from urllib.parse import quote

class Command(BaseCommand):
    help = 'Downloads book cover images from Google Books API'

    def handle(self, *args, **kwargs):
        # Create media directory if it doesn't exist
        media_root = settings.MEDIA_ROOT
        covers_dir = os.path.join(media_root, 'book_covers')
        os.makedirs(covers_dir, exist_ok=True)

        books = Book.objects.all()
        success_count = 0
        fail_count = 0

        for book in books:
            try:
                # Search for the book in Google Books API
                search_query = quote(f"{book.title} {book.author}")
                api_url = f"https://www.googleapis.com/books/v1/volumes?q={search_query}"
                response = requests.get(api_url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('items'):
                        # Get the first result
                        book_data = data['items'][0]
                        volume_info = book_data.get('volumeInfo', {})
                        
                        # Try to get the highest quality image available
                        image_links = volume_info.get('imageLinks', {})
                        image_url = None
                        
                        # Try different image qualities in order of preference
                        for quality in ['extraLarge', 'large', 'medium', 'thumbnail']:
                            if quality in image_links:
                                image_url = image_links[quality]
                                break
                        
                        if image_url:
                            # Download the image
                            image_response = requests.get(image_url)
                            if image_response.status_code == 200:
                                # Generate filename
                                filename = f"{slugify(book.title)}.jpg"
                                filepath = os.path.join(covers_dir, filename)
                                
                                # Save the image
                                with open(filepath, 'wb') as f:
                                    f.write(image_response.content)
                                
                                # Update book's cover_image field
                                book.cover_image = f'book_covers/{filename}'
                                book.save()
                                
                                success_count += 1
                                self.stdout.write(
                                    self.style.SUCCESS(f'Successfully downloaded cover for "{book.title}"')
                                )
                            else:
                                fail_count += 1
                                self.stdout.write(
                                    self.style.WARNING(f'Failed to download image for "{book.title}"')
                                )
                        else:
                            fail_count += 1
                            self.stdout.write(
                                self.style.WARNING(f'No cover image found for "{book.title}"')
                            )
                    else:
                        fail_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'No results found for "{book.title}"')
                        )
                else:
                    fail_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'API request failed for "{book.title}"')
                    )
                    
            except Exception as e:
                fail_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Error processing "{book.title}": {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Finished downloading book covers. Success: {success_count}, Failed: {fail_count}'
            )
        ) 