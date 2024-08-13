from CTkMessagebox import CTkMessagebox

class InfoPopup():
    def __init__(self, msg="InfoPopup") -> None:
        CTkMessagebox(title="Info", message=f"\n{msg}\n")


class ErrorPopup():
    def __init__(self, msg="ErrorPopup") -> None:
        CTkMessagebox(title="Error", message=f"\n{msg}\n", icon="cancel")


class PromptPopup():
    def __init__(self, msg="PromptPopup", func=lambda:()) -> None:
        self.prompt = CTkMessagebox(title="Confirm", message=f"\n{msg}\n", icon="question", option_1="Yes", option_2="Cancel")
        self.func = func

        if (self.prompt.get() == "Yes"):
            self.execute()

    def execute(self):
        self.func()

    def get(self):
        return True if self.prompt.get() == "Yes" else False
