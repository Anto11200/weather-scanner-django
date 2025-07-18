// funzione per rendere maiuscole la prima lettera di ogni parola all'interno di una frase

function capitalizeFirstLetters(string) {
    //divido la stringa ogni volta che si incontra uno spazio, tramite il metodo split
    var stringSplit = string.split(" ");
    for (let i = 0; i < stringSplit.length; i++) {
        //metto la prima lettera in maiuscolo e concateno il resto della stringa, per ogni parola all'interno di stringSplit
        stringSplit[i] = stringSplit[i][0].toUpperCase() + stringSplit[i].substr(1);
    }
    //rimetto assieme le parole che costituivano la stringa iniziale
    var string2 = stringSplit.join(" ");
    return string2;
};
