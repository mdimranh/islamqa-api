from anymail.message import AnymailMessage
from apps.events.base import BaseEvent
from django.template.loader import render_to_string

class userCreateEvent(BaseEvent):
    def action_email(self):
        body = render_to_string("email/verify_email.html", self.payload)
        message = AnymailMessage(
            subject="Welcome tou islamic-qa.",
            from_email="Islam QA <mdimran.cdda@gmail.com>",
            to=[f"no-reply <{self.payload.get('email')}>"],
            tags=["Onboarding"],
        )
        message.attach_alternative(body, "text/html")
        message.metadata = {"onboarding_experiment": "variation 1"}
        message.track_clicks = True
        message.send()

        status = message.anymail_status
        print("Mid ------------------------> ", status.message_id)

    def action_notification(self):
        print("notification send ------------------------>", self.payload)
