from tkinter import PhotoImage
from tkinter.messagebox import showwarning
from windows import Window, WindowChild
from security import wireauth_get_user_data, wireauth_update_balance


images = {
    'virtual-bank-bg': "assets/virtual_bank/background.png",
    'virtual-bank-withdraw': "assets/virtual_bank/withdraw.png",
    'virtual-bank-deposit': "assets/virtual_bank/deposit.png"
}


class App(Window):
    def __init__(self, protector: Window, username: str, access_token: str):
        # App should not be a child of login window
        protector.destroy()
        super().__init__("Virtual Bank", 720, 480, False)

        # Set application background and icon
        self.set_background_image(images["virtual-bank-bg"])

        # Format access token for requests
        self.access_token_header = {'Authorization': f'Bearer {access_token}'}

        # Get user data
        self.user_data = wireauth_get_user_data(username, self.access_token_header)

        # Draw user data
        self.draw_text((350, 160), self.user_data['username'])
        self.draw_text((350, 200), self.user_data['card_number'])

        # Draw balance
        self.balance_id = self.draw_text((350, 240), '£{:.2f}'.format(float(self.user_data['balance'])))

        # Draw buttons
        withdraw_button = self.draw_image_button((243, 280), 100, 40, images["virtual-bank-withdraw"],
                                                callback=self.withdraw)
        deposit_button = self.draw_image_button((366, 280), 100, 40, images["virtual-bank-deposit"],
                                                callback=self.deposit)
        self.buttons = [withdraw_button, deposit_button]

        # Start event loop
        self.show()

    def update_balance(self):
        self.canvas.delete(self.balance_id)
        self.balance_id = self.draw_text((350, 240), '£{:.2f}'.format(float(self.user_data['balance'])))

    def withdraw(self):
        for button in self.buttons: button['state'] = 'disabled'
        window = WindowChild(self, "Withdraw", 250, 130, False)

        def try_withdraw():
            error = False
            try:
                amount = float(amount_box.get())
            except ValueError:
                showwarning("Error", "Please enter a valid number")
                error = True
                window.lift()

            if not error:

                if amount > float(self.user_data['balance']):
                    showwarning("Error", "You do not have enough money to withdraw that amount")
                    window.lift()
                elif not float(amount) > 0:
                    showwarning("Error", "Amount cannot be negative or zero")
                    window.lift()
                else:
                    self.user_data['balance'] = "{:.2f}".format(float(self.user_data['balance']) - amount)
                    wireauth_update_balance(self.user_data['username'],
                                            {'balance': self.user_data['balance']},
                                            self.access_token_header)
                    self.update_balance()
                    self.on_close_withdraw_or_deposit(window)

        # Draw window UI
        window.draw_text((125, 18), "Enter Amount", font='TkDefaultFont 18')
        amount_box = window.draw_entry_box((46, 42), 159, 29)
        window.draw_image_button((73, 82), 100, 40, images["virtual-bank-withdraw"],
                                 callback=try_withdraw)

        window.protocol("WM_DELETE_WINDOW", lambda: self.on_close_withdraw_or_deposit(window))

    def deposit(self):
        for button in self.buttons: button['state'] = 'disabled'
        window = WindowChild(self, "Deposit", 250, 130, False)

        def try_deposit():
            error = False
            try:
                amount = float(amount_box.get())
            except ValueError:
                showwarning("Error", "Please enter a valid number")
                error = True
                window.lift()

            if not error:

                if not (0 < float(amount) < 10000):
                    showwarning("Error", "Amount must be between 0.01 and 9999.99")
                    window.lift()
                elif float(self.user_data['balance']) + float(amount) > 9999.99:
                    showwarning("Error", "You cannot have more than £9999.99 in your account")
                    window.lift()
                else:
                    self.user_data['balance'] = "{:.2f}".format(float(self.user_data['balance']) + amount)
                    wireauth_update_balance(self.user_data['username'],
                                            {'balance': self.user_data['balance']},
                                            self.access_token_header)
                    self.update_balance()
                    self.on_close_withdraw_or_deposit(window)

        # Draw window UI
        window.draw_text((125, 18), "Enter Amount", font='TkDefaultFont 18')
        amount_box = window.draw_entry_box((46, 42), 159, 29)
        window.draw_image_button((73, 82), 100, 40, images["virtual-bank-deposit"],
                                 callback=try_deposit)

        window.protocol("WM_DELETE_WINDOW", lambda: self.on_close_withdraw_or_deposit(window))

    def on_close_withdraw_or_deposit(self, window):
        for button in self.buttons: button['state'] = 'normal'
        window.destroy()
