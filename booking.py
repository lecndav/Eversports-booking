import json
import sys
import requests
from datetime import date, timedelta

API = 'https://mobile.eversports.io'
CHECKOUT_API = 'https://checkout.eversports.io'


def create_cart(req, deviceId: str, uuid: str):
    req.headers['X-Apollo-Operation-Name'] = 'CreateCartFromEventBookableItem'
    with open('CreateCartFromEventBookableItem.json') as f:
        data = json.loads(f.read())

    data['variables']['bookableItemId'] = uuid
    data['variables']['deviceId'] = deviceId
    ret = req.post(f'{CHECKOUT_API}/v1', data=json.dumps(data))
    if ret.status_code != 200:
        sys.exit(1)
    j = ret.json()
    return j['data']['createCartFromEventBookableItem']['id'], j['data'][
        'createCartFromEventBookableItem']['items'][0]['id']


def set_product(req, membershipId: str, cartId: str, itemId: str):
    req.headers['X-Apollo-Operation-Name'] = 'setProductForCartItem'
    with open('setProductForCartItem.json') as f:
        data = json.loads(f.read())

    data['variables']['cartId'] = cartId
    data['variables']['itemId'] = itemId
    data['variables']['productId'] = membershipId
    ret = req.post(f'{CHECKOUT_API}/v1', data=json.dumps(data))
    if ret.status_code != 200:
        sys.exit(1)


def create_order(req, cartId: str):
    req.headers['X-Apollo-Operation-Name'] = 'ceateOrderFromCart'
    with open('ceateOrderFromCart.json') as f:
        data = json.loads(f.read())

    data['variables']['cartId'] = cartId
    ret = req.post(f'{CHECKOUT_API}/v1', data=json.dumps(data))
    if ret.status_code != 200:
        sys.exit(1)
    return ret.json()['data']['createOrderFromCart']['id']


def chekout_compelete(req, deviceId: str, orderId: str):
    req.headers['X-Apollo-Operation-Name'] = 'trackCheckoutComplete'
    with open('trackCheckoutComplete.json') as f:
        data = json.loads(f.read())

    data['variables']['orderId'] = orderId
    data['variables']['deviceId'] = deviceId
    ret = req.post(f'{CHECKOUT_API}/v1', data=json.dumps(data))
    if ret.status_code != 200:
        sys.exit(1)


def get_next_class(classes: dict, date: str):
    for c in classes:
        if c['start'] == f'{date} 06:15':
            return c


def get_class_uuid(req, classs: dict):
    ret = req.get(f'{API}/v24/event-session/{classs["sessionId"]}')
    if ret.status_code != 200:
        sys.exit(1)
    return ret.json()['uuid']


def get_classes(req, facilityId: str, date: str):
    data = {'limit': 30, 'offset': 0, 'startDate': date, 'type': 'class'}
    ret = req.get(f'{API}/v24/facility/{facilityId}/event-sessions',
                  params=data)
    if ret.status_code != 200:
        sys.exit(1)
    return ret.json()


def book_next_class(req, deviceId: str, facilityId: str, membershipId: str):
    today = date.today()
    date_str = today.strftime('%Y-%m-%d')
    classes = get_classes(req, facilityId, date_str)
    pday = today + timedelta(days=2)
    pday_str = pday.strftime('%Y-%m-%d')
    classs = get_next_class(classes, pday_str)
    uuid = get_class_uuid(req, classs)
    cartId, itemId = create_cart(req, deviceId, uuid)
    set_product(req, membershipId, cartId, itemId)
    orderId = create_order(req, cartId)
    chekout_compelete(req, deviceId, orderId)


def main():
    with open('credentials.json') as f:
        creds = json.loads(f.read())

    req = requests.session()
    req.headers['Authorization'] = f'Bearer {creds["token"]}'
    req.headers['Content-Type'] = 'application/json'

    with open('days.json') as f:
        days = json.loads(f.read())

    today = date.today()
    di = today.isoweekday()

    for day in days:
        if (day - di) % 7 == 2:
            book_next_class(req, creds['deviceId'], creds['facilityId'],
                            creds['membershipId'])
            break


if __name__ == '__main__':
    main()