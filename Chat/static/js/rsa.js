var load_chat_key = Math.floor(Math.random() * Math.floor(999999));
crypt = new JSEncrypt({
    default_key_size: 1024
});
function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};
$.ajaxSetup({
    crossDomain: false,
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
        }
    }
});
$.ajax({
  method: 'POST',
  url: '/chat/rsa/',
  data: {
    'public': crypt.getPublicKey(),
    'key': load_chat_key
  },
})
