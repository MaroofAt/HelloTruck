from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now=False , auto_now_add=True , editable=False)
    updated_at = models.DateTimeField(auto_now=True , auto_now_add=False , editable=False)
    class Meta:
        abstract = True

def check_mobile_number(mobile_number) -> bool:
    mobile_number = mobile_number.replace(" ", "") # remove all whitespaces
    length = len(mobile_number)
    if length < 9: return False # 987654321 | +987654321 | 0987654321
    if length > 13: return False # +963987654321
    if length < 13 and length > 10: return False
    if length == 9 and mobile_number[0] is not '9': return False # if the number is global it has to have +000 (ex. +963987654321)
    if length == 10 and mobile_number[0] not in ['0', '+']: return False
    for i in range(0, length):
        char = mobile_number[i]
        if char is not '+':
            char = int(char)
            if char > 9 or char < 0: return False
        elif i > 0: return False # there is '+' but not at first
    
    return True

def normalize_mobile_number(mobile_number) -> str:
    # we have to reach +963987654321
    # mobile_number = mobile_number.replace(" ", "") # remove all whitespaces
    if mobile_number is None: return "" 
    length = len(mobile_number) 
    if length == 9: return "+963" + mobile_number
    if length == 10: return "+963" + mobile_number[1:]
    # case length == 13:
    return mobile_number
    