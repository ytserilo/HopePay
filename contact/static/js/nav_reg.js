var gen_key = undefined;
var encrypter = new JSEncrypt;

function security_connect(){
  $.ajax({
    method: 'GET',
    url: '/auth/rsa/',
    data: {
      'key': Math.floor(Math.random() * Math.floor(999999))
    },
    success: function(data){
      if (data['response'] == 'reload'){
        security_connect();
      }
      else{
        var pubkey = data['pubkey'];
        gen_key = data['key'];
        encrypter.setPublicKey(pubkey);
      }
    }
  });
};

security_connect();

function encrypt_value(stringToBeEncrypted) {
    return encrypter.encrypt(stringToBeEncrypted);
};
var username_modal = $("#username_modal");
var password_modal = $("#password_modal");

var pre_username = undefined;
var pre_password = undefined;

$("#login-modal").on('click', function(){
  $("#so_login").css({'display': 'block', 'background-color': 'rgba(0,0,0,0.5)'});
  $("#so_login").attr('class', 'modal');
});
$("#close_login_modal").on('click', function(){
  $("#so_login").css({'display': 'none', 'background-color': 'rgba(0,0,0,0)'});
  $("#so_login").attr('class', 'modal fade');
});
var swch = false;
var modal_email = undefined;
$("#restore").on('click', function(){
  if(swch == false){
    swch = true;
    $("#restore").html('Увійти');
    $("#modal_body_login").children('.input-group').remove();
    $("#modal_body_login").children('button').remove();

    var html = '';
    html += '<div class="input-group mb-3">';
      html += '<label>Введіть ваш email для відновлення пароля</label>';
    html += '</div>';
    html += '<div class="input-group mb-3">';
        html += '<input type="text" id="email_modal" class="form-control" placeholder="Емайл" aria-label="Емайл" aria-describedby="basic-addon1">';
    html += '</div>';

    $("#modal_body_login").prepend(html);
    $("#modal_body_login").append('<button class="btn btn-primary" style="background-color: #435f7a;" id="restore_password" type="submit">Відновити</button>');

    $('#restore_password').on('click', function(){
      modal_email = $("#email_modal").val();
      $.ajax({
        method: 'GET',
        url: '/auth/email_send/',
        data: {
          'email': encrypt_value(modal_email),
          'restore': true,
          'key': gen_key
        },
        success: function(data){
          if(data['error']){
            $("#modal_body_login").append('<div class="alert alert-danger">'+ data['error'] +'</div>');
          }else{
            var html = '';
            html += '<div class="input-group mb-3">';
                html += '<input type="text" id="pin_modal" class="form-control" placeholder="Пін" aria-label="Пін" aria-describedby="basic-addon1">';
            html += '</div>';
            html += '<button class="btn btn-primary" style="background-color: #435f7a;" id="pin" type="submit">Відновити</button>'

            $("#modal_body_login").children('.input-group').remove();
            $("#modal_body_login").children('button').remove();

            $("#modal_body_login").append(html);

            $("#pin").on('click', function(){
              $.ajax({
                method: 'GET',
                url: '/auth/email_validate/',
                data: {
                  'email': encrypt_value(modal_email),
                  'pin': encrypt_value($("#pin_modal").val()),
                  'key': gen_key
                },
                success: function(data){
                  if(data['result'] == 'OK'){
                    var html = '';
                    html += '<div class="input-group mb-3">';
                        html += '<input type="password" id="password_modal1" class="form-control" placeholder="Придумайте новий пароль" aria-label="Придумайте новий пароль" aria-describedby="basic-addon1">';
                    html += '</div>';
                    html += '<div class="input-group mb-3">';
                        html += '<input type="password" id="password_modal2" class="form-control" placeholder="Підтвердіть пароль" aria-label="Підтвердіть пароль" aria-describedby="basic-addon1">';
                    html += '</div>';
                    html += '<button class="btn btn-primary" style="background-color: #435f7a;" id="newpassword" type="submit">Відновити</button>'

                    $("#modal_body_login").children('.input-group').remove();
                    $("#modal_body_login").children('button').remove();

                    $("#modal_body_login").append(html);

                    $("#newpassword").on('click', function(){
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
                        url: '/auth/restore_password/',
                        data: {
                          'password1': encrypt_value($("#password_modal1").val()),
                          'password2': encrypt_value($("#password_modal2").val()),
                          'email': encrypt_value(modal_email),
                          'key': gen_key
                        },
                        success: function(data){
                          if(data['result'] == 'ok'){
                            window.location.replace('/chat/remittances/');
                          }else{
                            if($("#modal_body_login").children('.alert').length == 0){
                              $("#modal_body_login").append('<div class="alert alert-danger">'+ data['result'] +'</div>')
                            }
                          }
                        }
                      })
                    })
                  }
                }
              })
            })
          }

        }
      })
    });
  }
  else{

    swch = false;
    $("#restore").html('Відновити пароль');
    $("#modal_body_login").children('.input-group').remove();
    $("#modal_body_login").children('button').remove();

    var html = '';
    html += '<div class="input-group mb-3">';
        html += '<input type="text" id="username_modal" class="form-control" placeholder="Логін" aria-label="Логін" aria-describedby="basic-addon1">';
    html += '</div>';
    html += '<div class="input-group mb-3">';
        html += '<input type="password" id="password_modal" class="form-control" placeholder="Пароль" aria-label="Пароль" aria-describedby="basic-addon1">';
    html += '</div>';

    $("#modal_body_login").prepend(html);

    $("#modal_body_login").append('<button class="btn btn-primary" style="background-color: #435f7a;" id="login_in" type="submit">Увійти</button>');

    login();
  }
});

function login(){
  var username_modal = $("#username_modal");
  var password_modal = $("#password_modal");

  username_modal.on('input', function(){
    p = username_modal.parent();
      if (username_modal.val() == ''){
        if(p.children('.input-group').children('.alert-danger').length == 0){
          p.append('<div class="input-group mb-3"><div class="alert alert-danger mb-3">Це поле обов\'язкове</div></div>');
        }
      }
      else{
        if(p.children('.input-group').children('.alert-danger').length != 0){
          p.children('.input-group').children('.alert-danger').remove();
        }
      }
  });
  password_modal.on('input', function(){
    p = password_modal.parent();
      if (password_modal.val() == ''){

        if(p.children('.input-group').children('.alert-danger').length == 0){
          p.append('<div class="input-group mb-3"><div class="alert alert-danger mb-3">Це поле обов\'язкове</div></div>');
        }
      }
      else{
        if(p.children('.input-group').children('.alert-danger').length != 0){
          p.children('.input-group').children('.alert-danger').remove();
        }
      }
  });
  $("#login_in").on('click', function(){
    if(username_modal.val() != '' && password_modal.val() != ''){
      function csrfSafeMethod(method) {
          return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
      };
      if (pre_username != username_modal.val() || pre_password != password_modal.val()) {
        $.ajaxSetup({
            crossDomain: false,
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
                }
            }
        });
        pre_username = username_modal.val();
        pre_password = password_modal.val();
        $.ajax({
          'method': 'POST',
          'url': '/auth/login_in/',
          'data': {
            'password': encrypt_value(password_modal.val()),
            'username': encrypt_value(username_modal.val()),
            'key': gen_key,
          },
          success: function(data){
            if (data['result'] == 'ok'){
              document.location.replace('/chat/remittances/');
            }else{
              if ($("#modal_body_login").children().children('.alert-danger').length == 0){
                $("#modal_body_login").append("<div class='input-group mb-3'><div class='alert alert-danger mb-3'>"+ data['login_error'] +"</div></div>");

              }
            }
          },
        });
      }
    }
  });
};
login();
