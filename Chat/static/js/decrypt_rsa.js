function encrypt_chat(crypt, data){
  var text = '';
  var data = JSON.parse(data);
  data.forEach(function(item, i, arr){
    text += crypt.decrypt(item);
  });
  return JSON.parse(text);
}
