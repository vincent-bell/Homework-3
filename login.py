from tkinter.messagebox import showwarning
from windows import Window, WindowChild
from security import wireauth_try_login, wireauth_try_register, validate_registration_fields


images = {
    'wire-auth-bg': "assets/wire_auth/background.png",
    'wire-auth-sign-up': "assets/wire_auth/sign_up.png",
    'wire-auth-sign-in': "assets/wire_auth/sign_in.png",
    'wire-auth-sign-up-bg': "assets/wire_auth/sign_up/background.png",
}


class LoginScreen(Window):
    def __init__(self, protected_app: Window):
        super().__init__("Wire Authentication", 720, 480, False)
        self.protected_app = protected_app

        # Set application background and icon
        self.set_background_image(images["wire-auth-bg"])

        # Draw entry boxes
        self.username_box = self.draw_entry_box((291, 311), 149, 27)
        self.password_box = self.draw_entry_box((288, 381), 149, 27)

        # Draw buttons
        sign_in_button = self.draw_image_button((296, 429), 88, 36, images['wire-auth-sign-in'],
                                                callback=self.try_login)
        sign_up_button = self.draw_image_button((89, 332), 88, 36, images["wire-auth-sign-up"],
                                                callback=self.open_sign_up)
        self.buttons = [sign_in_button, sign_up_button]

        # Start event loop
        self.show()

    def try_login(self):
        username = self.username_box.get()
        password = self.password_box.get()

        response = wireauth_try_login({'username': username, 'password': password})
        if response['status'] == 'success':
            self.protected_app(self, username, response['access_token'])
        else:
            showwarning("Error", response['message'])


    def open_sign_up(self):
        for button in self.buttons: button['state'] = 'disabled'
        window = WindowChild(self, "Wire Authentication - Sign Up", 480, 640, False)
        window.set_background_image(images["wire-auth-sign-up-bg"])

        # Draw entry boxes
        username_box = window.draw_entry_box((159, 210), 159, 29)
        email_box = window.draw_entry_box((158, 278), 159, 29)
        password_box = window.draw_entry_box((160, 348), 159, 29)
        confirm_password_box = window.draw_entry_box((161, 420), 159, 29)
        card_number_box = window.draw_entry_box((160, 497), 159, 29)

        def try_register():
            data = {
                'username': username_box.get(),
                'email': email_box.get(),
                'password': password_box.get(),
                'confirm_password': confirm_password_box.get(),
                'card_number': card_number_box.get()
            }

            if validate_registration_fields(data):
                data.pop('confirm_password')
                if wireauth_try_register(data)['status'] == 'success':
                    self.on_close_sign_up(window)

        window.draw_image_button((200, 565), 88, 36, images["wire-auth-sign-up"], callback=try_register)
        window.wm_protocol("WM_DELETE_WINDOW", lambda: self.on_close_sign_up(window))

    def on_close_sign_up(self, window):
        for button in self.buttons: button['state'] = 'normal'
        window.destroy()
