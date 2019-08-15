function load_content(){
  var unread_start = 10;
  var unread_finish = 30;

  var start = -40;
  var finish = -20;
  var all_unread_data_ready = false;
  var all_read_data_ready = false;
  var messages_block = $(".messages");

  function gen_messages_html(data){
      html = '';
          data['messages'].forEach(function(item, i, arr){
            if(item['you_author'] == true){
              html += '<li class="sent">';
                html += '<img src="'+ item['author_photo'] +'" alt="'+ item['author'] +'" />';
                html += '<p>'+ item['message_text'] +'</p>';
              html += '</li>';
            }else{
              html += '<li class="replies">';
                html += '<img src="'+ item['author_photo'] +'" alt="'+ item['author'] +'" />';
                html += '<p>'+ item['message_text'] +'</p>';
              html += '</li>';
            }
          });
    return html;
  };
  messages_block.scroll(function(){
      var scroll_width = messages_block.prop('scrollHeight') - messages_block.scrollTop();
      if(messages_block.scrollTop() == 0){

        if(all_read_data_ready == false){
          $.ajax({
              method: 'GET',
              url: window.location.pathname,
              data: {
                'start': start,
                'finish': finish,
                'key': load_chat_key
              },
              success: function(data) {
                if(data['error']){
                  all_data_ready = true;
                }else{
                  var data = encrypt_chat(crypt, data);

                  var messages = gen_messages_html(data);
                  var s = $(".messages").prop("scrollHeight");

                  $(".messages").children('ul').prepend(messages);

                  start -= 20;
                  finish -= 20;


                  var f = $(".messages").prop("scrollHeight");
                  messages_block.animate({scrollTop: f-s}, 0.001)
                }

              }
          })
        }
      }else if(Math.ceil(scroll_width) == messages_block.prop('clientHeight') | Math.round(scroll_width) == messages_block.prop('clientHeight')) {
        if(all_unread_data_ready == false){
          $.ajax({
              method: 'GET',
              url: window.location.pathname,
              data: {
                'start': unread_start,
                'finish': unread_finish,
                'key': load_chat_key
              },
              success: function(data) {
                if(data['error']){
                  all_unread_data_ready = true;
                  $.ajax({
                    method: 'GET',
                    url: '/chat/read_messages/' + window.location.pathname.split('/')[3] + '/',
                    success: function(data){
                      if(data['result'] == 'all read'){
                        $('#unread').remove();
                      }
                    }
                  })
                }else{
                  var data = encrypt_chat(crypt, data);

                  var messages = gen_messages_html(data);
                  var s = $(".messages").prop("scrollHeight");

                  $(".messages").children('ul').append(messages);

                  unread_start += 20;
                  unread_finish += 20;
                }

              }
          })
        }
      }
  })

}
