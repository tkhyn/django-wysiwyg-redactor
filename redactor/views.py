import os
import uuid

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from redactor.forms import ImageForm


UPLOAD_PATH = getattr(settings, 'REDACTOR_UPLOAD', 'redactor/')


@csrf_exempt
@require_POST
@user_passes_test(lambda u: u.is_staff)
def redactor_upload(request, upload_to=None, form_class=ImageForm,
                    response=lambda name, url: url):
    form = form_class(request.POST, request.FILES)
    if form.is_valid():
        file_ = form.cleaned_data['file']
        path = os.path.join(upload_to or UPLOAD_PATH, file_.name)
        count = 1
        while os.path.exists(path):
            fpath, ext = os.path.splitext(path)
            path = '%s_%d%s' % (fpath, count, ext)
        real_path = default_storage.save(path, file_)
        return HttpResponse(
            response(os.path.split(path)[-1], default_storage.url(real_path))
        )
    return HttpResponse(status=403)
