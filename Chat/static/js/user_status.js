function set_status_style(status_name, user_id){
  var obj = $(".user-"+user_id + "");
  var chld = obj.children('.contact-status');
  chld.attr('class', 'contact-status ' + status_name + '');
}

function UserStatus(){
  this.user_id = $("user_id").val();
  this.socket = new WebSocket('ws://'+window.location.host + '/userstatus/');
  socket = this.socket;

  this.create_websocket_connect = function(){
    socket.onopen = function(event){
      var self_id_user = $("user_id").val();
      var status = document.getElementById("profile-img");

      set_status_style('online', this.user_id);
      status.setAttribute('class', 'online');

      socket.send(JSON.stringify({'status': 'online'}));
    }

    socket.onmessage = function(event){
    var data = JSON.parse(event.data);

    if(data['status']){
      var status = 'contact-status ' + data["status"];
      var id = data["id"];
      var obj = $(".user-"+id + "");

      var chld = obj.children('.contact-status');
      chld.attr('class', status);
    }
    else if(data['room_id']){
      if(data['room_id'] == window.location.pathname.split('/')[3]){
          read_messages();
        }
      else{
          var len_messages = data['length-unread-messages'];
          $("#"+ data['room_id'] +"").children('.preview').html('Кількість не прочитаних : ' + len_messages + '');
      }
    }
  }

    $("#status-online").on('click', function(){
      set_status_style('online', this.user_id);
      socket.send(JSON.stringify({'status': 'online'}));
    });

    $("#status-offline").on('click', function(){
      set_status_style('offline', this.user_id);
      socket.send(JSON.stringify({'status': 'offline'}));
    });

    $("#status-away").on('click', function(){
      set_status_style('away', this.user_id);
      socket.send(JSON.stringify({'status': 'away'}));
    });

    $("#status-busy").on('click', function(){
      set_status_style('busy', this.user_id);
      socket.send(JSON.stringify({'status': 'busy'}));
    });

    socket.onclose = function(event){console.log('close')}
  }
}
var user = new UserStatus();
user.create_websocket_connect();
