# Stage finale (runtime)
FROM python:3.12-alpine AS final

# Crea un utente non root per motivi di sicurezza
RUN addgroup -S django && adduser -S -G django django
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Installa le dipendenze di build necessarie per i pacchetti Python con estensioni C
# build-base: include gcc, make, etc. per compilare pacchetti Python
# mariadb-dev: include header e librerie di sviluppo per la connessione al database
RUN apk add --no-cache build-base mariadb-dev

# Imposta la directory di lavoro
WORKDIR /app

# Copia il file requirements.txt e installa le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installa solo le librerie client di MariaDB, necessarie a runtime
# Non servono più i pacchetti di build, rendendo l'immagine più piccola
# Sostituito libmariadb3 con mariadb-connector-c
# Se mariadb-connector-c non funziona, prova con mariadb-client
RUN apk add --no-cache mariadb-connector-c

# Imposta le variabili d'ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Imposta la directory di lavoro e il proprietario
WORKDIR /app

# Cambia il proprietario dei file per il nuovo utente
RUN chown -R django:django /app

# Espone la porta su cui l'applicazione sarà in ascolto
EXPOSE 8000

# Passa all'utente django
USER django

COPY . .

# Comando per avviare l'applicazione Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]