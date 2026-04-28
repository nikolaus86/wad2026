

# # Пример плохого кода
class Email:
    def send(self, message):
        print(f"Sending email: {message}")

class Sms:
    def send(self, message):
        print(f"Sending Sms: {message}")

class Notification:
    def __init__(self):
        self.email = Email()
        self.sms = Sms()

    def notify_email(self, message):
        self.email.send(message)

    def notify_sms(self, message):
        self.sms.send(message)

notification = Notification()
notification.notify_email("Hello, world!")
notification.notify_sms("Hello, world!")


# Пример хорошего кода

class Email:
    def send(self, message):
        print(f"Sending email: {message}")

class Sms:
    def send(self, message):
        print(f"Sending Sms: {message}")

class Notification:
    def __init__(self, method):
        self.method = method

    def notify(self, message):
        self.method.send(message)

notification = Notification(Email())
notification.notify("Hello, world!")

notification = Notification(Sms())
notification.notify("Hello, world!")

