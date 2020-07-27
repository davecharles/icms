import structlog as logging
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, reverse
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from viewflow.flow.views import UpdateProcessView
from viewflow.models import Process

from web.views.mixins import FileUploadMixin

from . import forms, models

logger = logging.getLogger(__name__)


def get_parent_process(request):
    """
        Resolve parent process from url parameter parent_process_pk

        Resolves concrete Process model. E.g. ImporterAccessRequestProcess,
        ExporterAccessRequestProcess, etc
    """
    kwargs = request.resolver_match.kwargs
    parent_process_pk = kwargs.get("parent_process_pk")
    base_process = get_object_or_404(Process, pk=parent_process_pk)
    parent_process = get_object_or_404(base_process.flow_class.process_class, pk=parent_process_pk)
    # If parent process is finished no new FIR is to be allowed
    if parent_process.finished:
        raise Http404("Parent process not found")
    return parent_process


def get_fir_list_url(parent_process):
    """
        Return url for FIR list page of parent process
    """
    return reverse(f"{parent_process.get_process_namespace()}:fir-list", args=(parent_process.pk,),)


class FurtherInformationRequestListView(ListView):
    """
        List of FIRs for given parent process
    """

    template_name = "web/domains/case/fir/list.html"
    context_object_name = "fir_list"

    def get_queryset(self):
        # Filter by parent process
        parent_process = get_parent_process(self.request)
        return parent_process.fir_processes.filter(fir__is_active=True)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["parent_process"] = get_parent_process(self.request)
        return context

    class Meta:
        model = models.FurtherInformationRequestProcess


class FurtherInformationRequestStartView(PermissionRequiredMixin, FileUploadMixin, FormView):
    """
    Creates a new FIR and associates it with the parent process,
    then display FIR form for new FIR
    """

    template_name = "web/domains/case/fir/start.html"
    form_class = forms.FurtherInformationRequestForm

    def has_permission(self):
        """
            Check parent process for permission
        """
        return get_parent_process(self.request).get_fir_starter_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["parent_process"] = get_parent_process(self.request)
        return context

    def get_form(self):
        request = self.request
        parent_process = get_parent_process(self.request)
        if request.POST:
            return self.form_class(user=self.request.user, data=request.POST)

        # initial request
        template = parent_process.get_fir_template()
        initial = {
            "request_detail": parent_process.render_template_content(template, self.request),
            "request_subject": parent_process.render_template_title(template, self.request),
        }
        return self.form_class(user=self.request.user, initial=initial)

    def _start_process(self, fir):
        """
            Trigger FIR flow start task
        """
        # Lazy import as flows.py imports views.py as well, causing a circular
        # dependency
        from .flows import FurtherInformationRequestFlow

        parent_process = get_parent_process(self.request)
        parent_process.add_fir(fir)

        # Start a new FIR flow
        FurtherInformationRequestFlow.start.run(get_parent_process(self.request), fir)

    @transaction.atomic
    def form_valid(self, form):
        """
            If the form is valid set parent process and start FIR process
        """
        fir = form.save()
        fir.files.set(self.get_files())
        self._start_process(fir)
        parent_process = get_parent_process(self.request)
        return redirect(get_fir_list_url(parent_process))


class FutherInformationRequestEditView(FileUploadMixin, UpdateProcessView):
    """
        Edit or submit an existing FIR draft
    """

    template_name = "web/domains/case/fir/edit.html"
    form_class = forms.FurtherInformationRequestForm

    def get_file_queryset(self):
        return self.get_form().instance.files

    def get_form(self):
        fir = self.activation.process.fir
        return self.form_class(instance=fir, data=self.request.POST or None)

    def get_success_url(self):
        return get_fir_list_url(self.activation.process.parent_process)

    def form_valid(self, form):
        """
            Prevent proceeding with Viewflow if saving as draft
        """
        fir = form.save()
        fir.files.set(self.get_files())
        if fir.is_draft():
            return redirect(self.get_success_url())

        return super().form_valid(form)


class FurtherInformationRequestResponseView(FileUploadMixin, UpdateProcessView):
    template_name = "web/domains/case/fir/respond.html"
    form_class = forms.FurtherInformationRequestResponseForm

    def get_form(self):
        return self.form_class(
            self.request.user, instance=self.activation.process.fir, data=self.request.POST or None,
        )

    def get_success_url(self):
        return reverse("workbasket")

    def get_file_queryset(self):
        return self.get_form().instance.files


class FurtherInformationRequestReviewView(FileUploadMixin, UpdateProcessView):
    template_name = "web/domains/case/fir/review.html"

    def form_valid(self, form):
        fir = form.instance.fir
        fir.close()
        return super().form_valid(form)

    def get_file_queryset(self):
        return self.get_form().instance.fir.files

    def get_success_url(self):
        return get_fir_list_url(self.activation.process.parent_process)
