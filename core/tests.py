# Create your tests here.
from django.test import TestCase
from core.models import Slide, Article
from django.core.files.uploadedfile import SimpleUploadedFile
import os


class SlideModelTest(TestCase):
    def setUp(self):
        # Create a sample image for testing
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'test image content',
            content_type='image/jpeg'
        )

    def test_create_slide(self):
        slide = Slide.objects.create(
            title="Test Slide",
            description="This is a test slide description.",
            image=self.test_image,
            order=1
        )
        self.assertEqual(slide.title, "Test Slide")
        self.assertEqual(slide.description, "This is a test slide description.")
        self.assertEqual(slide.order, 1)

    def test_delete_slide_removes_image(self):
        slide = Slide.objects.create(
            title="Delete Test Slide",
            description="This is a slide to test deletion.",
            image=self.test_image,
            order=2
        )
        image_path = slide.image.path
        self.assertTrue(os.path.isfile(image_path))
        
        slide.delete()
        self.assertFalse(os.path.isfile(image_path))

    def test_slide_string_representation(self):
        slide = Slide.objects.create(
            title="String Representation Test Slide",
            image=self.test_image
        )
        self.assertEqual(str(slide), "String Representation Test Slide")


class ArticleModelTest(TestCase):
    def setUp(self):
        # Create a sample image for testing
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'test image content',
            content_type='image/jpeg'
        )

    def test_create_article(self):
        article = Article.objects.create(
            title="Test Article",
            description="This is a test article description.",
            image=self.test_image,
            is_published=True
        )
        self.assertEqual(article.title, "Test Article")
        self.assertEqual(article.description, "This is a test article description.")
        self.assertTrue(article.is_published)

    def test_article_snippet(self):
        long_description = "A" * 300
        article = Article.objects.create(
            title="Snippet Test Article",
            description=long_description,
            image=self.test_image
        )
        self.assertTrue(len(article.snippet()) <= 203)  # 200 chars + "..."

    def test_delete_article_removes_image(self):
        article = Article.objects.create(
            title="Delete Test Article",
            description="This is an article to test deletion.",
            image=self.test_image
        )
        image_path = article.image.path
        self.assertTrue(os.path.isfile(image_path))
        
        article.delete()
        self.assertFalse(os.path.isfile(image_path))

    def test_article_string_representation(self):
        article = Article.objects.create(
            title="String Representation Test Article",
            image=self.test_image
        )
        self.assertEqual(str(article), "String Representation Test Article")

