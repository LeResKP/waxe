// Event on the select when we want to create a new XML file
$(document).on('change', '.dtd-urls', function(){
    var dtdUrl = $(this).val();
    if(dtdUrl){
        var $this = $(this);
        var url = $this.data('href');
        var select = $this.parents('form').find('.dtd-tags');
        select.html('');
        waxe.ajax.GET(url + '?dtd-url=' + dtdUrl, function(data){
            for(var index in data.tags){
                var v = data.tags[index];
                select.append($('<option>').attr('value', v).html(v));
            }
        });
    }
});