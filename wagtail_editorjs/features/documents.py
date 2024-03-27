from typing import Any, TYPE_CHECKING
from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe
from django.http import (
    JsonResponse,
)

from wagtail.models import Collection
from wagtail.documents import (
    get_document_model,
)
from wagtail.documents.forms import (
    get_document_form,
)
if TYPE_CHECKING:
    from wagtail.documents.models import AbstractDocument

from ..registry import (
    EditorJSFeature,
    EditorJSBlock,
    EditorJSElement,
    FeatureViewMixin,
)

BYTE_SIZE_STEPS = [_("Bytes"), _("Kilobytes"), _("Megabytes"), _("Gigabytes"), _("Terabytes")]

def filesize_to_human_readable(size: int) -> str:
    for unit in BYTE_SIZE_STEPS:
        if size < 1024:
            break
        size /= 1024
    return f"{size:.0f} {unit}"



Document = get_document_model()
DocumentForm = get_document_form(Document)


class AttachesFeature(FeatureViewMixin, EditorJSFeature):
    allowed_tags = [
        "div", "p", "span", "a",
        "svg", "path",
    ]
    allowed_attributes = {
        "div": ["class"],
        "p": ["class"],
        "span": ["class"],
        "a": ["class", "href", "title"],
        "svg": ["xmlns", "width", "height", "fill", "class", "viewBox"],
        "path": ["d"],
    }
    klass="CSRFAttachesTool"
    js=[
        "wagtail_editorjs/vendor/editorjs/tools/attaches.js",
        "wagtail_editorjs/js/tools/attaches.js",
    ],


    def get_config(self, context: dict[str, Any] = None) -> dict:
        config = super().get_config(context)
        config.setdefault("config", {})
        config["config"]["endpoint"] = reverse(f"wagtail_editorjs:{self.tool_name}")
        return config


    def validate(self, data: Any):
        super().validate(data)

        if "file" not in data["data"]:
            raise forms.ValidationError("Invalid file value")
        
        if "id" not in data["data"]["file"] and not data["data"]["file"]["id"] and "url" not in data["data"]["file"]:
            raise forms.ValidationError("Invalid id/url value")
        
        if "title" not in data["data"]:
            raise forms.ValidationError("Invalid title value")
        

    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:

        document_id = block["data"]["file"]["id"]
        document = Document.objects.get(pk=document_id)
        url = document.url

        if not any([url.startswith(i) for i in ["http://", "https://", "//"]]) and context:
            request = context.get("request")
            if request:
                url = request.build_absolute_uri(url)

        if block["data"]["title"]:
            title = block["data"]["title"]
        else:
            if document:
                title = document.title
            else:
                title = url

        return EditorJSElement(
            "div",
            [
                EditorJSElement(
                    "p",
                    EditorJSElement(
                        "a",
                        title,
                        attrs={"href": url},
                    ),
                    attrs={"class": "attaches-title"},
                ),
                EditorJSElement(
                    "span",
                    filesize_to_human_readable(document.file.size),
                    attrs={"class": "attaches-size"},
                ),
                EditorJSElement(
                    "a",
                    mark_safe("""<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-link" viewBox="0 0 16 16">
    <path d="M6.354 5.5H4a3 3 0 0 0 0 6h3a3 3 0 0 0 2.83-4H9q-.13 0-.25.031A2 2 0 0 1 7 10.5H4a2 2 0 1 1 0-4h1.535c.218-.376.495-.714.82-1z"/>
    <path d="M9 5.5a3 3 0 0 0-2.83 4h1.098A2 2 0 0 1 9 6.5h3a2 2 0 1 1 0 4h-1.535a4 4 0 0 1-.82 1H12a3 3 0 1 0 0-6z"/>
</svg>"""),
                    attrs={
                        "title": _("Download"),
                        "href": url,
                        "class": "attaches-link",
                        # "data-id": document_id,
                    },
                )
            ],
            attrs={"class": "attaches"},
        )
    

    @classmethod
    def get_test_data(cls):
        instance = Document.objects.first()
        return [
            {
                "file": {
                    "id": instance.pk,
                },
                "title": "Document",
            },
        ]

    @csrf_exempt
    def handle_post(self, request):
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({
                'success': False,
                'errors': {
                    'file': ["This field is required."]
                }
            }, status=400)

        filename = file.name
        title = request.POST.get('title', filename)

        collection = Collection.get_first_root_node().id
        form = DocumentForm({ 'title': title, 'collection': collection }, request.FILES)
        if form.is_valid():
            document: AbstractDocument = form.save(commit=False)

            hash = document.get_file_hash()
            existing = Document.objects.filter(file_hash=hash)
            if existing.exists():
                exists: AbstractDocument = existing.first()
                return JsonResponse({
                    'success': True,
                    'file': {
                        'id': exists.pk,
                        'title': exists.title,
                        'size': exists.file.size,
                        'url': exists.url,
                        'upload_replaced': True,
                        'reuploaded_by_user': request.user.pk,
                    }
                })

            document.uploaded_by_user = request.user
            document.save()
            return JsonResponse({
                'success': True,
                'file': {
                    'id': document.pk,
                    'title': document.title,
                    'size': document.file.size,
                    'url': document.url,
                    'upload_replaced': False,
                    'reuploaded_by_user': None,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors,
            }, status=400)

