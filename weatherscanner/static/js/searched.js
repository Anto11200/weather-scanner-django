$(document).ready(function () {

    // ottengo il nome della città dall'url e la data; 
    // al caricamento della pagina, il primo tra i giorni delle 
    // previsioni deve essere selezionato e mostrato

    citta = $(location).attr('href').split('/')[5];
    oggi = new Date().toISOString().split('T')[0]
    $('.day:first-child').addClass('selected');

    // ajax da effettuare al caricamento della pagina, per ottenere le previsioni
    // relative alla data odierna sia per 3bmeteo che meteoit

    $.ajax({
        type: "GET",
        url: "/weatherscanner/searched/" + citta + "/forecast/3bmeteo",
        data: {'data': oggi},
        success: function (response) {
            console.log(response)
            fillTable(response, oggi)
        }
    });

    $.ajax({
        type: "GET",
        url: "/weatherscanner/searched/" + citta + "/forecast/meteoit",
        data: {'data': oggi},
        success: function (response) {
            fillTable(response, oggi)
        }
    });

    // ajax per ottenere l'accuratezza di entrambi i servizi

    $.ajax({
        type: "GET",
        url: "/weatherscanner/searched/forecast/accuracy",
        data: {'formula': 'mape'},
        success: function (response) {
            showAccuracy(response)
        }
    });

    // funzione legata al click sui div relativi ai giorni di cui si vogliono 
    // visualizzare le previsioni dettagliate;
    // si deseleziona il div attualmente selezionato e si seleziona quello 
    // desiderato (rimuovendo e aggiungendo la classe selected);
    // si inviano le ajax relative a quel giorno e al servizio considerato 
    // per ottenere le previsioni dettagliate

    $('.day').click(function (e) { 
        e.preventDefault();
        id_elem = this.id.split('_');
        giorno = id_elem[0];
        servizio = id_elem[1];
        $('.day.' + servizio).removeClass('selected');
        $('.day.' + servizio + ' .minmax').empty();
        $(this).addClass('selected');
        if(servizio == '3bmeteo'){
            $.ajax({
                type: "GET",
                url: "/weatherscanner/searched/" + citta + "/forecast/3bmeteo",
                data: {'data': giorno},
                success: function (response) {
                    fillTable(response, oggi)  
                }
            });
        }else if(servizio == 'meteoit'){
            $.ajax({
                type: "GET",
                url: "/weatherscanner/searched/" + citta + "/forecast/meteoit",
                data: {'data': giorno},
                success: function (response) {
                    fillTable(response, oggi)
                }
            });
        }
    });

    // funzione legata alla select della formula da utilizzare per il calcolo 
    //dell'accuratezza; al cambiamento dell'option selezionata, viene inviata 
    //un ajax per ottenere i dati corretti

    $('#formula').on('change', function(){
        formula = $(this).val()
        $.ajax({
            type: "GET",
            url: "/weatherscanner/searched/forecast/accuracy",
            data: {'formula': formula},
            success: function (response) {
                showAccuracy(response)
            }
        });
    })
});

// funzione per riempire la tabella html contenente le previsioni del giorno selezionato

function fillTable(response, oggi){
    let servizio = response['meteo']['servizio'];
    $('#' + response['meteo']['giorno'] + '_' + servizio + '.selected .minmax').text(response['meteo']['min'] + '/' + response['meteo']['max']);
    if(response.length == 0){
        $("#"+servizio).append("Previsioni non disponibili.");
    }else{
        let prev = response['meteo']['previsioni'];
        let rows = "";
        let i=0;
        if(response['meteo']['giorno'] == oggi){
            i = new Date().getHours();     
        }
        for(p = i; p < 24; p++){
            rows = rows + `<tr class="prev-row">
                            <td>` + prev[p]['ora'] + `</td>
                            <td class="icon">` + prev[p]['icon'] + `</td>
                            <td>` + prev[p]['meteo'] + `</td>
                            <td>`+ prev[p]['temp'] + `</td>
                            <td>` + prev[p]['precip'] + `</td>
                            <td>` + prev[p]['vento'] + `km/h</td>
                            <td>` + prev[p]['umidita'] + `</td>
                        </tr>`;
        }
        $("#"+servizio).empty(); 
        $("#"+servizio).append(rows); 
    } 
}

// funzione per mostrare i dati relativi all'accuratezza desiderata, per entrambi i servizi

function showAccuracy(response){
    b3meteo = response['3bmeteo']
    meteoit = response['meteoit']
    wbias_3b = response['wbias_3bmeteo']
    wbias_it = response['wbias_meteoit']

    if(b3meteo['formula'] == 'mape'){
        acc_3bmeteo = (100 - b3meteo['mape']).toString() + "%"
    }
    else if(b3meteo['formula'] == 'rmse'){
        acc_3bmeteo = b3meteo['rmse']
    }

    if(meteoit['formula'] == 'mape'){
        acc_meteoit = (100 - meteoit['mape']).toString() + "%"
    }
    else if(meteoit['formula'] == 'rmse'){
        acc_meteoit = meteoit['rmse']
    }

    wbias_3b_string = biasRange(wbias_3b)
    wbias_it_string = biasRange(wbias_it)

    $('.accuracy.3bmeteo').text("(Affidabilità: " + acc_3bmeteo + ", risulta " + wbias_3b_string + ")")
    $('.accuracy.meteoit').text("(Affidabilità: " + acc_meteoit + ", risulta " + wbias_it_string + ")")
}

// funzione che associa al valore ottenuto per il bias, una stringa da mostrare

function biasRange(wbias){
    if(wbias < 0.0 ){
        string = "pessimista"
    }else if(wbias > 0.0) {
        string = "ottimista"
    }else{
        string = "realista"
    }
    return string
}