document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById('login-form').addEventListener('submit', function(event) {
        event.preventDefault();

        var username = document.getElementById('id_username').value;
        var password = document.getElementById('id_password').value;

        const csrftoken = getCookie('csrftoken'); 

        $.ajax({
            url: '/login/',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            data: JSON.stringify({
                username: username,
                password: password,
            }),
            success: function(data) {
                Swal.fire({
                    title: data.success,
                    icon: "success",
                    confirmButtonText: "OK",
                }).then((result) => {
                    if (result.isConfirmed) {
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

document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById('subscribe-form').addEventListener('submit', function(event) {
        event.preventDefault();

        var email = document.getElementById('id_email_subscribe').value;

        const csrftoken = getCookie('csrftoken'); 

        $.ajax({
            url: this.action,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            data: JSON.stringify({
                email: email,
            }),
            success: function(data) {
                Swal.fire({
                    title: data.success,
                    icon: "success",
                    confirmButtonText: "OK",
                }).then((result) => {
                    if (result.isConfirmed) {
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