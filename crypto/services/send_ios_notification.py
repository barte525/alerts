
from channels.layers import get_channel_layer

from asgiref.sync import async_to_sync
from crypto.const import MESSAGE_TEXT


def send_ios_notification(notifications):
    list_of_notifications = parse_dict_to_list_of_jl(notifications)
    chanel_layer = get_channel_layer()
    print(" list", list_of_notifications)
    async_to_sync(chanel_layer.group_send)(
        'test',
        {
            'type': 'chat_message',
            'message': list_of_notifications
        })


def parse_dict_to_list_of_jl(notifications):
    result = []
    for notication in notifications:
        email = notication['email']
        name, price, currency = notication['alert_msg']
        result.append({'email': email, 'alert_msg': MESSAGE_TEXT.format(asset_name=name, currency=currency, price=price).strip()})
    return result
