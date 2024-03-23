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
        document = form.save(commit=False)
        document.uploaded_by_user = request.user
        document.save()
        return JsonResponse({
            'success': True,
            'file': {
                'id': document.id,
                'title': document.title,
                'url': document.url,
            }
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors,
        }, status=400)


