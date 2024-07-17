from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from lidz.models import Client, Message, Debt

# View to get all clients
@api_view(['GET'])
def get_clients(request):
    clients = Client.objects.all()
    return Response([
        {
            'id': client.id,
            'name': client.name,
            'rut': client.rut,
            'salary': client.salary,
            'savings': client.savings
        } for client in clients
    ])

# View to get single client, with its corresponding messages and debts
@api_view(['GET'])
def get_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    messages = Message.objects.filter(client=client)
    debts = Debt.objects.filter(client=client)
    return Response({
        'name': client.name,
        'rut': client.rut,
        'salary': client.salary,
        'savings': client.savings,
        'messages': [
            {
                'text': message.text,
                'role': message.role,
                'sent_at': message.sent_at
            } for message in messages
        ],
        'debts': [
            {
                'institution': debt.institution,
                'amount': debt.amount,
                'due_date': debt.due_date
            } for debt in debts
        ]
    })

# View to get clients where the last message was sent 7 days ago or more
@api_view(['GET'])
def get_clients_last_message(request):
    seven_days_ago = timezone.now() - timedelta(days=7)
    clients = Client.objects.filter(message__sent_at__lt=seven_days_ago).distinct()
    return Response([
        {
            'id': client.id,
            'name': client.name,
            'rut': client.rut,
            'salary': client.salary,
            'savings': client.savings
        } for client in clients
    ])
# View to create a new client, with its corresponding messages and debts
@api_view(['POST'])
def create_client(request):
    data = request.data
    client = Client(
        name=data.get('name'),
        rut=data.get('rut'),
        salary=data.get('salary'),
        savings=data.get('savings')
    )
    client.save()
    for message_data in data.get('messages', []):
        message = Message(
            text=message_data.get('text'),
            role=message_data.get('role'),
            client=client,
            sent_at=message_data.get('sentAt')
        )
        message.save()
    for debt_data in data.get('debts', []):
        debt = Debt(
            amount=debt_data.get('amount'),
            institution=debt_data.get('institution'),
            due_date=debt_data.get('dueDate'),
            client=client
        )
        debt.save()
        
    # Return the same as request.data, but adding the id of the new client
    return Response({
        'id': client.id,
        'name': client.name,
        'rut': client.rut,
        'salary': client.salary,
        'savings': client.savings,
        'messages': data.get('messages', []),
        'debts': data.get('debts', [])
    }, status=status.HTTP_201_CREATED)

# View to get the chance of that client to actually buy a house, considering his salary, savings, interest (messages) and debts
@api_view(['GET'])
def get_score(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    # Value of the house (UF at 37597)
    HOUSE_VALUE = 3000*37597
    
    # We get the client's information
    salary = client.salary
    savings = client.savings
    messages = Message.objects.filter(client=client)
    debts = Debt.objects.filter(client=client)

    # Now that we have the information, we calculate the score
    # First filter is the messages, if there are no messages, the score is inmediately 0
    if len(messages) == 0:
        return Response({
            'score': 0
        })
    
    # If there are more messages, we calculate a score between -10 and 20 for the messages
    interest_score = -10
    for message in messages:
        if message.role == 'client':
            interest_score += 1
        else:
            interest_score += 0.5
    interest_score = min(interest_score, 20)
    
    # Now we calculate the savings score, which is between 0 and 20. If the savings are less than 3% of the house value, the score is 0
    savings_score = 0
    savings_percentage = savings/HOUSE_VALUE
    SAVINGS_NORMALIZATION =  10
    if savings_percentage >= 0.03:
        savings_score = min(savings_percentage*20*SAVINGS_NORMALIZATION, 20)
    
    # Now we calculate the debts score, which is between 20 and -20. If all the debts are from this month, they don't affect the score; if they are from last month to 2 years ago, they affect the score negatively
    debts_score = 0
    for debt in debts:
      # If the debt is from this month, we don't do anything
      if debt.due_date >= timezone.now() - timedelta(days=30):
        continue
      # If the debt is from last month to 2 years ago, we decrease the score evenly from 0 to -24 (every month is -1)
      if debt.due_date < timezone.now() - timedelta(days=30) and debt.due_date >= timezone.now() - timedelta(days=365*2):
        debts_score -= (timezone.now() - debt.due_date).days/30
    # If no debts, score is 20
    if len(debts) == 0:
        debts_score = 20
    
    # Now we calculate the salary score, which is between 0 and 20. If the salary is less than 0.5% of the house value, the score is 0
    salary_score = 0
    salary_percentage = salary/HOUSE_VALUE
    SALARY_NORMALIZATION =  100
    if salary_percentage >= 0.005:
        salary_score = min(salary_percentage*20*SALARY_NORMALIZATION, 20)
        
    # Now we calculate bonuses for the client (this will be for atypical/border cases)
    bonus_score = 0
    # If the client has more than 20% of the house value in savings and no debts, we add 10 to the score
    if savings_percentage >= 0.2 and len(debts) == 0:
        bonus_score += 10
    # If the client has a salary higher than 5% of the house value, we add 10 to the score
    if salary_percentage >= 0.05:
        bonus_score += 10

    # Now we calculate the final score
    score = interest_score + savings_score + debts_score + salary_score + bonus_score
    
    # Now if the score is less than 0, we return 0; if it's more than 100, we return 100
    score = max(0, score)
    score = min(100, score) 
    
    return Response({
        'score': score,
        #'interest_score': interest_score,
        #'savings_score': savings_score,
        #'debts_score': debts_score,
        #'salary_score': salary_score,
        #'bonus_score': bonus_score
    })
    
    
    