var current_manuscript_id;
var current_pdf_filename;
var currentPage;
var current_verse_id;
var pageImageController = null;

function setLoadVerseLink() {
    $( ".loadVerseLink" ).click(function(e) {
        verse_id = $(this).data('verseid');
        load_verse(verse_id, current_manuscript_id);				
        return false;
    });
}

function setCurrentPage( page ) {
    if ( currentPage == page ) 
        return;

    $('.thumbnailContainer').removeClass('thumbnailCurrent');
    var thumbnail = $('#thumbnailContainer'+page);
    thumbnail.addClass('thumbnailCurrent');


    // Check if page is visible
//		alert( "scroll top" + $('#thumbnails').scrollTop() + " thumbnail.offset().top" + thumbnail.offset().top + " $('#thumbnails').height() " + $('#thumbnails').height() );
    if (thumbnail.offset().top + thumbnail.height() < 0 || thumbnail.offset().top > $('#thumbnails').height() ) {
    
        if ( Math.abs( currentPage - page ) < 4 ) {
            $('#thumbnails').scrollTo(thumbnail, 300);							
        }
        else {
            $('#thumbnails').scrollTo(thumbnail);				
        }
    }
        
    currentPage = page;
}

function loadVerseMarker(dict) {
    var page = dict['page'];
    var x0 = dict['x'];
    var y0 = dict['y'];
    var ref = dict['ref'];
    var tooltip = dict['tooltip'];
    var verseID = dict['verse_id'];		
    
    var pageDiv = $('#page'+page);
    var pageHeight = pageDiv.height();
    var pageWidth = pageDiv.width();		      	
//		      	alert(pageHeight);
    var top = y0*pageHeight;
    var left = x0*pageWidth;
        

    verseMapX = $('#verseMapX'+verseID);
    if ( verseMapX.length > 0 ) {
        hasVerseMarker = true;
    }
    else {
        hasVerseMarker = false;
    }
    
    if ( hasVerseMarker && verseMapX.data('page') != page ) {
        removeMarkerDisplay( verseID );
        hasVerseMarker = false;
    }

    if ( hasVerseMarker ) {
        verseMap = $('#verseMap'+verseID);				
        verseMap.css( 'top', top+"px" );
        verseMapX.css( 'top', top+"px" );
        verseMapX.css( 'left', left+"px" );
        verseReference = $('#verseReference'+verseID);
        verseReference.css( 'top', top+"px" );
        verseReference.html( ref+tooltip );

        verseMapX.data('x0', x0);			
        verseMapX.data('y0', y0);			
        verseMapX.data('page', page);
    }
    else {		
        pageDiv.append( "<div id=verseMap"+verseID+" class='verseMarker' style='top: "+(top)+"px' ></div>" );		      	
        pageDiv.append( "<div id=verseMapX"+verseID+" class='verseMarkerX' style='top: "+(top)+"px; left:"+(left)+"px' ></div>" );
        pageDiv.append( "<div id=verseReference"+verseID+" class='verseReference' style='top: "+(top)+"px;' data-verse='"+verseID+"'>"+ref+tooltip+"<div id=removeMarker"+verseID+" class=removeMarker data-verse='"+verseID+"'></div></div>" );

        
        verseMap = $('#verseMap'+verseID);			
        verseMapX = $('#verseMapX'+verseID);
        verseMapX.data('x0', x0);			
        verseMapX.data('y0', y0);			
        verseMapX.data('page', page);			
        verseMapX.data('verseid', verseID);			
        verseReference = $('#verseReference'+verseID);			
        removeMarkerDiv = $('#removeMarker'+verseID);
        removeMarkerDiv.click(function(e) {
            var verseID = $(this).data('verse');
            deleteMarker(verseID);
            return false;
        });
        

        verseReference.click(function(e) {
            var verse = $(this).data('verse');
            loadVerse(verse);
            e.stopPropagation();
        });
    }
}
function deleteMarker(verse_id) {
    $.post('/dcodex/ajax/delete-location/', { manuscript_id:current_manuscript_id, verse_id:verse_id }, function(response) {
        removeMarkerDisplay(verse_id);
    });
}
function removeMarkerDisplay( verseID ) {
    verseMap = $('#verseMap'+verseID);			
    verseMapX = $('#verseMapX'+verseID);
    verseReference = $('#verseReference'+verseID);			
    
    verseMap.remove();
    verseMapX.remove();
    verseReference.remove();	
}

function setup_manuscript_images_lazy_load(pdf_filename, manuscript_id) {
	pageImageController = $('.pageImage').lazy({
		chainable: false,
		appendScroll: $('#manuscript'),
		beforeLoad: function(element) {
			console.log("start loading " + element.prop("tagName"));
			console.log("data-src " + element.data("src"));
		},
		afterLoad: function(element) {
			var page = element.data('page');
			$.getJSON('/dcodex/ajax/page-locations-json/', { manuscript_id:manuscript_id, pdf_filename:pdf_filename, page:page }, function (data) {
				$.each(data, function(k, v) {
					loadVerseMarker(v);								
				});
			  });
			finalizeMarker();
        },
        effect: 'fadeIn',
        effectTime: 400,
        onError: function(element) {
            console.log('error loading ' + element.data('src'));
        }
	});

}
function finalizeMarker( ) {
    marker = $('#marker');
    console.log("Setting up Marker");		
    page = marker.data('page');
    y0 = marker.data('y0');
    placeMarkerAt( page, y0 );
//alert('placeMarkerAt');
    marker.data('toSetup',false);
//		}
    if ( marker.data('toSeek') ) {
        console.log("Seeking Marker");
        //$( "#manuscript" ).scrollTo(marker, 0, {offset:-300});		
        marker.data('toSeek',false);
    }
}
function placeMarkerAt(page, y0) {
    marker = $('#marker');
    var pageDiv = $('#page'+page);	
    if (! pageDiv.length)
        return;
    relativeY = pageDiv.height()*y0;
    y = pageDiv.offset().top + relativeY + $('#manuscript').scrollTop();
    x = 0;
    console.log("Located page: "+page);
    console.log("Located y0: "+y0);				
    console.log("Located pageDiv.offset().top: "+pageDiv.offset().top);				
    console.log("Located relativeY: "+relativeY);				
    console.log("Calculated y: "+y);				

    marker.css('top',y+"px");
    $('#markerX').css('top',y+"px");
    $('#markerX').css('left',x+"px");
    marker.css('visibility','visible');
    marker.show();
    //alert('show marker');
    $('#markerX').css('visibility','visible');	
    
    $('#marker').show();
    $('#markerX').show();
    
}

function load_thumbnails( pdf_filename ) {
    $('#thumbnails').load("/dcodex/ajax/thumbnails/"+pdf_filename, function() {
        console.log( "thumbnails loaded" );
        
        $('.thumbnail').lazy({
            appendScroll: $('#thumbnails'),
            beforeLoad: function(element) {
            },
            afterLoad: function(element) {
            },
            effect: 'fadeIn',
            effectTime: 400,
            onError: function(element) {
                console.log('error loading ' + element.data('src'));
            }
        });
        $('.thumbnailContainer').click(function(e) {
            var page = $(this).data('page');		
            $('#manuscript').scrollTo('#page'+page, 0, {offset:-300});
        });         
        $('.thumbnailContainer').dblclick(function(e) {
            $('#tagPageWindow').show();
            var page = $(this).data('page');		
            $('#saveTagPage').data('page', page );
        });
           
    });
}

function setup_manuscript_image_click() {
	$( ".pageContainer" ).click(function(e) {
		var page = $(this).data('page');

        var posX = $(this).position().left,
            posY = $(this).position().top;
            
        var relativeX = e.pageX - posX;
        var relativeY = e.pageY - posY;

        var y0 = relativeY/$(this).height();
        
        var x = (e.pageX - $('#manuscript').offset().left) + $('#manuscript').scrollLeft();
		var y = (e.pageY - $('#manuscript').offset().top) + $('#manuscript').scrollTop();
		
	    var x0 = x/$(this).width();


		$('#marker').css('top',y+"px");
		$('#markerX').css('top',y+"px");
		$('#marker').data('keepLocation', true);
		
		$('#markerX').css('left',x+"px");

		$('#marker').css('visibility','visible');
		$('#markerX').css('visibility','visible');
		$('#marker').show();
		$('#markerX').show();		
//		alert('make vis');
//		alert(page);
		$("#saveLocation").data("page", page);
		$("#saveLocation").data("y0", y0);		
		$("#saveLocation").data("x0", x0);		

		var height = $('#locationOptions').height();
		var width = $('#locationOptions').width();	
		
		var locationOptionsY = e.pageY -height - 80;
		var locationOptionsX = e.pageX -width*0.5;
//		alert($(window).width());		
		if (locationOptionsX < 0) {
			locationOptionsX = 0;
		}
		
		if (locationOptionsX+width > $(window).width()) {
			alert($(window).width());
//			locationOptionsX = $(window).width()-width-300;
//			locationOptionsX = 0;	
//			alert(locationOptionsX);
			$('#locationOptions').css('left', 'auto' );
			$('#locationOptions').css('right', '0px' );
					
		}
		else {
			$('#locationOptions').css('left', locationOptionsX );
			$('#locationOptions').css('right', 'auto' );
		}
		$('#locationOptions').data('offset', locationOptionsY + $('#manuscript').scrollTop() );
		$('#locationOptions').css('top', locationOptionsY);
		$('#locationOptions').show();
		$('input[name=locationOptionsY]').val(locationOptionsY);
		$('input[name=locationOptionsX]').val(locationOptionsX);
		$('#approximateVerseFromPosition').load("/ApproximateVerseFromPosition.php?manuscript=manuscriptID&msPDF=pdf&pageNumber="+page+"&y0="+y0, function() {
			//setLoadVerseLink();
		});
		$('#saveLocation').focus();		
	});    
}

function load_pdf_images( pdf_filename, manuscript_id ) {
    $('#manuscriptImages').load("/dcodex/ajax/pdf-images/"+pdf_filename, function() {
        console.log( "pdf images loaded" );
        setup_manuscript_images_lazy_load(pdf_filename, manuscript_id);
        setup_manuscript_image_click();
    });
}
        

function load_pdf( pdf_filename, manuscript_id ) {
    load_thumbnails( pdf_filename );
    load_pdf_images( pdf_filename, manuscript_id );
    
    current_manuscript_id = manuscript_id;
    current_pdf_filename  = pdf_filename;
}

function highlightVerseMarker( verse_id, manuscript_id, highlightedCallback = null  ) {
    color = 'purple';
    normalColor = 'green';		
    $('.verseMarker').css('background-color',normalColor);
    $('.verseMarkerX').css('background-color',normalColor);
    $('.verseReference').css('color',normalColor);
    console.log("highlightVerseMarker : "+verse_id);
//		alert('highlightVerseMarker');

    verseMap = $('#verseMap'+verse_id);
    console.log("highlightVerseMarker verseMap: "+verseMap.length);
    
    if (verseMap.length == 0) {
        console.log("verseMap.length == 0: ");
        console.log("about to post dcodex/ajax/verse-location-json/");
        $.post('/dcodex/ajax/verse-location-json/', { manuscript_id:manuscript_id, verse_id:verse_id }, function(data) {
            console.log("responded to post dcodex/ajax/verse-location-json");
            // Log the response to the console
            // load data.page
            // Move marker to y0
            //        return {'manuscript_id': self.manuscript.manuscript_id, 'pdf_filename': self.pdf.filename, 'x':self.x, 'y':self.y, 'page':self.page, 'verse_id':self.verse.id, 'ref':self.verse.reference_abbreviation(), 'tooltip':'', 'exact': True if self.pk else False }
            
            console.log("verse-location-json response: " + data);
            page = data.page;
            y0 = data.y;
            pdf_filename = data.pdf_filename
            
//            if (pdf_filename == null)
//                return;
            if ( current_pdf_filename != data.pdf ) {
//                location.reload(); // If verse isn't in current PDF then reload everything - should do this via AJAX
            }

            // Load Page if necessary
            //console.log("pageImageController: "+pageImageController);
            pageImage = $('#pageImage'+page);
            console.log( "is handled: ", pageImage.data('loaded') )

            if ( pageImage.data('loaded') ) {
                placeMarkerAt( page, y0 );
                console.log("VerseLocation Response: "+data);
                  
                if (typeof highlightedCallback == "function") highlightedCallback( $('#marker') );
            }
            else {
//					alert('later');
                delay = 10;

                // Hack - wait 10ms and try again to see if the images have loaded
                if (pageImageController!= null) {
                    pageImageController.force($('#pageImage'+(page-1)));
                    pageImageController.force($('#pageImage'+page));
                }


                /*
                */
                setTimeout(function() {
                    console.log('trying again in 10ms');
                    highlightVerseMarker(verse_id, manuscript_id, highlightedCallback);
                }, delay);

                
                //$('#marker').data('page', page);
                //$('#marker').data('y0', y0);
                //$('#marker').data('toSetup', true);
            }
        }, "json");
    }
    else {
        verseMap.css('background-color',color);
        $('#verseMapX'+verse_id).css('background-color',color);
        $('#verseReference'+verse_id).css('color',color);
        //alert('marker hide');
        $('#marker').hide();
        $('#markerX').hide();
        console.log( "is handled: ", pageImage.data('loaded') )

        if (typeof highlightedCallback == "function") highlightedCallback(verseMap);			
    }
}


function load_comparison(verse_id, manuscript_id) {
    $( "#comparison" ).load( "/dcodex/ajax/comparison/", { manuscript_id:manuscript_id, verse_id:verse_id }, function() {
        $(".mshover").hover(function(){
            $('#msHover').load("/dcodex/ajax/transcription-mini/", { manuscript_id:$(this).data('manuscriptid'), verse_id:verse_id } );
            $('#msHover').show();
        }, function() {
            $('#msHover').hide();	  
            $('#msHover').html("");
        });
        $(".copyToTranscription").click(function(e) {
            transcription = $(this).data('transcription');

            var textarea = $( "#transcription" );
            var text = textarea.val();				
            text+=transcription
            setTranscription(text);
            return false;
        });
    } );
}

function shrinkFontToFit( element ) {
    counter = 1;
    while ( element.get(0).scrollHeight > element.height() + 5 ) {
        console.log("trying: " +counter+' '+element.css('font-size')+' '+element.get(0).scrollHeight +' '+element.height());
        delta = parseInt(parseInt(element.css('font-size'))/4);
        if (delta < 1)
            delta = 1;
        console.log('-='+delta);
        element.css('font-size', '-='+delta);
        counter += 1;
        if (counter>100)
            break;
    }
    console.log("resolved: "+counter+' '+element.css('font-size')+' '+element.get(0).scrollHeight +' '+element.height());
}

function setTranscriptionRTL() {
    var textarea = $( "#transcription" );	
    textarea.css('direction', "rtl");		
    $( "#directionToggle" ).html("LTR");	
}
function setTranscriptionLTR() {
    var textarea = $( "#transcription" );	
    textarea.css('direction', "ltr");
    $( "#directionToggle" ).html("RTL");
}

$( "#directionToggle" ).click(function(e) {
    var textarea = $( "#transcription" );
    var direction = textarea.css('direction');
    if ( direction == "rtl" ) {
        setTranscriptionLTR();		
    }
    else {
        setTranscriptionRTL();
    }
});

function resetTranscriptionFont() {
    element = $('#transcription');	
    element.css('font-size', '48px');
}
function setTranscription( text ) {
//		alert('setTranscription');

    $('#transcription').val(text);
    resizeTranscription();
    if ( text.length == 0 )
        return;
    if ( isRTL(text) ) {
//			alert('rtl');
        setTranscriptionRTL();
    }
    else {
//			alert('ltr');		
        setTranscriptionLTR();
    }
}

function resizeTranscription( ) {
    return; // hack
    element = $('#transcription');
    shrinkFontToFit(element);
}

function isRTL( text ) {
    var ltrChars    = 'A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02B8\u0300-\u0590\u0800-\u1FFF'+'\u2C00-\uFB1C\uFDFE-\uFE6F\uFEFD-\uFFFF',
        rtlChars    = '\u0591-\u07FF\uFB1D-\uFDFD\uFE70-\uFEFC',
        rtlDirCheck = new RegExp('^[^'+ltrChars+']*['+rtlChars+']');

    divText = "<div>"+text+"</div>";
    str = $(divText).text();
    var i = str.length;
    rltCount = 0
    while (i--) {
        s = str.charAt(i);
        if ( rtlDirCheck.test(s) == true )
            rltCount++;
    }
//		alert("text "+text);				
//		alert("str "+str);				
//		alert("rltCount "+rltCount);				
//		alert("str.length "+str.length);				
    if ( rltCount/str.length > 0.5 )
        return true;
    return false;
}

function register_close_buttons() {
    $( ".closeButton" ).click(function(e) {
        $( this ).parent().hide();						
    });
}

	


function load_verse_search_div(verse_id, manuscript_id) {
    $( "#verseSearch" ).load( "/dcodex/ajax/verse-search/", { manuscript_id:manuscript_id, verse_id:verse_id }, function() {
        $( "#seekVerseButton" ).click(function(e) {
            book_id = $('#bookSelect').val();
            chapter = $('#chapterSelect').val();				
            verse = $('#verseSelect').val();
            $.post('/dcodex/ajax/verse-id/', { manuscript_id:manuscript_id, book_id:book_id, chapter:chapter, verse:verse }, function(response) {
                verse_id = response;
                seekVerse(verse_id, manuscript_id);
            });
            return false;
        });
        $( ".seekVerseLink" ).click(function(e) {
            verse_id = $(this).data('verseid');
            seekVerse(verse_id, manuscript_id);
            return false;
        });
        $( "#showManuscriptSelect" ).click(function(e) {
            $('#manuscriptSelectWindow').load("/dcodex/ajax/select-manuscript/",  function(response) {
                register_close_buttons();
                $( ".manuscriptSelect" ).click(function(e) {
                    ms = $(this).data('manuscript');
                    window.location.replace("/dcodex/ms/"+ms+"/"+verse_id);		
                });	
                $( "#manuscriptSelectWindow" ).show();
            });
        });
        $('#transcription').keypress(function(){
            resizeTranscription();
        });
        
    });
}
function load_verse_location_popup(verse_id, manuscript_id) {
    $( "#locationOptions" ).load( "/dcodex/ajax/location-popup/", { manuscript_id:manuscript_id, verse_id:verse_id }, function() {
        register_close_buttons();
        $( "#saveLocation" ).click(function(e) {
            var page = $("#saveLocation").data("page");
            var y = $("#saveLocation").data("y0");
            var x = $("#saveLocation").data("x0");		
            console.log("SaveLocation try: ");

            $.post('/dcodex/ajax/save-location/', { manuscript_id:manuscript_id, verse_id:verse_id, pdf_filename:current_pdf_filename, page:page, y:y, x:x }, function(response) {
                loadVerseMarker(response);
                highlightVerseMarker(verse_id);	    
                console.log("SaveLocation Response: "+response);
                var textarea = $( "#transcription" );
                textarea.focus();
            }, "json");
            $('#locationOptions').hide();
            return false;
        });
        setLoadVerseLink();
    });
}

function load_verse_transcription(verse_id, manuscript_id) {
    $.post('/dcodex/ajax/transcription-text/', { manuscript_id:manuscript_id, verse_id:verse_id }, function(response) {
        var textarea = $( "#transcription" );
        resetTranscriptionFont();
        setTranscription(response);
        textarea.focus();			
        console.log("TranscriptionText Response: "+response);
    });
}

function load_verse_to_title(verse_id, manuscript_id) {
    $.post('/dcodex/ajax/title-json/', { manuscript_id:manuscript_id, verse_id:verse_id }, function(data) {
        $(document).attr("title", data.title);
        window.history.replaceState("object or string", "Manuscript", data.url);
    }, "json");
}


function load_verse( verse_id, manuscript_id ) {
    console.log( "Loading verse: ", verse_id );
    load_comparison( verse_id, manuscript_id );
    load_verse_search_div( verse_id, manuscript_id );
    load_verse_transcription( verse_id, manuscript_id );
    load_verse_to_title( verse_id, manuscript_id );
    load_verse_location_popup( verse_id, manuscript_id );
    
    current_verse_id = verse_id;
}
function seekVerse( verse_id, manuscript_id ) {
    $('#marker').data("keepLocation", false);	
    $("#marker").data('toSeek', true);
    load_verse(verse_id, manuscript_id);
    highlightVerseMarker( verse_id, manuscript_id, function(marker) {
        console.log("Marker in highlightVerseMarker callback:"+marker);
        $( "#manuscript" ).scrollTo(marker, 0, {offset:-300});
        $("#marker").data('toSeek', false);			
    });
}

function setVerseMarkerPosition(verseID) {
    verseMap = $('#verseMap'+verseID);
    verseMapX = $('#verseMapX'+verseID);
    verseReference = $('#verseReference'+verseID);			
    
    x0 = verseMapX.data('x0');
    y0 = verseMapX.data('y0');	
//		y0=0.5;	
    //x0 = 0.1;
    
    page = verseMapX.data('page');		
    
    var pageDiv = $('#page'+page);
    var pageHeight = pageDiv.height();
    var pageWidth = pageDiv.width();		      	
    var top = y0*pageHeight;
    var left = x0*pageWidth;
    verseMap.css( 'top', top+"px" );
    verseMapX.css( 'top', top+"px" );
    verseMapX.css( 'left', left+"px" );
    verseReference.css( 'top', top+"px" );		
}

function resetVerseMarkers() {
    $( ".verseMarkerX" ).each(function() {
        verseID = $(this).data('verseid');
        setVerseMarkerPosition(verseID);
    });
}


$( document ).ready(function() {
    console.log( "Loading from manuscript.js" );    
    $( '#toggleLeftSidebar' ).click(function(e) {
        var middle = $( "#middle" );
        var left = middle.offset().left;
        if ( left > 0 ) {
            middle.animate({ left: '0px' }, function(response) {
                resetVerseMarkers();
            });
        }
        else {
            middle.animate({ left: $('#leftSidebar').width() + 'px' }, function(response) {
                resetVerseMarkers();
            });
        }
    });
	$( '#toggleReferences' ).click(function(e) {
		var middle = $( "#middle" );
		var right = $(window).width() - (middle.offset().left + middle.outerWidth());
		if ( right > 0 ) {
			middle.animate({ right: '0px' }, function(response) {
				resetVerseMarkers();
			});
		}
		else {
		    comparison = $('#comparison')
		    width = comparison.outerWidth();
			middle.animate({ right: width + 'px' }, function(response) {
				resetVerseMarkers();
			});
		}
	});
	$( "#goToPage" ).click(function(e) {

		folio_ref = $('#pageNumberInput').val();

		$.post('/dcodex/ajax/page-number/', { pdf_filename:current_pdf_filename, folio_ref:folio_ref }, function(response) {
			page = parseInt(response);
			$('#manuscript').scrollTo('#page'+page);
		});
		
		return false;
	});
	$('#manuscript').scroll(function(){
		var manuscriptHeight = $(this).height();
		var first = false;		
		var transcriptionEntry = $("#transcriptionEntry");
		var top = transcriptionEntry.offset().top + transcriptionEntry.height();
		var cutOff = top + 0.5*(manuscriptHeight-top);
		$(".pageImage").each( function() {
			var page = $(this).data('page');
			var offset = $(this).offset();
			var pageHeight = $(this).height();
			var pageTopOffset = offset.top;			
			var pageBottonOffset = pageTopOffset+pageHeight;
		
			if (pageTopOffset < cutOff && pageBottonOffset > cutOff && first == false) {
				setCurrentPage(page);
				first=true;
			}
		});
		$('#locationOptions').css('top', $('#locationOptions').data('offset') - $('#manuscript').scrollTop() );
		
	});
	
	$('#tagPageWindowClose').click(function(e) {
		$('#tagPageWindow').hide();	
	});
	
	$('#saveTagPage').click(function(e) {
		var page = $(this).data('page');		
	
		var folio = $( "#tagPageFolioNumber" ).val();
		var side = $( "#tagPageFolioLetter" ).val();

		$.post('/dcodex/ajax/save-folio-ref/', { manuscript_id:current_manuscript_id, pdf_filename:current_pdf_filename, page:page, folio:folio, side:side }, function(response) {
			$('#tagPageWindow').hide();	
			load_thumbnails(current_pdf_filename)
		});

		return false;
	});	
    $('#saveTranscription').click(function(e) {
        var textarea = $( "#transcription" );
        transcription = textarea.val();
        $.post('/dcodex/ajax/save-transcription/', { manuscript_id:current_manuscript_id, verse_id:current_verse_id, transcription:transcription }, function(response) {
            nextVerseID = parseInt(current_verse_id)+1
            console.log( "Progressing to verse: ", nextVerseID );
            load_verse( nextVerseID, current_manuscript_id );
            highlightVerseMarker( nextVerseID, current_manuscript_id );            
        });

        return false;
    });

});