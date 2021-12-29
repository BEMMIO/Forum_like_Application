/*DOM ready*/
$(document).ready(function(){

// reset browser url on page refresh
window.history.replaceState("",""," ")


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



    //  Search Article & User

    $(".search-form").submit(function(e){
        e.preventDefault();
    });

    $(".search-form .search-input").keyup(function(e){

        query = $(this).val().trim();
        var url = $(".search-form").attr("method");

        if(!(query.length > 1)){
            return false;
        }

        let payload = {
        "q":query,
        "csrf_token":csrftoken
    }

    $.ajax({
            url : url,

            data: payload,

            type: 'GET',

            cache:false,

            success:function(response){
              // console.log(response["html_template"]);
              $(".search-results").html(response["html_template"])
            },
            error:function(response){
                console.log(response.responseText);
            }
        });
        return false;


    });




    // Board Search Form

    $(".board-search-fm-cls").submit(function(e){
        // prevent any form submission actions.
        e.preventDefault();
    });

    $(".board-search-fm-cls .search-input").keyup(function(e){
        e.preventDefault();

        const url = $(".board-search-fm-cls").attr("action"); 
        var data = $.trim($(this).val());

        if (!(data.length > 0)){
            // set to default url : `http://127.0.0.1:8000/blog/boards/`
            window.history.replaceState("",""," ")
        }else{  

            // update url : `http://127.0.0.1:8000/blog/boards/#search?q=text-from-user`
            window.history.replaceState("","", "#search?q="+data);

            // call ajax GET to fetch data to update template.

            var payload = {
                "q":data,
            }

            // fetch(url, {
            //       headers:{
            //           'Accept': 'application/json',
            //           'X-Requested-With': 'XMLHttpRequest', //Necessary to work with request.is_ajax()
            //           'X-CSRFToken': csrftoken,
            //     },

            //   })
            //   .then(response => {
            //       return response.json() //Convert response to JSON
            //   })
            //   .then(data => {
            //       //Perform actions with the response data from the view
            //         console.log(data);
            //   })
            //   .catch(function(){
            //         console.log("Error : search failed.")
            //   });

            $.ajax({
                url : url,

                data: payload,

                type: 'GET',

                cache:false,

                success:function(response){
                  // console.log(response["html_template"]);
                  console.log(response);
                },
                error:function(response){
                    console.log(response);
                }
        });
        return false;

        }/* end if-else */



    });

}); /* DOM End*/
