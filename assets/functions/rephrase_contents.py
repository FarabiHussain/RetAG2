from writer import get_prompt_response
from icecream import ic
import threading
import time


def callback(app=None):
    ic("/assets/functions/generate_conclusion.py")

    if app is None:
        return

    conclusion_content = app.components['conclusion content'].get().strip()

    def run_model():
        app.components['generate conclusion'].component.configure(state='disabled', fg_color='light gray')
        app.components['conclusion content'].set('loading...')

        prompt=f'rephrase and reword this: {conclusion_content}'

        prompt_response = get_prompt_response(prompt)

        app.components['conclusion content'].set(prompt_response)
        app.components['generate conclusion'].component.configure(state='normal', fg_color='#33008B')


    child_thread_1 = threading.Thread(target=run_model)
    child_thread_1.start()
