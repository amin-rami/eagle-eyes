from locust import HttpUser, task
import random

URL_PREFIX = "/api/v1"
USER_ID = "eagle-eyes-user"


class EagleEyesProducerUser(HttpUser):
    @task
    def post_events(self):
        vertical = random.choice(["media", "ava"])
        action = random.choice(["play", "search"])

        self.client.post(
            url=f"{URL_PREFIX}/campaigns/events/",
            json={
                "user_id": USER_ID,
                "vertical": vertical,
                "action": action,
            }
        )


class EagleEyesStateWatcherUser(HttpUser):
    @task
    def get_trend_query_list(self):
        self.client.get(url=f"{URL_PREFIX}/campaigns/campaign-states/?user_id={USER_ID}")
