from datetime import datetime, date, timedelta
from django.shortcuts import render, redirect
from django.http import JsonResponse
from mongodb import Mongodb
from ws_webapp.utilities import *

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

from django.conf import settings

from rest_framework.decorators import api_view
from rest_framework.views import APIView

import logging
import requests # Per fare chiamate HTTP al token endpoint di Cognito
import jwt # Per decodificare il JWT (ID Token)
import boto3
from urllib.parse import quote_plus
import secrets

from django.views.decorators.http import require_POST
from django.core.validators import validate_email
import os

# ---------- CONFIGURAZIONE LOGGING ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log.txt"),
        logging.StreamHandler()
    ]
)


def weatherscanner(request):
    return render(request, 'weatherscanner/home.html')

# Views che permettono la registrazion e il login sul sito
@api_view(['GET', 'POST'])
def register(request):
    if request.method == 'POST':
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        password_confirm = request.data.get('password_confirm')

        if not username or not password or not password_confirm or not email:
            return JsonResponse({'error': 'Username, Email, Password e Conferma password sono necessarie'}, status=400)

        if password != password_confirm:
            return JsonResponse({'error': 'Le password non corrispondono!'}, status=400)
            
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username già esistente'}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Un utente è già registrato con quest\'email.'}, status=400)

        try:
            User.objects.create_user(username, email, password)
            return JsonResponse({'success': 'Registrazione effettuata con successo!', 'redirect': '/login/'})
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return render(request, 'weatherscanner/register.html')


@api_view(['GET', 'POST'])
def login_view(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return JsonResponse({'error': 'Username e Password sono necessari'}, status=400)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': 'Login avvenuto con successo!', 'redirect': '/'})
        else:
            return JsonResponse({'error': 'Credenziali invalide'}, status=400)
    else:
        context = {
            'COGNITO_DOMAIN': settings.COGNITO_DOMAIN,
            'COGNITO_APP_CLIENT_ID': settings.COGNITO_APP_CLIENT_ID,
            'COGNITO_REDIRECT_URI': settings.COGNITO_REDIRECT_URI,
        }
        return render(request, 'weatherscanner/login.html', context)

@api_view(['GET'])
def logout_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Nessun utente connesso'}, status=400)

    # Esegui il logout da Django
    logout(request)
    cognito_logout_url = (
        f"{settings.COGNITO_DOMAIN}/logout?"
        f"client_id={settings.COGNITO_APP_CLIENT_ID}&"
        f"logout_uri={settings.LOGOUT_REDIRECT_URI}"
    )
    
    # Reindirizza l'utente all'endpoint di logout di Cognito
    return JsonResponse({'success': 'Disconnessione avvenuta', 'redirect': cognito_logout_url})

# ------------------------------------------------------

# View che permette di ottenere la lista delle possibili città di cui è possibile visualizzare le condizioni meteo
class SearchAjaxView(APIView):
    def get(self, request, format=None):
        val = request.GET['search']
        # mongodb = Mongodb("mongodb://root:admin@mongo-service.default.svc.cluster.local:27017/")
        mongodb = Mongodb(os.environ.get("MONGO_DB_URI", "mongodb://foo:mustbeeightchars@mydocdb-cluster-instance.cb082oguy914.eu-west-1.docdb.amazonaws.com:27017/?tls=true&tlsCAFile=global-bundle.pem&retryWrites=false"))
        db = mongodb.connect()
        citta = db['cities'].find({"name": {'$regex': '^' + val, '$options': 'i'}}, {'_id': 0})
        return JsonResponse({'citta': list(citta)})


# ------------------------------------------------------


# View che permette di ottenere il meteo attuale della città selezionatata, 
# questa informazione verrà stampata all'interno di una pagina web
class SearchedView(APIView):
    def get(self, request, city, format=None):
        ora = datetime.now().isoformat().split('T')[1].split(':')[0]
        dates = []
        for i in range(0, 6):
            data = date.today() + timedelta(days=i)
            dates.append({'data': data.strftime("%Y-%m-%d"), 'string': data.strftime("%d %b"), 'day': data.strftime("%a") })

        # ---------OGGI -----
        giorno = date.today().isoformat() + "T00:00:00"

        # -----------IERI ---------------
        # giorno = (datetime.now() - timedelta(1)).isoformat() + "T00:00:00"
        
        # mongodb = Mongodb("mongodb://root:admin@mongo-service.default.svc.cluster.local:27017/")
        mongodb = Mongodb(os.environ.get("MONGO_DB_URI", "mongodb://foo:mustbeeightchars@mydocdb-cluster-instance.cb082oguy914.eu-west-1.docdb.amazonaws.com:27017/?tls=true&tlsCAFile=global-bundle.pem&retryWrites=false"))
        db = mongodb.connect()

        # nella query vengono selezionati solamente i dati meteo correnti, 
        # relativi alla città indicata, nel giorno e ora correnti. 
        # orari.$ è necessario per filtrare solamente il documento relativo all'ora richiesta, 
        # e non tutti i documenti presenti dentro l'array (cioè tutti gli orari).
        
        info = list(db['centralina'].find({"localita": translateItEn(city, 'en'),
                                    "data": giorno, 
                                    "orari": {"$elemMatch": {"ora": {'$regex': '^' + ora}} }}, {"orari.$": 1 , "_id":0}))
        if(len(info)==0):
            info = {'notfound': 'Informazioni non disponibili.'}
            return render(request, 'weatherscanner/searched.html', {'citta': city.title(), 'info': info, 'prev_dates': dates})
        # info = [{'orari': [{'ora': '18:01', 'meteo': 'Partly cloudy', 'temp': 27.0, 'precip': '0.0mm', 'vento': 11.2, 'umidita': '45%'}]}]
        print(info)
        info = info[0]['orari'][0]
        info['meteo'] = standardizedNames(info['meteo'])
        info['icon'] = namesInIcons(info['meteo'], info['ora'])
        return render(request, 'weatherscanner/searched.html', {'citta': city.title(), 'info': info, 'prev_dates': dates})


# ------------------------------------------------------


# View che permette di ottenere le previsioni di un servizio meteo per una città in base al giorno selezionato
class ForecastView(APIView):
    def get(self, request, city, service, format=None):
        # mongodb = Mongodb("mongodb://root:admin@mongo-service.default.svc.cluster.local:27017/")
        mongodb = Mongodb(os.environ.get("MONGO_DB_URI", "mongodb://foo:mustbeeightchars@mydocdb-cluster-instance.cb082oguy914.eu-west-1.docdb.amazonaws.com:27017/?tls=true&tlsCAFile=global-bundle.pem&retryWrites=false"))
        db = mongodb.connect()
        meteo = list(db[service].aggregate([{'$match': {"localita": city, "giorno": request.GET['data']}},
                                            {'$project': {'_id':0}},
                                            {'$sort': {'timestamp': -1}},
                                            {'$limit': 1}
                                        ]))[0]

        meteo['servizio'] = service
        for prev in meteo['previsioni']:
            prev['meteo'] = standardizedNames(prev['meteo'])
            prev['icon'] = namesInIcons(prev['meteo'], prev['ora'])

        return JsonResponse({'meteo': meteo})


# ------------------------------------------------------


# view che permette di ottenere le informazioni riguardo l'affidabilità dei servizi

class AccuracyView(APIView):
    def get(self, request, format=None):
        # mongodb = Mongodb("mongodb://root:admin@mongo-service.default.svc.cluster.local:27017/")
        mongodb = Mongodb(os.environ.get("MONGO_DB_URI", "mongodb://foo:mustbeeightchars@mydocdb-cluster-instance.cb082oguy914.eu-west-1.docdb.amazonaws.com:27017/?tls=true&tlsCAFile=global-bundle.pem&retryWrites=false"))
        db = mongodb.connect()
        formula = request.GET['formula']
        b3meteo = db['accuracy'].find_one({"formula": formula, "servizio": "3bmeteo"}, {"_id":0})
        meteoit = db['accuracy'].find_one({"formula": formula, "servizio": "meteoit"}, {"_id":0})
        wbias_b3meteo = db['accuracy'].find_one({"formula": "wbias", "servizio": "3bmeteo"}, {"_id":0, "wbias":1})
        wbias_meteoit = db['accuracy'].find_one({"formula": "wbias", "servizio": "meteoit"}, {"_id":0, "wbias":1})

        return JsonResponse({'3bmeteo': b3meteo, 'meteoit': meteoit, "wbias_3bmeteo": wbias_b3meteo['wbias'], "wbias_meteoit": wbias_meteoit['wbias']})


# ------------------------------------------------------

# Permette di stampare la pagina con all'interno le info sui calcoli utilizzati per ottenere l'affidabilità di un servizio e il bias
def accuracyInfo(request):
    return render(request, 'weatherscanner/accuracy_info.html')

# ------------------------------------------------------

def cognito_google_callback(request):
    """
    Gestisce il callback da AWS Cognito dopo l'autenticazione con Google.
    Scambia il codice di autorizzazione con i token di sessione.
    Crea o autentica l'utente in Django.
    """
    code = request.GET.get('code')
    if not code:
        # Errore, il codice di autorizzazione non è stato ricevuto
        return JsonResponse({'error': 'Il codice di autorizzazione non è stato ricevuto!', 'redirect': '/login/'})
        # Reindirizza alla pagina di login con un messaggio di errore

    try:
        # 1. Scambia il codice di autorizzazione di Cognito con i token
        token_endpoint = settings.COGNITO_TOKEN_URL
        client_id = settings.COGNITO_APP_CLIENT_ID
        redirect_uri = settings.COGNITO_REDIRECT_URI

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'code': code,
            'redirect_uri': redirect_uri
        }

        response = requests.post(token_endpoint, headers=headers, data=data)
        response.raise_for_status() # Solleva un'eccezione per errori HTTP (4xx o 5xx)
        tokens = response.json()

        id_token = tokens.get('id_token')
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')

        if not id_token:
            logging.error("Errore: ID Token non ricevuto da Cognito.")
            return redirect('/login/')

        # 2. Decodifica e verifica l'ID Token (contiene le info utente)
        # Per una verifica robusta, dovresti scaricare le chiavi JWKS di Cognito
        decoded_id_token = jwt.decode(id_token, options={"verify_signature": False})

        email = decoded_id_token.get('email')
        cognito_username = decoded_id_token.get('cognito:username') # O 'sub' o 'username' a seconda del mapping

        if not email:
            logging.error("Email non trovata nell'ID Token.")
            return redirect('/login/')

        # 3. Trova o crea l'utente in Django e loggalo
        User = get_user_model()
        user, created = User.objects.get_or_create(email=email)
        
        # Se l'utente è stato appena creato, imposta uno username e una password (non usata per login Cognito)
        if created:
            user.username = cognito_username or email # Usa lo username di Cognito
            user.set_unusable_password() # Non usiamo una password per gli utenti Cognito
            user.save()
            logging.info(f"Utente Django creato per {email}")
        else:
            logging.info(f"Utente Django esistente per {email}")

        # Logga l'utente in Django
        login(request, user)

        # Reindirizza l'utente alla tua homepage o dashboard
        return redirect('/') # O qualsiasi URL di destinazione post-login

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error durante lo scambio di token: {e.response.text}")
        return redirect('/login/') # Errore HTTP da Cognito
    except Exception as e:
        print(f"Errore inaspettato durante l'autenticazione Cognito: {e}")
        return redirect('/login/') # Gestisci altri errori


# ------------------------------------------------------

# Logica di iscrizione al topic SNS
@require_POST
@api_view(['POST'])
def subscribe_to_weather_notifications(request):
    """
    Gestisce la richiesta di iscrizione di un utente al topic SNS.
    Accetta solo richieste POST.
    """
    email = request.data.get('email')

    try:
        validate_email(email) # Questa linea controlla il formato
    except ValidationError:
        # messages.error(request, "Inserire un indirizzo email valido.")
        return JsonResponse({'error': 'Inserire un indirizzo email valido.'}, status=400)

    try:
        sns_client = boto3.client(
            'sns',
            region_name=settings.AWS_REGION,
            # Boto3 gestirà automaticamente le credenziali
        )

        response = sns_client.subscribe(
            TopicArn=settings.SNS_TOPIC_ARN,
            Protocol='email',
            Endpoint=email
        )

        # Restituisci una risposta JSON di successo
        return JsonResponse({'success': "Grazie! Ti abbiamo inviato un'email di conferma. Clicca sul link nell'email per completare l'iscrizione.", 'redirect': '/'})

    except Exception as e:
        return JsonResponse({'error': f"Si è verificato un errore durante l'iscrizione: {e}"}, status=500)

    
