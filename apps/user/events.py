from anymail.message import AnymailMessage
from apps.events.base import BaseEvent

class userCreateEvent(BaseEvent):
    def action_email(self):
        message = AnymailMessage(
            subject="Welcome tou islamic-qa.",
            from_email="Islam QA <mdimran.cdda@gmail.com>",
            body="Welcome to our site. You otp code is 1234",
            to=[f"no-reply <{self.payload.get('email')}>"],
            tags=["Onboarding"],
        )
        message.metadata = {"onboarding_experiment": "variation 1"}
        message.track_clicks = True
        message.send()

        status = message.anymail_status
        print("Mid ------------------------> ", status.message_id)

    def action_notification(self):
        print("notification send ------------------------>", self.payload)
