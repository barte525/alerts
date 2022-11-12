from crypto.models import Alert
from crypto.services.send_email import EmailSender


def check_alert(asset, asset_values):
    alerts_list_from_origin_asset = Alert.objects.filter(origin_asset_name=asset)
    alerts_in_origin_asset = Alert.objects.filter(currency=asset)
    currencies = alerts_list_from_origin_asset.values_list('currency', flat=True)
    assets = alerts_in_origin_asset.values_list('origin_asset_name', flat=True)
    new_origin_asset_price = 0
    for asset_r in asset_values:
        if asset_r['assetIdentifier'] == asset:
            new_origin_asset_price = asset_r['value']
    asset_dict_from_origin_asset = {asset_r['assetIdentifier']: asset_r['value'] * new_origin_asset_price for
                                    asset_r in asset_values if asset_r['assetIdentifier'] in currencies}
    asset_dict_in_origin_asset = {asset_r['assetIdentifier']: asset_r['value'] / new_origin_asset_price for
                                  asset_r in asset_values if asset_r['assetIdentifier'] in assets}
    for alert in alerts_list_from_origin_asset:
        new_price = asset_dict_from_origin_asset[alert.currency]
        inner_check_alert(alert, new_price)
    for alert in alerts_in_origin_asset:
        new_price = asset_dict_in_origin_asset[alert.origin_asset_name]
        inner_check_alert(alert, new_price)


def inner_check_alert(alert, new_price):
    if (new_price > alert.alert_value) == alert.alert_when_increases or new_price == alert.alert_value:
        EmailSender().send_email(alert.email, alert.origin_asset_name, alert.alert_value, alert.currency, "")
        alert.active = False
        alert.save()
