/*DOM ready*/
$(document).ready(function(){

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


/* Like */
$('.article-like-form .btn-like-unlike').on('click',function(e){

	e.preventDefault();

	// Text
	const Like = "Like"
	const Liked = "Liked"

	const form = $('.article-like-form');
	const url = form.attr('action');
	var id = form.find('input[name=article_id]').val();

	let payload = {
		"id":id,
		"csrf_token":csrftoken
	}

	$.ajax({
			url : url,
			data: payload,
			type: 'POST',
			cache:false,
			success:function(response){
				if(response["is_liked"] == true){
					$('.btn-like-unlike')[0].innerText = Liked
					$('.btn-like-unlike').addClass('liked-css');
				}
				else{
					if($('.btn-like-unlike').hasClass('liked-css')){
						$('.btn-like-unlike').removeClass('liked-css');
					}
					
					$('.btn-like-unlike')[0].innerText = Like
				}
			},
			error:function(response){
				console.log(response.responseText);
			}
		});
		return false;


  });


}); /* DOM End*/
