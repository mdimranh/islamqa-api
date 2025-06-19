from anymail.message import AnymailMessage


class userCreateEvent:
    def __init__(self, type, data):
        self.type = type
        self.data = data

    def trigger(self):
        if self.type == "created":
            self.send_email()

    def send_email(self):
        print("Sending mail -----------------------")
        message = AnymailMessage(
            subject="Welcome tou islamic-qa.",
            from_email="mdimran.cdda@gmail.com",
            body="Welcome to our site. You otp code is 1234",
            to=[f"no-reply <{self.data.email}>"],
            tags=["Onboarding"],
        )
        message.metadata = {"onboarding_experiment": "variation 1"}
        message.track_clicks = True
        message.send()

        status = message.anymail_status
        print("Mid ------------------------> ", status.message_id)
