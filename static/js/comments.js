/*DOM ready*/
$(document).ready(function(){

// Change placeholder of comment-reply form
$('body').find(".reply-to-comment-form-cls #id_content").attr('placeholder','Reply...')

// Disable Btn - avoid multiple database submissions.
    
$('#comment-delete-fm').submit(function(){
    $(this).find('.comment-delete-btn').attr('disabled',true);

});


$('#comment-edit-form').submit(function(){
    $(this).find('.edit-btn').attr('disabled',true);

});
   

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


    $('body').on('click', '.reply-btn',function(){
        $(this).parent().find(".reply-list-form-wrp").fadeToggle();
    });

    $('.comment-form-cls .textarea').on('focus',function(){
        $(this).attr("rows",6);
    });


    // Ajax-Comment-form
    $('body').on('submit','.article-comment',function(e){
        e.preventDefault();

        // Disable button for prevent multiple submitting. 
        $(this).find('input[name=submit-comment]').attr('disabled',true);

        let content = $(this).find('#id_content');

        let self = $(this);

        if($.trim(content.val()).length == 0){
            // prevent user sending empty content.
            self.find('input[name=submit-comment]').attr('disabled',false);
            return false;
        }else{
            // content isn't empty - call ajax to send serialized data to server-side
            $.ajax({
                url : self.attr('action'),
                data: self.serialize(),
                dataType: 'json',
                type: 'POST',
                cache:false,
                beforeSend: function(){
                    self.find('#id_content').attr("disabled",true);
                },
                success:function(response){
                    // console.log(response);

                    content.val('');

                    if(response["is_a_reply"] == false){

                        console.log(response);

                        $(".column-wrap-comments").prepend(response["html_template"]);
                        $('.comments-count').html(parseInt(response["count"]))

                        // Enable button after response is successful.
                        self.find('input[name=submit-comment]').attr('disabled',false);
                        self.find('#id_content').attr("disabled",false);
                    }
                    else if(response["is_a_reply"] == true)
                    {

                        console.log(response);
                        
                        self.find('input[name=submit-comment]').attr('disabled',false);
                        self.parent('.reply-list-form-wrp').find(".empty-reply").hide();

                        // Increment parent comments count
                        self.parent('.reply-list-form-wrp').prepend(response["html_template"]);
                        $('.comments-count').html(parseInt(response["count"]))
                        self.find('#id_content').attr("disabled",false);
                        // Increment reply count

                    }
                },
                error:function(response){
                    console.log(response.responseText);
                }
            });
            return false;

        }


    });

    // Like

    $('.comment-like-fm-cls .comment-like-btn').on('click',function(e){

    e.preventDefault();

    const form = $('.comment-like-fm-cls');
    const url = form.attr('action');
    let id = $(this).parent("form").find("input[name=comment-id]").val();

    let payload = {
        "id":id,
        "csrf_token":csrftoken
    }

    console.log(payload);

        fetch(url, {

                method : 'POST',
                headers:{
                      'Accept': 'application/json',
                      'X-Requested-With': 'XMLHttpRequest',
                      'X-CSRFToken': csrftoken,
                },

                    // POST data
                    body: JSON.stringify(payload),

                })
                  .then(response => {
                      return response.json() //Convert response to JSON
                })
                  .then(data => {
                      //Perform actions with the response data from the view
                        console.log(data);
                })
                  .catch(function(){
                        console.log("Error : search failed.")
                });


  });



}); /* DOM End*/
