import jwt
from datetime import datetime, timedelta
from superadmin.models import Commission
from clientapi.models import ClientBanking

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