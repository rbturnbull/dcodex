
function setup_left_sidebar_toggle() {
    $( '#toggle_left_sidebar' ).click(function(e) {
        var middle = $( "#middle" );
        var left = middle.offset().left;
        if ( left > 0 ) {
            middle.animate({ left: '0px' }, function(response) {
                middle.trigger( "middle:resize" );
            });
        }
        else {
            middle.animate({ left: $('#left_sidebar').width() + 'px' }, function(response) {
                middle.trigger( "middle:resize" );
            });
        }
    });
}
function setup_right_sidebar_toggle() {
	$( '#toggle_right_sidebar' ).click(function(e) {
		var middle = $( "#middle" );
		var right = $(window).width() - (middle.offset().left + middle.outerWidth());
		if ( right > 0 ) {
			middle.animate({ right: '0px' }, function(response) {
                middle.trigger( "middle:resize" );
			});
		}
		else {
		    comparison = $('#right_sidebar')
		    width = comparison.outerWidth();
			middle.animate({ right: width + 'px' }, function(response) {
                middle.trigger( "middle:resize" );
			});
		}
	});
}

$( document ).ready(function() {
    console.log( "Loading from sidebars.js" );    
    setup_right_sidebar_toggle();
    setup_left_sidebar_toggle();
});
