from itertools import chain

import structlog as logging
from django.db.models import Prefetch
from django.views.generic.list import ListView
from guardian.shortcuts import get_objects_for_user

from web.auth.mixins import RequireRegisteredMixin
from web.domains.case.access.approval.models import ExporterApprovalRequest, ImporterApprovalRequest
from web.domains.case.access.models import (
    AccessRequest,
    ExporterAccessRequest,
    ImporterAccessRequest,
)
from web.domains.case.export.models import CertificateOfManufactureApplication
from web.domains.exporter.models import Exporter
from web.domains.importer.models import Importer
from web.flow.models import Task

logger = logging.get_logger(__name__)


class Workbasket(RequireRegisteredMixin, ListView):
    template_name = "web/domains/workbasket/workbasket.html"
    permission_required = []

    def get_queryset(self):
        # TODO: remove once converted
        # return Process.objects.filter_available(
        #     [
        #         ImporterAccessRequestFlow,
        #         ExporterAccessRequestFlow,
        #         ApprovalRequestFlow,
        #         FurtherInformationRequestFlow,
        #     ],
        #     self.request.user,
        # )

        # TODO: implement below
        #   * change to django-guardian
        #   * if admin/case officer, filter by all
        #   * if external user, filter by "all exporters i have access to"

        processes = []

        if self.request.user.has_perm("web.reference_data_access"):
            certificates = CertificateOfManufactureApplication.objects.filter(
                is_active=True
            ).prefetch_related(Prefetch("tasks", queryset=Task.objects.filter(is_active=True)))
            exporter_access_requests = ExporterAccessRequest.objects.filter(
                is_active=True, status=AccessRequest.SUBMITTED
            ).prefetch_related(Prefetch("tasks", queryset=Task.objects.filter(is_active=True)))
            importer_access_requests = ImporterAccessRequest.objects.filter(
                is_active=True, status=AccessRequest.SUBMITTED
            ).prefetch_related(Prefetch("tasks", queryset=Task.objects.filter(is_active=True)))
            processes.extend([certificates, exporter_access_requests, importer_access_requests])

        else:
            # current user's exporters
            # TODO: check if agent's contacts can do Approval Request
            exporters = get_objects_for_user(
                self.request.user, ["is_contact_of_exporter"], Exporter
            )

            # current user's importers
            # TODO: check if agent's contacts can do Approval Request
            importers = get_objects_for_user(
                self.request.user, ["is_contact_of_exporter"], Importer
            )

            exporter_approval_requests = (
                ExporterApprovalRequest.objects.select_related(
                    # get the exporter associated with the approval request
                    # join access_request and join exporter from access_request
                    "access_request__exporteraccessrequest__link",
                )
                .prefetch_related(Prefetch("tasks", queryset=Task.objects.filter(is_active=True)))
                .filter(is_active=True)
                .filter(access_request__exporteraccessrequest__link__in=exporters)
            )

            importer_approval_requests = (
                ImporterApprovalRequest.objects.select_related(
                    # get the importer associated with the approval request
                    # join access_request and join importer from access_request
                    "access_request__importeraccessrequest__link",
                )
                .prefetch_related(Prefetch("tasks", queryset=Task.objects.filter(is_active=True)))
                .filter(is_active=True)
                .filter(access_request__importeraccessrequest__link__in=importers)
            )

            # contacts of exporter to approve Approval Request
            processes.extend([exporter_approval_requests, importer_approval_requests])

        # user/admin access requests and firs
        processes.append(
            self.request.user.submitted_access_requests.filter(status=AccessRequest.SUBMITTED)
            .prefetch_related("further_information_requests")
            .prefetch_related(
                Prefetch(
                    "further_information_requests__tasks",
                    queryset=Task.objects.filter(is_active=True, owner=self.request.user),
                )
            )
        )

        return chain(*processes)
