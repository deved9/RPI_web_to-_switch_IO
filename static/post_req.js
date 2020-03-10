function switch_pin(x){
    let custom_object = {
        "pin":x
    }
    $.ajax({
        type: 'POST',
        url: window.location.href.split("/")[0] + 'api_set',
        data: custom_object,
        success: function(){
            location.reload(true)
        },
        error: function(e){
            console.log('ERROR! ', e);
        }
    });
}
