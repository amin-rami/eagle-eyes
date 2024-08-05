from django.urls import path
from eagle_eyes.apps.referral.views import ReferralSubmission, ReferralLogin

urlpatterns = [
    path("submit-phone-number/", view=ReferralSubmission.as_view(), name="submit_phone_number"),
    path("login/", view=ReferralLogin.as_view(), name="submit_phone_number"),
]
