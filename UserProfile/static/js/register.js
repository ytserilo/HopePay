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
}
security_connect();

function encrypt_value(stringToBeEncrypted) {
    return encrypter.encrypt(stringToBeEncrypted);
}

var username = $("#id_username");
var email = $("#id_custom_email");
var password1 = $("#id_password1");
var password2 = $("#id_password2");
var first_name = $("#id_first_name");
var last_name = $("#id_last_name");

var cnt = $("#continue");
cnt.on('click', function(){
  if($(".alert").length == 0 && username.val() != '' && email.val() != '' && password1.val() != '' && password2.val() != '' && first_name.val() != '' && last_name.val() != '' && $('#accept').prop('checked')){

    $.ajax({
      url: '/auth/email_send/',
      method: 'GET',
      data: {
        'email': encrypt_value(email.val()),
        'key': gen_key
      },
      success: function(data){
        $("#so_email").css({'display': 'block', 'background-color': 'rgba(0, 0, 0, 0.5)'});
        $("#so_email").attr('class', 'modal')
      }
    })
  }
});

$("#close_email_modal").on('click', function(){
  $("#so_email").css({'display': 'none', 'background-color': 'rgba(0, 0, 0, 0)'});
  $("#so_email").attr('class', 'modal fade')
});

$("#btn_pin").on('click', function(){

  $.ajax({
    method: 'GET',
    url: '/auth/email_validate/',
    dataType: 'json',
    data: {
      'email': encrypt_value(email.val()),
      'pin': encrypt_value($("#pin").val()),
      'key': gen_key
    },
    success: function(data){
      if(data['result'] == 'OK'){
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
          url: '/auth/register/',
          dataType: 'json',
          data: {
            'custom_email': encrypt_value(email.val()),
            'password2': encrypt_value(password2.val()),
            'password1': encrypt_value(password1.val()),
            'username': encrypt_value(username.val()),
            'first_name': encrypt_value(first_name.val()),
            'last_name': encrypt_value(last_name.val()),
            'key': gen_key
          },
          success: function(data){
            window.location.replace('/auth/profile/');
          }
        })

      }else{
        var div = $("#email_customer");
        if(div.children('.alert-danger').length != 0){
          div.children('.alert-danger').remove();
          div.append('<div class="alert alert-danger">Вы ввели не верный пин-код</div>');
        }
        else{
          div.append('<div class="alert alert-danger">Вы ввели не верный пин-код</div>');
        }
      }
    },
    error: function(){
      alert("error");
    }
  })
})

first_name.on('blur', function(){
  var div = first_name.parent();
  if(first_name.val() == ''){
    if(div.children('.alert-danger').length != 0){
      div.children('.alert-danger').remove();
      div.append('<div class="alert alert-danger">Це поле обов\'язкове</div>');
    }
    else{
      div.append('<div class="alert alert-danger">Це поле обов\'язкове</div>');
    }
  }
  else{
      if(div.children('.alert-danger').length != 0){
        div.children('.alert-danger').remove();
      }
  }
});

last_name.on('blur', function(){
  var div = last_name.parent();
  if(last_name.val() == ''){
    if(div.children('.alert-danger').length != 0){
      div.children('.alert-danger').remove();
      div.append('<div class="alert alert-danger">Це поле обов\'язкове</div>');
    }
    else{
      div.append('<div class="alert alert-danger">Це поле обов\'язкове</div>');
    }
  }
  else{
      if(div.children('.alert-danger').length != 0){
        div.children('.alert-danger').remove();
      }
  }
});

username.on('blur', function(){
  var div = username.parent();
 if(username.val() != ''){
    $.ajax({
      url: '/auth/register/',
      method: 'get',
      dataType: 'json',
      data: {
        'username': encrypt_value(username.val()),
        'key': gen_key
      },
      success: function(data){
        var text_error = $('.text-danger');

        if(data['result_login'] != 'OK'){
          if(div.children('.alert-danger').length != 0){
            div.children('.alert-danger').remove();
            div.append('<div class="alert alert-danger">'+ data['result_login'] +'</div>');
          }
          else{
            div.append('<div class="alert alert-danger">'+ data['result_login'] +'</div>');
          }
        }
        else{
          if(div.children('.alert-danger').length != 0){
              div.children('.alert-danger').remove();
          }
        }
      }
    })
  }
  else{
    if(div.children('.alert-danger').length != 0){
      div.children('.alert-danger').remove();
      div.append('<div class="alert alert-danger">Це поле обов\'язкове</div>');
    }
    else{
      div.append('<div class="alert alert-danger">Це поле обов\'язкове</div>');
    }
  }
});

email.on('blur', function(){
  var div = email.parent();
  if(email.val() != ''){
    $.ajax({
      url: '/auth/register/',
      method: 'get',
      dataType: 'json',
      data: {
        'email': encrypt_value(email.val()),
        'key': gen_key
      },
      success: function(data){
        var text_error = $('.text-danger');

        if(data['result_email'] != 'OK'){
          if(div.children('.alert-danger').length != 0){
            div.children('.alert-danger').remove();
            div.append('<div class="alert alert-danger">'+ data['result_email'] +'</div>');
          }
          else{
            div.append('<div class="alert alert-danger">'+ data['result_email'] +'</div>');
          }
        }
        else{
          if(div.children('.alert-danger').length != 0){
              div.children('.alert-danger').remove();
            }
        }
      }
    })
  }
  else{
    if(div.children('.alert-danger').length != 0){
      div.children('.alert-danger').remove();
      div.append('<div class="alert alert-danger">Це поле обов\'язкове</div>');
    }
    else{
      div.append('<div class="alert alert-danger">Це поле обов\'язкове</div>');
    }
  }
});

password1.on('blur', function(){
  var div1 = password1.parent();
  var div2 = password2.parent();

  if(password1.val() != ''){
      var result_re = password1.val().match(/(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z]{8,}/);
      if (result_re != null){
        if(div1.children('.alert-danger').length != 0){
          div1.children('.alert-danger').remove();
        }
        if(password1.val() && password2.val() && password1.val() == password2.val()){
          if(div2.children('.alert-danger').length != 0){
            div2.children('.alert-danger').remove();
          }
        }
      }
      else{
        if(div1.children('.alert-danger').length != 0){
          div1.children('.alert-danger').remove();
          div1.append('<div class="alert alert-danger">Введіть пароль не менше 8 символів використовуючи цифри, латиницю і принаймні одну велику літеру</div>');
        }
        else{
          div1.append('<div class="alert alert-danger">Введіть пароль не менше 8 символів використовуючи цифри, латиницю і принаймні одну велику літеру</div>');
        }
      }
    if(password1.val() && password2.val() && password1.val() != password2.val()){
      if(div2.children('.alert-danger').length != 0){
        div2.children('.alert-danger').remove();
        div2.append('<div class="alert alert-danger">Паролі не співпадають</div>');
      }
      else{
        div2.append('<div class="alert alert-danger">Паролі не співпадають</div>');
      }
    }
  }
  else{
    if(div1.children('.alert-danger').length != 0){
      div1.children('.alert-danger').remove();
      div1.append('<div class="alert alert-danger">Це поле обов\'язкове</div>');
    }
    else{
      div1.append('<div class="alert alert-danger">Це поле обов\'язкове</div>');
    }
  }
});
password2.on('blur', function(){
  var div1 = password1.parent();
  var div2 = password2.parent();
  if(password2.val() != ''){
      var result_re = password1.val().match(/(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z]{8,}/);
      if (result_re != null){
        if(div1.children('.alert-danger').length != 0){
          div1.children('.alert-danger').remove();
        }
        if(password1.val() && password2.val() && password1.val() == password2.val()){
          if(div2.children('.alert-danger').length != 0){
            div2.children('.alert-danger').remove();
          }
        }
      }
      else{
        if(div1.children('.alert-danger').length != 0){
          div1.children('.alert-danger').remove();
          div1.append('<div class="alert alert-danger">Введіть пароль не менше 8 символів використовуючи цифри, латиницю і принаймні одну велику літеру</div>');
        }
        else{
          div1.append('<div class="alert alert-danger">Введіть пароль не менше 8 символів використовуючи цифри, латиницю і принаймні одну велику літеру</div>');
        }
      }
    if(password1.val() && password2.val() && password1.val() != password2.val()){
      if(div2.children('.alert-danger').length != 0){
        div2.children('.alert-danger').remove();
        div2.append('<div class="alert alert-danger">Паролі не співпадають</div>');
      }
      else{
        div2.append('<div class="alert alert-danger">Паролі не співпадають</div>');
      }
    }
  }
  else{
    if(div2.children('.alert-danger').length != 0){
      div2.children('.alert-danger').remove();
      div2.append('<div class="alert alert-danger">Це поле обов\'язкове</div>');
    }
    else{
      div2.append('<div class="alert alert-danger">Це поле обов\'язкове</div>');
    }
  }
});




var pre_username = undefined;
var pre_password = undefined;
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
              window.location.replace('/chat/remittances/');
            }else{
              if ($("#modal_body_login").children('.input-group').children('.alert-danger').length == 0){
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
$("#close_login_modal").on('click', function(){
  $("#so_login").css({'display': 'none', 'background-color': 'rgba(0, 0, 0, 0)'});
  $("#so_login").attr('class', 'modal fade');
});
function popup_login(){
  $("#so_login").css({'display': 'block', 'background-color': 'rgba(0, 0, 0, 0.5)'});
  $("#so_login").attr('class', 'modal');
};
