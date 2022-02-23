from kavenegar import *
from django.conf import settings
import ghasedak


def send_otp_code(phone_number, code):
    try:
        api = KavenegarAPI(settings.KAVENEGAR_APIKEY)
        params = {
            'sender': '',
            'receptor': phone_number,
            'message': f'کد تایید شما{code}'
        }
        response = api.sms_send(params)
        print(response)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)


def send_otp_code_gh(phone_number, code):

    sms = ghasedak.Ghasedak(settings.GHASEDAK_APIKEY)
    sms.send({'message': f"کد تایید شما {code}",
              'receptor': phone_number,
              'linenumber': "10008566"})

