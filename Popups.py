from CTkMessagebox import CTkMessagebox

class InfoPopup():
    def __init__(self, msg="InfoPopup") -> None:
        CTkMessagebox(title="Info", message=f"\n{msg}\n", height=250)


class ErrorPopup():
    def __init__(self, msg="ErrorPopup") -> None:
        CTkMessagebox(title="Error", message=f"\n{msg}\n", icon="cancel", height=250)


class PromptPopup():
    def __init__(self, msg="PromptPopup", func=lambda:()) -> None:
        self.prompt = CTkMessagebox(title="Confirm", message=f"\n{msg}\n", icon="question", option_1="Yes", option_2="Cancel", height=250)
        self.func = func

        if (self.prompt.get() == "Yes"):
            self.execute()

    def execute(self):
        print(self.func)
        self.func()

    def get(self):
        return True if self.prompt.get() == "Yes" else False
