from typing import TYPE_CHECKING
from django.http import (
    HttpRequest,
    FileResponse,
    HttpResponse,
)
from django.shortcuts import get_object_or_404

from wagtail.images.exceptions import InvalidFilterSpecError
from wagtail.images.models import SourceImageIOError
from wagtail.images import (
    get_image_model,
)

if TYPE_CHECKING:
    from wagtail.images.models import Image as AbstractImage


Image = get_image_model()



def image_for_id(request: HttpRequest, image_id: int) -> "AbstractImage":
    image: "AbstractImage" = get_object_or_404(Image, pk=image_id)

    # Get/generate the rendition
    try:
        rendition = image.get_rendition("original")
    except SourceImageIOError:
        return HttpResponse(
            "Source image file not found", content_type="text/plain", status=410
        )

    with rendition.get_willow_image() as willow_image:
        mime_type = willow_image.mime_type

    # Serve the file
    f = rendition.file.open("rb")
    response = FileResponse(f, filename=image.filename, content_type=mime_type)
    response["Content-Length"] = f.size
    return response

