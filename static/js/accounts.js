/*DOM ready*/
$(document).ready(function(){

$(".js-register-user-form input[name=username]").parents("#div_id_username").find("label b").html($(".js-register-user-form input[name=username]").val())

// Required by Ajax to work with Django.

function getCookie(name) {
        // Function to get any cookie available in the session.
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    function csrfSafeMethod(method) {
        // These HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    var csrftoken = getCookie('csrftoken');
    var page_title = $(document).attr("title");
    // This sets up every ajax call with proper headers.
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });



// Simple async func updating content with username for keyup.
$(".js-register-user-form input[name=username]").keyup(function(){

    let val_ = $(this).val();
    $(this).parents("#div_id_username").find("label b").html(val_)

});



// Authenticatio & Validation Form `Toggle-Visibility`

let validation_form = $(".js-auth-validation-form");

let authentication_form = $(".js-auth-login-form");

default_src = '/static/img/158.svg'

$(".js-signup-txt").click(function(e){
    // Display : validation_form
    e.preventDefault()
    $(this).parents("form").hide();
    validation_form.show()
    // change image to key
    $(".img-illustrator").attr("src",'/static/img/268_key.svg');
});

$(".js-login-txt").click(function(e){
    // Display : authentication_form
    e.preventDefault()
    $(this).parents("form").hide();
    authentication_form.show();
    // change image to lady
    $(".img-illustrator").attr("src",default_src)
});


$(".js-auth-validation-form").submit(function(e){
    e.preventDefault();
})




}); /* DOM End*/
