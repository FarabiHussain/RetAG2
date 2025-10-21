from Popups import ErrorPopup
from actions import update_total_row, generate_row_contents

def callback(app=None):

    if app is None:
        print("app components not provided")
        return

    try:

        cart_obj=app.components.get('cart')
        final_row_contents, final_row_infos = [], []

        # first reset the cart
        cart_obj.reset()
        cart_obj.tools.buttons[3].configure(fg_color='white', text_color="white", state='disabled', text="$0.00")
        cart_obj.tools.buttons[4].configure(fg_color='white', text_color="white", state='disabled', text="$0.00")

        # by default, we will add these three items in the invoice template
        # amounts shows below are not refundable
        template_row_contents = [
            {
                'service': 'File Opening Fee',
                'quantity': '1',
                'rate': '500.00',
                'tax_rate': 12.0,
                'gst': 7.0,
                'pst': 5.0,
            },
            {
                'service': 'Eligibility Consultation with Lawyer',
                'quantity': '1',
                'rate': '275.00',
                'tax_rate': 12.0,
                'gst': 7.0,
                'pst': 5.0,
            },
            {
                'service': 'Review and Preparation by Case Manager',
                'quantity': '1',
                'rate': '225.00',
                'tax_rate': 12.0,
                'gst': 7.0,
                'pst': 5.0,
            }
        ]


        # used to calculate concession
        running_total = 0.0

        # append the amounts from the template
        for i in range(len(template_row_contents)):
            new_row, new_row_info = generate_row_contents(app_components=app.components, override_row_content=template_row_contents[i])
            final_row_contents.append(new_row)
            final_row_infos.append(new_row_info)
            running_total += float(new_row_info['price'])

        # apply concession only if the value is less than 1000
        # for services costing more than 1000, no concession is applied as it goes into payment plans
        if float(app.components.get('invoice total').get()) <= 1000.0:
            concession_row, concession_row_info = generate_row_contents(
                app_components=app.components, 
                override_row_content={
                    'service': 'Concession Discount',
                    'quantity': '1',
                    'rate': float(app.components.get('invoice total').get()) - running_total,
                    'tax_rate': 0.0,
                    'gst': 0.0,
                    'pst': 0.0,
                }
            )

            final_row_contents.append(concession_row)
            final_row_infos.append(concession_row_info)

        if float(app.components.get('paid amount').get()) > 0:
            paid_row, paid_row_info = generate_row_contents(
                app_components=app.components, 
                override_row_content={
                    'service': 'Amount Paid',
                    'quantity': '1',
                    'rate': -float(app.components.get('paid amount').get()),
                    'tax_rate': 0.0,
                    'gst': 0.0,
                    'pst': 0.0,
                }
            )

            final_row_contents.append(paid_row)
            final_row_infos.append(paid_row_info)

        # finally, add all rows to the cart and calculate total
        app.components.get('cart').add(row_contents=final_row_contents, row_info=final_row_infos)
        update_total_row(cart_obj)

    except Exception as e:
        ErrorPopup(e)