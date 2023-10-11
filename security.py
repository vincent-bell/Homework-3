import requests
from tkinter.messagebox import showwarning
from validate_email import validate_email


# Post requests
wireauth_try_login = lambda json: requests.post('http://127.0.0.1:5000/user/login', json=json).json()
wireauth_try_register = lambda json: requests.post('http://127.0.0.1:5000/user/create',
                                                   json=json).json()
# Get/Put requests
wireauth_get_user_data = lambda username, headers: requests.get(f'http://127.0.0.1:5000/user/{username}',
                                                                   headers=headers).json()
wireauth_update_balance = lambda username, json, headers: requests.put(f'http://127.0.0.1:5000/user/{username}/balance',
                                                                          json=json, headers=headers).json()


def validate_credit_card_no(digits: str):
    for digit in digits:
        if not digit.isdigit():
            return False

    # Static digit count
    digit_count = 16

    # Store digits in array
    digit_array = [int(digit) for digit in digits]

    # Luhn algorithm
    for i in range(digit_count-2, -1, -2):
        digit_array[i] *= 2
        if digit_array[i] > 9:
            digit_array[i] -= 9

    if sum(digit_array) % 10 == 0:
        return True
    return False


def validate_registration_fields(fields: dict):
    if fields['username'] == '':
        showwarning('Invalid Username', 'Username cannot be empty')
        return False
    elif len(fields['username']) < 8 or len(fields['username']) > 22:
        showwarning('Invalid Username', 'Username must be between 8 and 22 characters')
        return False
    elif len(fields['email']) >= 25:
        showwarning('Invalid Email', 'Email must be shorter than 25 characters')
        return False
    elif not validate_email(fields['email']):
        showwarning('Invalid Email', 'Email is invalid')
        return False
    elif len(fields['password']) < 8:
        showwarning('Invalid Password', 'Password must be at least 8 characters')
        return False
    elif fields['password'] != fields['confirm_password']:
        showwarning('Invalid Password', 'Passwords do not match')
        return False
    elif len(fields['card_number']) != 16:
        showwarning('Invalid Card Number', 'Card number is invalid')
        return False
    elif not validate_credit_card_no(fields['card_number']):
        showwarning('Invalid Card Number', 'Card number is invalid')
        return False
    return True
