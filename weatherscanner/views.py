from datetime import datetime, date, timedelta
import locale
from django.shortcuts import render
from django.http import JsonResponse
from mongodb import Mongodb
from ws_webapp.utilities import *

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError
from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.views import APIView





# locale.setlocale(locale.LC_TIME, 'it_IT')

# -----------------------CONNESSIONE AL RASPBERRY----------------------------


def weatherscanner(request):
    return render(request, 'weatherscanner/home.html')


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
        return render(request, 'weatherscanner/login.html')


@api_view(['POST'])
def logout_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Nessun utente connesso'}, status=400)

    logout(request)
    return JsonResponse({'success': 'Disconnessione avvenuta', 'redirect': '/login/'})

# ------------------------------------------------------


# View che permette di ottenere la lista delle possibili città di cui è possibile visualizzare le condizioni meteo
class SearchAjaxView(APIView):
    def get(self, request, format=None):
        val = request.GET['search']
        # mongodb = Mongodb("mongodb://root:admin@localhost:27017/")
        # mongodb = Mongodb("mongodb://root:admin@siakoo.asuscomm.com:27017/?authMechanism=DEFAULT")
        mongodb = Mongodb("mongodb://foo:mustbeeightchars@load-balancer-docdb-0183b5887cd86ae8.elb.eu-west-1.amazonaws.com:27017/?tls=true&tlsAllowInvalidHostnames=true&directConnection=true")
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

        # ---------OGGI ----- CONNESSIONE RASPBERRY
        giorno = date.today().isoformat() + "T00:00:00"

        # -----------IERI ---------------
        # giorno = (datetime.now() - timedelta(1)).isoformat() + "T00:00:00"
        
        mongodb = Mongodb("mongodb://foo:mustbeeightchars@load-balancer-docdb-0183b5887cd86ae8.elb.eu-west-1.amazonaws.com:27017/?tls=true&tlsAllowInvalidHostnames=true&directConnection=true")
        # mongodb = Mongodb("mongodb://root:admin@siakoo.asuscomm.com:27017/?authMechanism=DEFAULT")
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
        mongodb = Mongodb("mongodb://root:admin@mongo-service.default.svc.cluster.local:27017/")
        # mongodb = Mongodb("mongodb://root:admin@siakoo.asuscomm.com:27017/?authMechanism=DEFAULT")
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
        mongodb = Mongodb("mongodb://root:admin@localhost:27017/")
        # mongodb = Mongodb("mongodb://root:admin@siakoo.asuscomm.com:27017/?authMechanism=DEFAULT")
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