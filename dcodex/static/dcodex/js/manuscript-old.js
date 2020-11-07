$( document ).ready(function(e) {
	
	$( ".manuscriptSelect" ).click(function(e) {
//		alert('manuscriptSelect');
		ms = $(this).data('manuscript');
		window.location.replace("/Manuscript.php?manuscript="+ms+"&verseID="+currentVerseID);		

//		window.history.replaceState("object or string", "Manuscript", );		
//		location.reload();
		
	});	
	$( '.manuscriptLoad' ).click(function(e) {


		pdf=$(this).data('pdf');
		manuscriptID=$(this).data('manuscript');
		window.location.replace("/Manuscript.php?msPDF="+pdf+"&manuscript="+manuscriptID+"&verseID="+currentVerseID);		
	});
	
	$( ".teiInputClose" ).click(function(e) {
		$( ".teiInput" ).hide();
		$( "#teiOptions" ).hide();				
	});
	$( ".teiOption" ).click(function(e) {
		var id = this.id;
		var left = $( "#teiOptions" ).offset().left;
		var top = $( "#teiOptions" ).offset().top;

		var teiOption = id.substr(9);
		var input = $( "#teiInput"+teiOption );
		input.css({top: top,left: left}).show();
		$( "#teiOptions" ).hide();		
//		alert(teiOption);
	});
	$( "#teiOptionsView" ).click(function(e) {
		var left = $(this).offset().left - 200;
		var top = $(this).offset().top;
//		$( "#teiOptions" ).css({top: top,left: left}).toggle();
		$( "#teiOptions" ).toggle();
	});
	$( "#teiInputPBAdd" ).click(function(e) {
		$( ".teiInput" ).hide();
		var textarea = $( "#transcription" );
		var start = textarea.prop('selectionStart');

		var val = textarea.val();
		var teiInputPBfolio = $( "#teiInputPBfolio" ).val();
		var teiInputPBfacs = $( "#teiInputPBfacs" ).val();
//		alert(val);
		var markup = '<pb n="'+teiInputPBfolio+'" facs="'+teiInputPBfacs+'"/>';
		setTranscription(val.slice(0,start) + markup + val.substr(start));
		textarea.focus();			
		//alert(val.slice(0,start));
	});
	$( "#teiOptionPB" ).click(function(e) {
		currentThumbnail = $( "#thumbnail"+currentPage );
		facs = '<?=$msPDF;?>-'+currentPage+'.jpg';
		
		$( "#teiInputPBfolio" ).val(currentThumbnail.data('folio'));
		$( "#teiInputPBfacs" ).val(facs);	
	});
	$( "#teiInputGAPAdd" ).click(function(e) {
		$( ".teiInput" ).hide();
		var textarea = $( "#transcription" );
		var start = textarea.prop('selectionStart');

		var val = textarea.val();
		var teiInputGAPextent = $( "#teiInputGAPextent" ).val();
		var teiInputGAPreason = $( "#teiInputGAPreason" ).val();
		var markup = '<gap extent="'+teiInputGAPextent+'" reason="'+teiInputGAPreason+'"/>';
		setTranscription(val.slice(0,start) + markup + val.substr(start));
		textarea.focus();			
	});
	$( "#teiInputLBAdd" ).click(function(e) {
		$( ".teiInput" ).hide();
		var textarea = $( "#transcription" );
		var start = textarea.prop('selectionStart');

		var val = textarea.val();
		var teiInputLBbreaking = $( "#teiInputLBbreaking" ).val();
		var markup = '<lb';
		if ( teiInputLBbreaking.length > 0 ) {
			markup += ' breaking="'+teiInputLBbreaking+'"';
		}
		markup += '/>';
		setTranscription(val.slice(0,start) + markup + val.substr(start));
		textarea.focus();			
	});	
	$( "#teiInputUNCLEARAdd" ).click(function(e) {
		$( ".teiInput" ).hide();
		var textarea = $( "#transcription" );
		var start = textarea.prop('selectionStart');

		var val = textarea.val();
		var markup = '<unclear';
		var teiInputUNCLEARreason = $( "#teiInputUNCLEARreason" ).val();		
		if ( teiInputUNCLEARreason.length > 0 ) {
			markup += ' reason="'+teiInputUNCLEARreason+'"';
		}
		var teiInputUNCLEARagent = $( "#teiInputUNCLEARagent" ).val();		
		if ( teiInputUNCLEARagent.length > 0 ) {
			markup += ' agent="'+teiInputUNCLEARagent+'"';
		}
		var teiInputUNCLEARtext = $( "#teiInputUNCLEARtext" ).val();		
		markup += '>'+teiInputUNCLEARtext+'</unclear>';
		setTranscription(val.slice(0,start) + markup + val.substr(start));
		textarea.focus();			
	});	
	$( "#teiInputADDAdd" ).click(function(e) {
		$( ".teiInput" ).hide();
		var textarea = $( "#transcription" );
		var start = textarea.prop('selectionStart');

		var val = textarea.val();
		var teiInputADDplace = $( "#teiInputADDplace" ).val();
		var teiInputADDtext = $( "#teiInputADDtext" ).val();		
		var markup = '<add place="'+teiInputADDplace+'">'+teiInputADDtext+'</add>';
		setTranscription(val.slice(0,start) + markup + val.substr(start));
		textarea.focus();			
	});
	$( "#teiInputHIAdd" ).click(function(e) {
		$( ".teiInput" ).hide();
		var textarea = $( "#transcription" );
		var start = textarea.prop('selectionStart');

		var val = textarea.val();
		var teiInputHIrend = $( "#teiInputHIrend" ).val();
		var teiInputHItext = $( "#teiInputHItext" ).val();		
		var markup = '<hi rend="'+teiInputHIrend+'">'+teiInputHItext+'</hi>';
		setTranscription(val.slice(0,start) + markup + val.substr(start));
		textarea.focus();			
	});
	$( "#teiInputDELAdd" ).click(function(e) {
		$( ".teiInput" ).hide();
		var textarea = $( "#transcription" );
		var start = textarea.prop('selectionStart');
		var end = textarea.prop('selectionEnd');

		var val = textarea.val();
		var teiInputDELrend = $( "#teiInputDELrend" ).val();
		var markup = '<del rend="'+teiInputDELrend+'">'+val.slice(start, end)+"</del>";
		setTranscription(val.slice(0,start) + markup + val.substr(start));
		textarea.focus();			
	});
	
	
	var textarea = $( "#transcription" );
	var val = textarea.val();
	textarea.focus().val("");
	setTranscription(val);
		
	

	
function CopyContainerID(containerid) {
    CopyToClipboard(containerid);
    var text = document.getElementById(containerid).textContent;
    document.getElementById('transcription').focus();
    if (document.getElementById('transcription').value == "") {
        setTranscription(text);
    }
    else {
        alert("Transcription window already has text. New text is just copied to clipboard.");
    }
}
function CopyToClipboard(containerid) {
    if (document.selection) { 
        var range = document.body.createTextRange();
        range.moveToElementText(document.getElementById(containerid));
        range.select().createTextRange();
        document.execCommand("copy"); 

    } else if (window.getSelection) {
        var range = document.createRange();
        range.selectNode(document.getElementById(containerid));
    
        var s = window.getSelection();
        if(s.rangeCount > 0) s.removeAllRanges();

        s.addRange(range);
        document.execCommand("copy");
        //alert("text copied"+containerid) 
    }
}

	

	
		


	
	var currentVerseID;
	function loadVerse( verseID ) {
//		alert( 'load verse' );


		$('.prevVerseLink').data( 'verseid', parseInt(verseID)-1 );
		$('.nextVerseLink').data( 'verseid', parseInt(verseID)+1 );		

		currentVerseID = verseID;
	}
	
	$("#marker").hide();
	$('#marker').data("keepLocation", false);
	
	function setLoadVerseLink() {
//		alert('setLoadVerseLink');
		$( ".loadVerseLink" ).click(function(e) {
//			alert(new Error().stack);
			verseID = $(this).data('verseid');
//			alert('loadVerseLink '+verseID);
			loadVerse(verseID);				
			return false;
		});
	}
	setLoadVerseLink();
	
	
	

	

});	