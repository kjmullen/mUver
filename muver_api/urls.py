from django.conf.urls import url
from muver_api.views import CreateUser, DetailUser, ListUserProfile

urlpatterns = [
    url(r'^user/$', CreateUser.as_view(), name="create_user"),
    url(r'^user/(?P<pk>\d+)/$', DetailUser.as_view(), name="detail_user"),
    url(r'^profiles/$', ListUserProfile.as_view(), name="list_profile"),

]
