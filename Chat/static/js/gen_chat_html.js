function chat(data){
  var html = '';
  html += '<div class="contact-profile" style="position: relative; height: 40px">';
    html += '<button id="settings-remittance" title="Натисніть щоб відкрити налаштування договору"><i class="fa fa-cogs"></i></button>';
    html += '<button id="info-remittance" title="Натисніть щоб отримати інформацію про договір"><i class="fa fa-info"></i></button>';
  html += '</div>';
  html += '<div class="messages">';
    html += '<ul>';

      data['messages'].forEach(function(item, i, arr){

        if(item['you_author'] == true){
          html += '<li class="sent">';
            html += '<img src="'+ item['author_photo'] +'" alt="'+ item['author'] +'" />';
            html += '<p>'+ item['message_text'] +'</p>';
          html += '</li>';

        }else{

          if(item['unread'] == false){
            html += '<li class="replies">';
              html += '<img src="'+ item['author_photo'] +'" alt="'+ item['author'] +'" />';
              html += '<p>'+ item['message_text'] +'</p>';
            html += '</li>';
          }
        }
      });
      try{
        if(data['messages'][data['messages'].length-1]['unread']){
          if(data['messages'][data['messages'].length-1]['unread'] == true){
            html += '<li class="sent" id="unread" style="">Не прочитані повідомлення</li>';
            data['messages'].forEach(function(item, i, arr){
                if(item['unread']){
                  if(item['unread'] == true){
                    html += '<li class="replies">';
                      html += '<img src="'+ item['author_photo'] +'" alt="'+ item['author'] +'" />';
                      html += '<p>'+ item['message_text'] +'</p>';
                    html += '</li>';
                  }
                }
            });
          }
        }
      }
      catch{
          html += '';
      }
  html += '</ul>';
    html += '</div>'
  html += '<div class="message-input">';
    html += '<div class="wrap">';
      html += '<input type="text" id="input_chat" placeholder="Напишіть повідомлення..." />';
      html += '<button class="submit" id="send_message">';
        html += '<i class="fa fa-paper-plane" aria-hidden="true"></i>';
      html += '</button>';

    html += '</div>';
  html += '</div>';
  return html;
}

function gen_html(data){
  html = '';
  html += '<div class="content">';
  if(data['fin_remittance']){
    if(data['fin_remittance']['successful'] == true){
      html += '<div class="messages" style="text-align: center;">';
      html += '<i class="fa fa-check-circle" style="display: flex;justify-content: center;font-size: 150px;margin-top: calc(145px);text-align: center;"></i>';
      html += '<p style="font-size: 40px;">Договір успішний</p></div>';
    }
    else if(data['fin_remittance']['successful'] == false){
      html += '<div class="messages" style="text-align: center;">';
      html += '<i class="fa fa-exclamation-triangle" style="display: flex;justify-content: center;font-size: 150px;margin-top: calc(145px);text-align: center;"></i>';
      html += '<p style="font-size: 40px;">Договір відкликаний</p></div>';
    }
    else{
      var text = chat(data);
      html += text;
    }
  }else{
    var text = chat(data);
    html += text;
  }


  html += '</div>';
  return html;
}
