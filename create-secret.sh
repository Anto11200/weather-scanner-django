# Si specifica una variabile d'input per non salvare sulla repo una variabile in chiaro
kubectl create secret generic db-secret --from-literal=password=$1