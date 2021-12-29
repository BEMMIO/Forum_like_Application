/*DOM ready*/
$(document).ready(function(){

$("#div_id_invite_to_user_email").append("<i class='la la-paper-plane'></i>");


let email_data = $.trim($("#id_invite_to_user_email").val());

var bool = email_data.length == 0 ? true : false;

if(bool == true){
    $(".hide-toggle").hide();
    $(".auto-text-update").html("")
}
else{
    $(".auto-text-update").html(email_data);
    $(".hide-toggle").show();
}



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

// Scripts here


    $(".js-invite-btn").click(function(e){
        $(this).parents(".invite-row").find("form").submit();
    });


    $("#id_invite_to_user_email").keyup(function(){
        let val_ = $(this).val();

        if(val_.length == 0){
            $(".hide-toggle").hide();
            $(".auto-text-update").html("")
        }else{
            $(".hide-toggle").show();
            $(".auto-text-update").html(val_)

        }


    });


}); /* DOM End*/
