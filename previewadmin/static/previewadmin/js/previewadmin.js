django.jQuery(function($){

    function close_preview(){
        $(this).parents('.preview-content').fadeOut();
        return false;
    }

    $('body').append('<div id="preview-content-loader-over" class="">'+
        '<img src="/static/previewadmin/img/loader.gif" alt="Loading"></div>');

    $('.preview-item').on('click', function(){
        $('#preview-content-loader-over').addClass('display');
        var url = window.location.pathname + $(this).attr('href');
        var qs = window.location.search;
        var $this = $(this);
        var content = $this.siblings('.preview-content');
        if(content.is(':visible')){
            content.fadeOut();
        }
        else if(content.is(':hidden')){
            $.ajax({
                url: url+qs,
                success: function(data){
                    content.html(data);
                    $('.preview-content').fadeOut();
                    $('.close-preview').bind('click', close_preview);
                    content.fadeIn();
                    $('#preview-content-loader-over').removeClass('full_opacity display');
                }
            });
        }
        return false;
    });


});