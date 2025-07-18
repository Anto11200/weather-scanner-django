document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById('logout-button').addEventListener('click', function(event) {
        event.preventDefault();

        const csrftoken = getCookie('csrftoken');

        $.ajax({
            url: '/logout/',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            success: function(data) {
                Swal.fire({
                    title: data.success,
                    icon: "success",
                    confirmButtonText: "OK",
                    timer: 3000,
                    showConfirmButtom: false,
                }).then((result) => {
                    if (result.isConfirmed || (result.dismiss === Swal.DismissReason.timer)) {
                        window.location.href = data.redirect;
                    }
                });
            },
            error: function(jqXHR) {
                var errorData = jqXHR.responseJSON;
                if (errorData.error) {
                    Swal.fire({
                        title: errorData.error,
                        icon: "error"
                    })
                }
            }
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
