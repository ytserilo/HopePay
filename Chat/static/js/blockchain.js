var blockchain_socket = new WebSocket('ws://'+window.location.pathname+'/blockchain/');

function encrypt(msgString, secret) {
    var key = CryptoJS.enc.Utf8.parse(String(secret).slice(0, 16));
    var iv = CryptoJS.lib.WordArray.random(16);
    var encrypted = CryptoJS.AES.encrypt(msgString, key, {
        iv: iv
    });
    var result = iv.concat(encrypted.ciphertext).toString(CryptoJS.enc.Base64)

    return result;
}

blockchain_socket.onopen = function(){}

blockchain_socket.onmessage = function(event){
  var data = event.data;

  var start_date = new Date();
  start_date = start_date.getMiliseconds();
  var counter = 0;

  while(true){
    var now = new Date();
    var result = data;

    if(now.getMiliseconds() - start_date <= 500){
      result = CryptoJS.SHA256(result);

      if (result.match( /0/ig ).length == 17){

        var send_data = {
          'hash': result,
          'count': counter,
          'status': 'success',
        };
        send_data = encrypt(JSON.stringify(send_data), $.cookie('csrftoken'));

        blockchain_socket.send(send_data);
        break;
      }
    }else{

      var send_data = {
        'hash': result,
        'count': counter,
        'status': 'fail'
      };
      send_data = encrypt(JSON.stringify(send_data), $.cookie('csrftoken'));

      blockchain_socket.send(send_data);
      break;
    }
    counter++;
  }
}
blockchain_socket.onclose = function(){}
