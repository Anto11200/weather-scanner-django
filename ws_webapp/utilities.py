# funzione per effettuare la traduzione dei nomi delle città, in quanto l'api per il meteo attuale utilizza i nomi in inglese,
# mentre i crawler quelli in italino. 
# come parametri accetta il nome da tradurre e 'language', cioè la lingua di destinazione, 'it' o 'en'

def translateItEn(name, language):
    dizionario = {
        'messina': "messina",
        'palermo': "palermo",
        'roma': 'rome',
        'milano': 'milan',
        'torino': 'turin'
    }
    if(language == 'en'):
        return dizionario.get(name)
    elif(language == 'it'):
        return list(dizionario.keys())[list(dizionario.values()).index(name)]

# funzione necessaria per rendere standard le diciture meteo dei servizi scelti.
# controlla all'interno dei valori del dizionario se è presente il nome passato come parametro; 
# se presente, viene restituita la chiave associata.

def standardizedNames(name):
    dizionario = {"sereno":["sereno", "sereno con lievi velature", "sereno o poco nuvoloso", "sereno con foschia",  "prevalentemente soleggiato", "soleggiato", "sereno notte", "Sunny", "Clear"],
                  "velature": ["velature estese", "velature sparse", "velature lievi",],
                  "nubi sparse": ["nubi sparse", "nubi sparse con ampie schiarite", "nubi basse", "nubi basse e schiarite" ], 
                  "parzialmente nuvoloso":["poco o parzialmente nuvoloso per velature sparse", "poco nuvoloso", "Partly cloudy", "parz nuvoloso"],
                  "nuvoloso": ["nuvoloso con locali aperture", "nuvoloso per velature estese", "cielo in gran parte nuvoloso", "Cloudy", "molto nuvoloso", "nuvoloso"],
                  "coperto": ["Mist", "coperto", "molto nuvoloso o coperto per nubi alte", "nuvoloso o molto nuvoloso", "molto nuvoloso o coperto", "cielo grigio per nubi basse", "cielo coperto", "Overcast", "coperto per nubi alte"],
                  "pioggia debole": ["nubi sparse con pioggia debole", "coperto con pioviggini", "coperto con pioggia debole", "nubi sparse con possibili piogge", "coperto con possibili piogge", "coperto con possibili piogge e nebbia", "nubi sparse con pioviggine", "pioggia debole", "nuvoloso con pioggia leggera", "Patchy rain possible", "Light rain", "Patchy light rain", "Light freezing rain", "Light rain shower", "Patchy light drizzle", "Light drizzle", "Freezing drizzle", "Heavy freezing drizzle", "pioggia debole e schiarite", "pioviggine", "pioviggine e schiarite", "possibili piogge"],
                  "pioggia": ["nuvoloso con pioggia media", "coperto con pioggia", "coperto con pioggia e nebbia", "coperto con rovesci di pioggia e nebbia", "pioggia moderata", "Moderate rain at times", "Moderate rain", "Moderate or heavy freezing rain", "Moderate or heavy rain shower", "nubi sparse e rovesci", "pioggia", "pioggia e schiarite", "rovesci di pioggia"],
                  "pioggia forte": ["pioggia forte e schiarite", "coperto con rovesci di pioggia", "piogge di forte intensità", "piogge molto forti, localmente alluvionali", "nubi irregolari con pioggia forte", "nubi irregolari con pioggia molto forte", "pioggia forte", "nuvoloso con pioggia forte", "Heavy rain at times", "Heavy rain", "Torrential rain shower"],
                  "temporale": ["temporale forte e schiarite", "possibili temporali", "temporali forti con grandine", "temporali di forte intensità", "molto nuvoloso con piogge e temporali", "temporali di forte intensità e nebbia", "nubi irregolari con temporali", "molto nuvoloso con piogge e temporali e nebbia", "nubi irregolari con possibile temporale", "nubi irregolari con possibili temporali e nebbia", "nubi irregolari con temporale forte", "temporale", "nuvoloso con temporale", "Patchy light rain with thunder", "Moderate or heavy rain with thunder", "Thundery outbreaks possible", "nubi sparse e temporali"],
                  "nebbia": ["nebbia", "nebbia a banchi"]}
    trovato = ""
    #c = chiave, v = valore
    for c, v in dizionario.items():
        if(name in v):
            trovato = c
            
    if(trovato == ""):
        trovato = name
    
    return trovato

# associa ad ogni nome standardizzato l'icon associata per mostrarla nel front-end.
# vi sono due dizionari differenti in quanto alcune icon cambiano a seconda di giorno/sera, dunque è presente un controllo sull'orario.

def namesInIcons(name, time):
    if int(time[0:2]) > 17 or int(time[0:2]) < 5:
        dizionario = {"sereno": "<i class='fa-solid fa-moon'></i>",
                      "velature": "<i class='fa-solid fa-moon'></i>",
                      "nubi sparse": "<i class='fa-solid fa-cloud-moon'></i>",
                      "parzialmente nuvoloso": "<i class='fa-solid fa-cloud-moon'></i>",
                      "nuvoloso":"<i class='fa-solid fa-cloud'></i>",
                      "coperto": "<i class='fa-solid fa-cloud'></i>",
                      "pioggia debole": "<i class='fa-solid fa-droplet'></i>",
                      "pioggia": "<i class='fa-solid fa-cloud-rain'></i>",
                      "pioggia forte": "<i class='fa-solid fa-cloud-showers-heavy'></i>",
                      "temporale": "<i class='fa-solid fa-bolt'></i>"
                      }
    else:
        dizionario = {"sereno": "<i class='fa-solid fa-sun'></i>",
                      "velature": "<i class='fa-solid fa-sun'></i>",
                      "nubi sparse": "<i class='fa-solid fa-cloud-sun'></i>",
                      "parzialmente nuvoloso": "<i class='fa-solid fa-cloud-sun'></i>",
                      "nuvoloso":"<i class='fa-solid fa-cloud'></i>",
                      "coperto": "<i class='fa-solid fa-cloud'></i>",
                      "pioggia debole": "<i class='fa-solid fa-droplet'></i>",
                      "pioggia": "<i class='fa-solid fa-cloud-rain'></i>",
                      "pioggia forte": "<i class='fa-solid fa-cloud-showers-heavy'></i>",
                      "temporale": "<i class='fa-solid fa-bolt'></i>"
                      }
    
    return dizionario[name]

# funzione che associa ad ogni nome standardizzato un valore numerico.
# tali valori sono necessari al calcolo dell'accuratezza.

def namesInValue(name):
    dizionario = {  "sereno": 1,
                    "velature": 2,
                    "nubi sparse": 3,
                    "parzialmente nuvoloso": 4,
                    "nuvoloso": 5,
                    "coperto": 6,
                    "pioggia debole": 7,
                    "pioggia": 8,
                    "pioggia forte": 9,
                    "temporale": 10
                    }
    
    return dizionario[name]