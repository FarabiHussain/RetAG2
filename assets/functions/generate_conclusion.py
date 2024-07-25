from writer import get_prompt_response
from icecream import ic
import threading
import time


def callback(app=None):
    ic("/assets/functions/generate_conclusion.py")

    if app is None:
        return

    guest_fields={}
    purpose_of_visit = app.components['purpose of visit'].get().strip()
    address_in_Canada = app.components['address in Canada'].get().strip()
    arrival_date = app.components['arrival date'].get().strip()
    departure_date = app.components['departure date'].get().strip()
    bearer_of_expenses = app.components['bearer of expenses'].get().strip()
    attached_documents = app.components['attached documents'].get().strip()
    country_of_residence = app.components['country of residence'].get().strip()


    for i in range(1,6):
        guest_fields[f"guest {i} full name"] = app.components[f"guest {i} full name"].get().strip()
        guest_fields[f"guest {i} date of birth"] = app.components[f"guest {i} date of birth"].get().strip()
        guest_fields[f"guest {i} passport no."] = app.components[f"guest {i} passport no."].get().strip()
        guest_fields[f"guest {i} address"] = app.components[f"guest {i} address"].get().strip()
        guest_fields[f"guest {i} phone number"] = app.components[f"guest {i} phone number"].get().strip()
        guest_fields[f"guest {i} email address"] = app.components[f"guest {i} email address"].get().strip()
        guest_fields[f"guest {i} occupation"] = app.components[f"guest {i} occupation"].get().strip()
        guest_fields[f"guest {i} country of citizenship"] = app.components[f"guest {i} country of citizenship"].get().strip()
        guest_fields[f"guest {i} relation to host 1"] = app.components[f"guest {i} relation to host 1"].get().strip()


    def run_model():
        app.components['generate conclusion'].component.configure(state='disabled', fg_color='light gray')
        app.components['conclusion content'].set('loading...')

        prompt=[f'Write a closing paragraph for an invitation letter to be submitted to IRCC including the following information:\nI am inviting the following people:']

        for i in range(1,6):
            if guest_fields[f'guest {i} full name'] != '':
                guest_name = guest_fields[f'guest {i} full name']
                relation_to_host = guest_fields[f'guest {i} relation to host 1']

                prompt.append(f'My {relation_to_host}, {guest_name}.')

        prompt.append(f'The purpose of their visit is {purpose_of_visit}.')
        prompt.append(f'They will be staying at {address_in_Canada}.')
        prompt.append(f'They plan to visit from {arrival_date} to {departure_date}.')

        
        prompt.append(f'They have significant ties to their home country of {country_of_residence} in the form of property and jobs, so they will not overstay their validity.')
        prompt.append('Make sure to mention each and every point above. Reword and rephrase the points above. Use full names instead of Ms. and Mr.')

        prompt_response = get_prompt_response("\n".join(prompt))

        app.components['conclusion content'].set(prompt_response)
        app.components['generate conclusion'].component.configure(state='normal', fg_color='#33008B')


    child_thread_1 = threading.Thread(target=run_model)
    child_thread_1.start()
    # time.sleep(5)
    # child_thread_1.join()
