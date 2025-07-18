$(document).ready(function () {
    let i = 0;
    let search = $("#search")

    // metodo per far in modo che venga inviata un'ajax per ottenere dinamicamente i suggerimenti delle città 
    // da ricercare a seconda del testo inserito;
    // se la barra è vuota, il div con i suggerimenti viene nascosto e vengono reimpostati i border radius della barra

    search.keyup(function selectMenu(e){
        val = search.val()
        if(e.key == "Backspace") {
            if(!val) {
                $('.select').removeClass('visible');
                $('.select').addClass('hidden');
                $('.search-bar').removeClass('radius-top');
                $('.search-bar').addClass('radius');
            }
            else{
                searchCities(val);
            }
        } else{
            searchCities(val);
        }
    });

    // metodo relativo all'evento del click sulla lente di ricerca della barra, per inviare un'ajax ed ottenere la città cercata;
    // se presente, si viene reindirizzati alla pagina relativa alla città, se non è presente nel db viene mostrato un alert di errore 

    $("#lens").click(function (e) { 
        e.preventDefault();
        citta = search.val().toLowerCase();
        $.ajax({
            type: "GET",
            url: "/weatherscanner/search/",
            data: {'search': val},
            success: function (response) {
                if(response['citta'].length == 0){
                    Swal.fire({
                        icon: 'error',
                        text: 'Nessuna città corrispondente alla ricerca.',
                        position: 'top',
                        showConfirmButton: false,
                        timer: 3000,
                        timerProgressBar: true,
                        didOpen: (toast) => {
                        toast.addEventListener('mouseenter', Swal.stopTimer)
                        toast.addEventListener('mouseleave', Swal.resumeTimer)
                        }
                    })
                }else {
                    window.location.href = "/weatherscanner/searched/" + citta;
                }
            }
        });
        
    });

    // funzione legata all'evento di mouseup: se viene effettuato un click al di fuori del div relativo alla 
    // barra di ricerca e i suggerimenti,
    // il div dei suggerimenti viene svuotato e nascosto chiudendo la tendina
    
    $(document).mouseup(function(e){
        var search = $(".search-container");
        var select = $(".search-container .select");
     
        // If the target of the click isn't the container
        if(!search.is(e.target) && search.has(e.target).length === 0){
            select.removeClass('visible');
            select.addClass('hidden');
            select.empty();
            $('.search-bar').removeClass('radius-top');
            $('.search-bar').addClass('radius');
        }
    });
});

// funzione che invia l'ajax per effettuare la ricerca delle città da mostrare come suggerimenti,
// impostando le classi per modificare l'aspetto della barra di ricerca e del div suggerimenti

function searchCities(val){
    $.ajax({
        type: "GET",
        url: "/weatherscanner/search/",
        data: {'search': val},
        success: function (response) {
            console.log(response['citta'])
            if(response['citta'].length){
                $('.select').removeClass('hidden');
                $('.select').addClass('visible');
                $('.search-bar').removeClass('radius');
                $('.search-bar').addClass('radius-top');
                selectHints(response)
            }
        }
    });
}

//  funzione che modifica l'html relativo al div dei suggerimenti, 
// aggiungendo un hint contenente il tag a per reindirizzare alla città desiderata

function selectHints(response){
    let hints = ''
    citta = response['citta']
    for(c in citta){
        hints += `<div class="hint">
                    <a href='/weatherscanner/searched/` + citta[c]['name'] +`'>` + capitalizeFirstLetters(citta[c]['name']) + `</a>
                </div>`
    }
    $('.select').html(hints);
}