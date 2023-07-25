import jwt
from datetime import datetime, timedelta
from superadmin.models import Commission
from clientapi.models import ClientBanking
from django.utils import timezone
from .models import BookProperty


def generate_token(id):
    payload = {
        'user_id': str(id),
        'exp': datetime.utcnow() + timedelta(days=1)  
    }

    jwt_token = jwt.encode(payload, 'secret', algorithm='HS256')

    return jwt_token



def get_transfers(data):
        owner = data['property'].owner
        commission = Commission.objects.filter(client=owner).first()
        
        if commission:
            commission_percent = int(commission.commission_percent)  # Convert to integer

        banking_details = ClientBanking.objects.filter(client=owner).first()
        if banking_details:
            account_id = banking_details.account_id

        total_amount = data['amount']
        commission_amount = total_amount * commission_percent / 100
        transfer_amount = total_amount - commission_amount

        transfers_data = [{
            "account": account_id,
            "amount": transfer_amount * 100,
            "currency": "INR"
        }]
        return transfers_data



def is_booking_overlapping(property, start_date, end_date):
    existing_bookings = BookProperty.objects.filter(property=property)
    for booking in existing_bookings:
        if (start_date <= booking.end_date) and (end_date >= booking.start_date):
            return True
    return False
