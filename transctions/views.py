from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from datetime import timedelta
from .models import *
from .serializers import *
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum
from django.db.models import F, ExpressionWrapper, DateField, Sum
from django.db.models.functions import Now
from .models import Transction, Friend

from django.db.models import DurationField
# from django.shortcuts import render

def index(request):
    return render(request, 'transctions/index.html')

def create_transaction_form(request):
    return render(request, 'transctions/create.html')

@api_view(['GET'])
def dashboard_view(request):
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response({"error": "user_id is required in query params"}, status=400)

    try:
        me = Friend.objects.get(user_id=user_id)
    except Friend.DoesNotExist:
        return Response({"error": "Friend entry not found for user"}, status=404)

    today = timezone.now().date()
    result = []

    annotated_transactions = Transction.objects.annotate(
        repay_duration=ExpressionWrapper(
            F('repay_within_days') * timedelta(days=1),
            output_field=DurationField()
        ),
        repayment_date=ExpressionWrapper(
            F('date') + F('repay_duration'),
            output_field=DateField()
        )
    )
    print("Annotated Transactions:", list(annotated_transactions.values('date', 'repay_within_days', 'repayment_date', 'payer', 'receiver', 'amount')))
    for week in range(8):
        start = today + timedelta(weeks=week)
        end = start + timedelta(days=6)

        week_data = {
            "week": week + 1,
            "from_date": str(start),
            "to_date": str(end),
            "to_receive_total": 0,
            "to_receive_breakdown": [],
            "to_pay_total": 0,
            "to_pay_breakdown": []
        }

        # --- To Receive ---
        to_receive_qs = annotated_transactions.filter(
            receiver=me,
            repayment_date__range=(start, end)
        ).values('payer__user__username').annotate(total=Sum('amount'))

        for entry in to_receive_qs:
            friend = entry.get("payer__user__username") or "Unknown"
            amount = entry.get("total") or 0
            week_data["to_receive_total"] += amount
            week_data["to_receive_breakdown"].append({
                "friend": friend,
                "amount": amount
            })

        # --- To Pay ---
        to_pay_qs = annotated_transactions.filter(
            payer=me,
            repayment_date__range=(start, end)
        ).values('receiver__user__username').annotate(total=Sum('amount'))
        print("Receive:", to_receive_qs)
        print("Pay:", to_pay_qs)

        for entry in to_pay_qs:
            friend = entry.get("receiver__user__username") or "Unknown"
            amount = entry.get("total") or 0
            week_data["to_pay_total"] += amount
            week_data["to_pay_breakdown"].append({
                "friend": friend,
                "amount": amount
            })

        result.append(week_data)

    return Response(result)

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
@api_view(['POST'])
def create_transction(request):
   
    payer_id = request.data.get('payer_id')
    reciever_id  = request.data.get('reciever_id')
    amount = request.data.get('amount')
    repay_within_days = request.data.get('repay_within_days')

    if not all([payer_id, reciever_id, amount, repay_within_days]):
        return Response({'error' : 'All field are required'}, status=400)
    
    try:
        payer = Friend.objects.get(id=payer_id)
        receiver = Friend.objects.get(id=reciever_id)
    except Friend.DoesNotExist:
        return Response({'error': 'Payer or Receiver not found'}, status=404)

    transaction = Transction.objects.create(
        payer=payer,
        receiver=receiver,
        amount=amount,
        repay_within_days=repay_within_days
    )

    serializer = TransctionSerializers(transaction)
    return Response(serializer.data, status=201)


