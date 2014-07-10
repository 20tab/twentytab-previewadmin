django.jQuery(function($){

    function close_preview(){
        $(this).parents('.preview-content').fadeOut();
        return false;
    }

    $('.preview-item').on('click', function(){
        var url = window.location.pathname + $(this).attr('href');
        var $this = $(this);
        var content = $this.siblings('.preview-content');
        if(content.is(':visible')){
            content.fadeOut();
        }
        else if(content.is(':hidden')){
            $.ajax({
                url: url,
                success: function(data){
                    content.html(data);
                    $('.preview-content').fadeOut();
                    $('.close-preview').bind('click', close_preview);
                    content.fadeIn();
                }
            });
        }
        return false;
    });


});