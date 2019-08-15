var room_id = undefined;
function create_invite(){
  $("#create_invite").on('click', function(){

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
      url: '/remittance/create_invite_link/',
      method: 'POST',
      data: {
        'room_id': window.location.pathname.split('/')[3]
      },
      success: function(data){
        var link = add_invitation(data);
        $(".messages ul").append(link);
        $(".messages").animate({ scrollTop: $('.messages').prop('scrollHeight') }, "fast");
      }
    })
  });
};

var individual_chat = new IndividualChat();
function send_smash(){individual_chat.send_smash()}
function remittance_settings_and_info(){individual_chat.remittance_settings_and_info()}
function open_chat(unique_link){individual_chat.open_chat(unique_link)}
function accept_confirmation(changes_id){individual_chat.accept_confirmation(changes_id)}
function pay(){individual_chat.pay()}
function send(){individual_chat.send()}
function confirm(){individual_chat.confirm()}
function cencell(){individual_chat.cencell()}
function create_new_suggestions(){individual_chat.create_new_suggestions()}
