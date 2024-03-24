from typing import TYPE_CHECKING
from django.http import (
    JsonResponse,
)
from django.views.decorators.csrf import csrf_exempt

from wagtail.models import Collection
from wagtail.documents import (
    get_document_model,
)
from wagtail.documents.forms import (
    get_document_form,
)

if TYPE_CHECKING:
    from wagtail.documents.models import AbstractDocument


Document = get_document_model()
DocumentForm = get_document_form(Document)

@csrf_exempt
def attaches_upload(request):
    collection = request.GET.get('collection', Collection.get_first_root_node().id)
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


