/*DOM ready*/
$(document).ready(function(){

enable_publish_btn_with_conditions()
enable_draft_btn_with_conditions()


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


/* Article */

/*
- disable btns
- toggle with check (text)
- enable all publish btn when all fields are filled
- enable only the draft btn title is filled
- count text of content length

*/

// submit buttons.
publish_btn = $("input[name=publish-article]");
draft_btn = $("input[name=draft-article]");
// Boolean

// Count-Down of article content. 
$(".textarea").keyup(function(){
    var charcount = $(this).val().length;
    $(".counter-val").text(450 - charcount);
});


// Enable Btn's

$(".textarea").keyup(function(){
    var textarea_val = $(this).val().length;
    var title_val = $("#id_title").val().length;

    if((textarea_val > 1) && (title_val > 1)){
        publish_btn.attr("disabled",false);
    }else{
        publish_btn.attr("disabled",true);
    }

    // Crispy forms error .
    if($(this).hasClass('is-invalid')){
        if(textarea_val > 105){
            $(this).removeClass('is-invalid');
        }
        else{
             $(this).addClass('is-invalid');
        }
    }

});


$("#id_title").keyup(function(){
    var title_val = $(this).val().length;
    var textarea_val = $(".textarea").val().length

    if((title_val > 1) && (textarea_val > 1)){
        publish_btn.attr("disabled",false);
    }else{
        publish_btn.attr("disabled",true);
    }

    // toggle drafts buttons state on text input in title.
    var bool_ = title_val > 1 ? false : true;
    draft_btn.attr("disabled",bool_);
});



// Refreshing Page after invalid input : make sure btn's are enabled for filled inputs.
function enable_publish_btn_with_conditions(){
    if($(".textarea").val().length > 1){
        $("input[name=publish-article]").attr("disabled",false);
    }else{
        $("input[name=publish-article]").attr("disabled",true);
    }
}

function enable_draft_btn_with_conditions(){
    if($("#id_title").val().length > 1){
        $("input[name=draft-article]").attr("disabled",false);
    }else{
        $("input[name=draft-article]").attr("disabled",true);
    }
}


// LocalStorage. Article : Title , Content & Tags.



}); /* DOM End*/
