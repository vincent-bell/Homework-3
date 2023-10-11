from windows import Window, WindowChild
from tkinter.messagebox import showwarning
from security import wireauth_try_login, wireauth_try_register, validate_registration_fields
from security import wireauth_get_user_data, wireauth_update_balance


images = {
    'wire-auth-bg': "assets/wire_auth/background.png",
    'wire-auth-sign-up': "assets/wire_auth/sign_up.png",
    'wire-auth-sign-in': "assets/wire_auth/sign_in.png",
    'wire-auth-sign-up-bg': "assets/wire_auth/sign_up/background.png",
    'virtual-bank-bg': "assets/virtual_bank/background.png",
    'virtual-bank-withdraw': "assets/virtual_bank/withdraw.png",
    'virtual-bank-deposit': "assets/virtual_bank/deposit.png",
    'virtual-bank-text': "assets/virtual_bank/text.png"
}


def main_app(root: Window, username: str, access_token: str):
    root.destroy() # App should not be a child of wire auth window
    window = Window("Virtual Bank", 720, 480, False)
    window.set_background_image(images["virtual-bank-bg"])

    access_token_f = {'Authorization': f'Bearer {access_token}'}
    data = wireauth_get_user_data(username, access_token_f)

    window.draw_text((350, 160), data['username'])
    window.draw_text((350, 200), data['card_number'])

    # Probably bad practice but it works
    global balance_id
    balance_id = window.draw_text((350, 240), '£{:.2f}'.format(float(data['balance'])))

    def update_balance():
        global balance_id
        window.canvas.delete(balance_id)
        balance_id = window.draw_text((350, 240), '£{:.2f}'.format(float(data['balance'])))

    def withdraw(buttons):

        def on_close(window):
            for button in buttons: button['state'] = 'normal'
            window.destroy()

        # TODO - Seriously need to refactor this code
        # TODO - Fix withdraw and deposit UI
        # TODO - Major problems with floating point arithmetic and negative numbers

        def try_withdraw(amount):
            error = False
            try:
                amount = float(amount)
            except ValueError:
                showwarning("Error", "Please enter a valid number")
                error = True
                windowchild.lift()
            if not error:
                if amount > float(data['balance']):
                        showwarning("Error", "You do not have enough money to withdraw that amount")
                else:
                    data['balance'] = float(data['balance']) - amount
                    wireauth_update_balance(username, {'balance': data['balance']}, access_token_f)
                    update_balance()
                    on_close(windowchild)

        for button in buttons: button['state'] = 'disabled'

        windowchild = WindowChild(window, "Withdraw", 250, 130, False)
        windowchild.draw_image(images['virtual-bank-text'], 154, 33, (48, 9))
        amount_box = windowchild.draw_entry_box((46, 42), 159, 29)
        windowchild.draw_image_button((73, 82), 100, 40, images["virtual-bank-withdraw"],
                                 callback=lambda: try_withdraw(amount_box.get()))
        windowchild.protocol("WM_DELETE_WINDOW", lambda: on_close(windowchild))


    def deposit(buttons):

        def on_close(window):
            for button in buttons: button['state'] = 'normal'
            window.destroy()

        def try_deposit(amount):
            error = False
            try:
                amount = float(amount)
            except ValueError:
                showwarning("Error", "Please enter a valid number")
                error = True
                windowchild.lift()
            if not error:
                data['balance'] = float(data['balance']) + amount
                wireauth_update_balance(username, {'balance': data['balance']}, access_token_f)
                update_balance()
                on_close(windowchild)

        for button in buttons: button['state'] = 'disabled'

        windowchild = WindowChild(window, "Deposit", 250, 130, False)
        windowchild.draw_image(images['virtual-bank-text'], 154, 33, (48, 9))
        amount_box = windowchild.draw_entry_box((46, 42), 159, 29)
        windowchild.draw_image_button((73, 82), 100, 40, images["virtual-bank-deposit"],
                                 callback=lambda: try_deposit(amount_box.get()))
        windowchild.protocol("WM_DELETE_WINDOW", lambda: on_close(windowchild))

    buttons = []
    withdraw_button = window.draw_image_button((243, 280), 100, 40, images["virtual-bank-withdraw"],
                                               callback=lambda: withdraw(buttons))
    deposit_button = window.draw_image_button((366, 280), 100, 40, images["virtual-bank-deposit"],
                                              callback=lambda: deposit(buttons))
    buttons.extend([withdraw_button, deposit_button])
    window.show()


def wireauth_app():
    def wire_auth_on_close_sign_up(window, buttons):
        for button in buttons: button['state'] = 'normal'
        window.destroy()

    def wire_auth_open_sign_up(window, buttons):
        for button in buttons: button['state'] = 'disabled'
        window = WindowChild(window, "Wire Authentication - Sign Up", 480, 640, False)
        window.set_background_image(images["wire-auth-sign-up-bg"])

        username_box = window.draw_entry_box((159, 210), 159, 29)
        email_box = window.draw_entry_box((158, 278), 159, 29)
        password_box = window.draw_entry_box((160, 348), 159, 29)
        confirm_password_box = window.draw_entry_box((161, 420), 159, 29)
        card_number_box = window.draw_entry_box((160, 497), 159, 29)

        def try_register():
            username = username_box.get()
            email = email_box.get()
            password = password_box.get()
            confirm_password = confirm_password_box.get()
            card_number = card_number_box.get()

            data = {
                'username': username,
                'email': email,
                'password': password,
                'confirm_password': confirm_password,
                'card_number': card_number
            }

            if validate_registration_fields(data):
                data.pop('confirm_password')
                if wireauth_try_register(data)['status'] == 'success':
                    wire_auth_on_close_sign_up(window, buttons)

        window.draw_image_button((200, 565), 88, 36, images["wire-auth-sign-up"], callback=try_register)

        window.wm_protocol("WM_DELETE_WINDOW", lambda: wire_auth_on_close_sign_up(window, buttons))

    window = Window("Wire Authentication", 720, 480, False)
    window.set_background_image(images["wire-auth-bg"])

    username_box = window.draw_entry_box((291, 311), 149, 27)
    password_box = window.draw_entry_box((288, 381), 149, 27)

    def try_authenticate():
        username = username_box.get()
        password = password_box.get()
        response = wireauth_try_login({'username': username, 'password': password})
        if response['status'] == 'success':
            main_app(window, username, response['access_token'])
        else:
            showwarning("Error", response['message'])

    buttons = []
    sign_up_button = window.draw_image_button((89, 332), 88, 36, images["wire-auth-sign-up"],
                                              callback=lambda: wire_auth_open_sign_up(window, buttons))
    sign_in_button = window.draw_image_button((296, 429), 88, 36, images['wire-auth-sign-in'],
                                              callback=try_authenticate)
    buttons.extend([sign_up_button, sign_in_button])

    window.show()


if __name__ == '__main__':
   wireauth_app()
