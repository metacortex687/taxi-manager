from django.core.exceptions import ValidationError


def vin_validator(value:str):
    if len(value) < 17:
        raise ValidationError("VIN номер не может быть короче 17 символов")

    if len(value) > 17:
        raise ValidationError("VIN номер не может быть длиннее 17 символов")

    for c in value:
        if c not in "0123456789ABCDEFGHJKLMNPRSTUVWXYZ":
            raise ValidationError("В VIN допустимо использовать только: 0 1 2 3 4 5 6 7 8 9 A B C D E F G H J K L M N P R S T U V W X Y Z")
