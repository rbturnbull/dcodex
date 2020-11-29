// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
function load_comparison(verse_id, manuscript_id, div_name) {
    $( div_name ).load( "/dcodex/ajax/comparison/", { manuscript_id:manuscript_id, verse_id:verse_id }, function() {
        $(".mshover").hover(function(){
            $('#msHover').load("/dcodex/ajax/transcription-mini/", { manuscript_id:$(this).data('manuscriptid'), verse_id:$(this).data('verseid') } );
            $('#msHover').show();
        }, function() {
            $('#msHover').hide();	  
            $('#msHover').html("");
        });        
    } );
}

$(function () {
    $('[data-toggle="tooltip"]').tooltip()
  })
  