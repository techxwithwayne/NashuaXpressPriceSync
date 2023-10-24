window.setTimeout(function() {
    $(".notice").fadeTo(500, 0).slideUp(500, function(){
        $(this).remove(); 
    });
}, 12000);