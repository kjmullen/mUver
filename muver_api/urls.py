from django.conf.urls import url
from muver_api.views import CreateUser, DetailUser, ListCreateJob, \
    RetrieveUpdateUserProfile, RetrieveUpdateDestroyJob,\
    CreateStripeAccount, ListUserProfile, DetailUserProfile, \
    JobsByUser, CompletedJobsByUser, CreateCustomer

urlpatterns = [
    url(r'^user/$', CreateUser.as_view(), name="create_user"),
    url(r'^user/(?P<pk>\d+)/$', DetailUser.as_view(), name="detail_user"),
    url(r'^profiles/$', ListUserProfile.as_view(), name="list_profile"),
    url(r'^profiles/(?P<pk>\d+)/$', RetrieveUpdateUserProfile.as_view(),
        name="detail_profile"),
    url(r'^profile/$', DetailUserProfile.as_view(),
        name="detail_logged_in_profile"),
    url(r'^profile/jobs/$', JobsByUser.as_view(), name="user_jobs"),
    url(r'^profile/jobs/completed/$', CompletedJobsByUser.as_view(),
        name="completed_user_jobs"),
    url(r'^jobs/$', ListCreateJob.as_view(), name="list_create_job"),
    url(r'^jobs/(?P<pk>\d+)/$', RetrieveUpdateDestroyJob.as_view(),
        name="detail_update_delete_job"),
    url(r'^customer/$', CreateCustomer.as_view(), name="create_customer"),
    url(r'^stripe/$', CreateStripeAccount.as_view(), name="create_stripe"),
    url(r'^strike/$', CreateStrike.as_view(), name="create_strike"),
    # url(r'^charge/$', CreateCharge.as_view(), name="create_charge"),
    # url(r'^charge/capture/$', CreateCaptureCharge.as_view(),
    #     name='capture_charge'),
]
