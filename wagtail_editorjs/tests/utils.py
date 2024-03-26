from django.test import TestCase
from django.core.management import call_command
from wagtail.models import Collection, Page
from wagtail.images.tests.utils import (
    get_test_image_file,
    get_test_image_file_jpeg,
    get_test_image_file_webp,
    get_test_image_file_avif,
)
from wagtail.images import get_image_model
from wagtail.documents import get_document_model


Image = get_image_model()
Document = get_document_model()


class BaseEditorJSTest(TestCase):
    def setUp(self) -> None:
        image_funcs = [
            get_test_image_file,
            get_test_image_file_jpeg,
            get_test_image_file_webp,
            get_test_image_file_avif,
        ]
        self.collection = Collection.get_first_root_node()
        root_page = Page.objects.filter(depth=2).first()
        
        child_url_paths = []
        sibling_url_paths = []
        
        for i in range(100):
            
            child_url_paths.append(f"test-page-{i}")
            sibling_url_paths.append(f"test-subchild-page-{i}")

            child = root_page.add_child(instance=Page(
                title=f"Test Page {i}",
                slug=f"test-page-{i}",
                path=f"/test-page-{i}/",
                url_path=f"/test-page-{i}/",
            ))
            child.set_url_path(root_page)
            child.save()

            subchild = child.add_child(instance=Page(
                title=f"Test Page subchild {i}",
                slug=f"test-subchild-page-{i}",
                path=f"/test-subchild-page-{i}/",
                url_path=f"/test-subchild-page-{i}/",
            ))
            subchild.set_url_path(child)
            subchild.save()

            Document.objects.create(file=get_test_image_file(), title=f"Test Document {i}", collection=self.collection)
            Image.objects.create(
                file=image_funcs[i % len(image_funcs)](),
                title=f"Test Image {i}",
                collection=self.collection
            )
        call_command("fixtree")
        call_command("set_url_paths")

