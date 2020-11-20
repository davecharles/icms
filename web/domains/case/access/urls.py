from django.urls import include, path, re_path

from . import views


app_name = "access"
urlpatterns = [
    path("importer/request/", views.importer_access_request, name="importer-request"),
    path("exporter/request/", views.exporter_access_request, name="exporter-request"),
    path("requested/", views.AccessRequestCreatedView.as_view(), name="requested"),
    re_path(
        "case/(?P<application_pk>[0-9]+)/(?P<entity>importer|exporter)/view/$",
        views.case_view,
        name="case-view",
    ),
    re_path(
        "case/(?P<application_pk>[0-9]+)/(?P<entity>importer|exporter)/view/firs/$",
        views.case_firs,
        name="case-firs",
    ),
    re_path(
        "case/(?P<application_pk>[0-9]+)/(?P<entity>importer|exporter)/firs/(?P<fir_pk>[0-9]+)/respond/$",
        views.case_fir_respond,
        name="case-fir-respond",
    ),
    # access request management
    re_path(
        "^case/(?P<pk>[0-9]+)/(?P<entity>importer|exporter)/management/$",
        views.management,
        name="case-management",
    ),
    re_path(
        "^case/(?P<pk>[0-9]+)/(?P<entity>importer|exporter)/close-access-request/$",
        views.management_response,
        name="case-management-response",
    ),
    # approval request
    re_path(
        "^case/(?P<pk>[0-9]+)/(?P<entity>importer|exporter)/approval-request/$",
        views.management_access_approval,
        name="case-management-access-approval",
    ),
    re_path(
        "^case/(?P<application_pk>[0-9]+)/(?P<entity>importer|exporter)/approval-request/(?P<approval_request_pk>[0-9]+)/withdraw/$",
        views.management_access_approval_withdraw,
        name="case-management-approval-request-withdraw",
    ),
    # approval request response by importer/exporter contacts
    re_path(
        "case/(?P<pk>[0-9]+)/(?P<entity>importer|exporter)/take_ownership/$",
        views.take_ownership_approval,
        name="case-approval-take-ownership",
    ),
    re_path(
        "case/(?P<pk>[0-9]+)/(?P<entity>importer|exporter)/release_ownership/$",
        views.release_ownership_approval,
        name="case-approval-release-ownership",
    ),
    re_path(
        "case/(?P<application_pk>[0-9]+)/(?P<entity>importer|exporter)/approval-request/(?P<approval_request_pk>[0-9]+)/$",
        views.case_approval_respond,
        name="case-approval-respond",
    ),
    # management for further information requests
    re_path(
        "^case/(?P<application_pk>[0-9]+)/(?P<entity>importer|exporter)/management/firs/",
        include(
            [
                path("", views.management_firs, name="case-management-firs",),
                re_path("add/$", views.add_fir, name="case-management-fir-add",),
                path("<int:fir_pk>/edit/", views.edit_fir, name="case-management-fir-edit",),
                path(
                    "<int:fir_pk>/archive/", views.archive_fir, name="case-management-fir-archive",
                ),
                path(
                    "<int:fir_pk>/withdraw/",
                    views.withdraw_fir,
                    name="case-management-fir-withdraw",
                ),
                path("<int:fir_pk>/close/", views.close_fir, name="case-management-fir-close",),
                path(
                    "<int:fir_pk>/files/<int:file_pk>/",
                    views.fir_archive_file,
                    name="case-management-fir-file-archive",
                ),
            ]
        ),
    ),
]
