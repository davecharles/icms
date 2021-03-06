from django.urls import reverse_lazy

from web.views import ModelCreateView

from .forms import NewImportApplicationForm
from .models import ImportApplication

permissions = "web.IMP_EDIT_APP"


class ImportApplicationCreateView(ModelCreateView):
    template_name = "web/domains/application/import/create.html"
    model = ImportApplication
    # TODO: Change to application form when created
    success_url = reverse_lazy("product-legislation-list")
    cancel_url = success_url
    form_class = NewImportApplicationForm
    page_title = "Create Import Application"
    permission_required = permissions

    def get_form(self):
        if hasattr(self, "form"):
            return self.form

        if self.request.POST:
            self.form = NewImportApplicationForm(self.request, data=self.request.POST)
        else:
            self.form = NewImportApplicationForm(self.request)

        return self.form

    def post(self, request, *args, **kwargs):
        # see web/static/web/js/main.js::initialize
        if request.POST:
            if request.POST.get("change", None):
                return super().get(request, *args, **kwargs)

        form = self.get_form()
        form.instance.created_by = request.user

        return super().post(request, *args, **kwargs)
