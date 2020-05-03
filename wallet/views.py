from django.shortcuts import render
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger 
from .models import User, Wallet, Transaction

def index(request):
    return render(request, "wallet/index.html")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "wallet/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "wallet/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "wallet/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            
            user = User.objects.create_user(username, email, password)
            user.save()
            wallet = Wallet(owner=user, balance =0)
            wallet.save()
        except IntegrityError:
            return render(request, "wallet/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "wallet/register.html")


# Create your views here.
@csrf_exempt
@login_required
def add_to_wallet(request):
    # add value to wallet must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    #get data from API input in body
    data = json.loads(request.body)
    #get the wallet of current logged in user
    get_wallet = Wallet.objects.get(owner = request.user)
    current_wallet_balance = get_wallet.balance
    amount_added_to_wallet = float(data.get("amount"))
    get_wallet.balance = current_wallet_balance + amount_added_to_wallet
    get_wallet.save()
    #save one transaction for top up
    transaction = Transaction(
        from_user = request.user,
        to_user = request.user,
        transaction_value = amount_added_to_wallet,
        transaction_description = "Wallet TopUp",
        transaction_category = 6 ,
        transaction_type ="Credit",
        transaction_relevant_user = request.user      
        )
    transaction.save()
    return JsonResponse({"message": f" Amount  { amount_added_to_wallet } added succesfuly to wallet"}, status =200)


@csrf_exempt
@login_required
def transfer_to_wallet(request):
     # transfer value to wallet must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    #get data from API input in body
    data = json.loads(request.body)
    #get the from wallet as current logged in user
    get_from_wallet = Wallet.objects.get(owner = request.user)
    #check if transfer to user exists
    get_to_user_input = data.get("transfer_to")
    try:
         get_to_user = User.objects.get(username = get_to_user_input)
    #if the transfer to user does not exist return an error
    except User.DoesNotExist:
            return JsonResponse({
                "error": f"User does not exist."
            }, status=400)
    # if the transfer to user is the same as transfer from user return an error
    if get_to_user == request.user:
             return JsonResponse({
                "error": "You cannot transfer to yourself."
            }, status=400)
    get_to_wallet = Wallet.objects.get(owner=get_to_user.id)
    current_from_wallet_balance = get_from_wallet.balance
    current_to_wallet_balance = get_to_wallet.balance
    amount_transferred = float(data.get("amount"))
    #check if there is sufficient funds in wallet 
    if amount_transferred > current_from_wallet_balance:
        return JsonResponse({"error": "You don't have sufficient funds for the transaction"}, status=400)
    get_from_wallet.balance = current_from_wallet_balance - amount_transferred
    get_from_wallet.save()
    get_to_wallet.balance = current_to_wallet_balance + amount_transferred
    get_to_wallet.save()
    #create one transaction for debit
    transaction_debit = Transaction(
        from_user = request.user,
        to_user = get_to_user,
        transaction_value = -amount_transferred,
        transaction_description = data.get("description"),
        transaction_category = data.get("category")   ,
        transaction_type ="Debit",
        transaction_relevant_user = request.user        
        )
    transaction_debit.save()
    #create one transaction for credit
    transaction_credit = Transaction(
        from_user = request.user,
        to_user = get_to_user,
        transaction_value = amount_transferred,
        transaction_description = data.get("description"),
        transaction_category = 6 ,
        transaction_type ="Credit",
        transaction_relevant_user = get_to_user     
        )
    transaction_credit.save()
    return JsonResponse({"message": f" Amount  { amount_transferred } transferred sucessfully to { get_to_user }"}, status = 200 )

@login_required
def transactions(request):
    
    transactions_list = Transaction.objects.filter(transaction_relevant_user = request.user)
    transactions_list = transactions_list.order_by("-transaction_timestamp").all()  
    return JsonResponse([transactions_response.serialize() for transactions_response in transactions_list], safe=False)


@login_required
def balance(request): 
    get_wallet = Wallet.objects.get(owner = request.user)
    current_wallet_balance = get_wallet.balance
    return JsonResponse({"Balance": current_wallet_balance}, safe= False )

 

