var product_socket = undefined;
function confirm_rate(id){
  var product_id = window.location.href.split('/');
  product_id = product_id[product_id.length-2];
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
    url: '/market/confirm_rate/{}/'.replace('{}', product_id),
    method: 'POST',
    data: {
      'id': id
    },
    success: function(data){
      console.log(data);
    }
  })
}
function product(){

  product_socket = new WebSocket('ws://'+window.location.host+window.location.pathname);

  product_socket.onopen = function(){
    $('#rate').on('click', function(){
      $('.modal').attr('style', 'display: block; background-color: rgba(0,0,0,0.5)');

      $('#send-rate').on('click', function(){
        var description = $("#description");
        var amount = $("#price");
        var pay = $("#pay");

        var data = {
          'description': description.val(),
          'amount': amount.val(),
          'pay': String(pay.prop('checked')),
          'parts': String($("#parts").val()),
        }
        data = JSON.stringify(data);

        if(description.val() != '' && amount != ''){
          if(pay.prop('checked') == true && Number($("#parts").val()) >= 2 && Number($("#parts").val()) <= 12){

          }else if(pay.prop('checked') == true && Number($("#parts").val()) <= 2 || Number($("#parts").val()) >= 12){
            return undefined;
          }
          product_socket.send(data);
        }
      });
    });
  }
  product_socket.onmessage = function(){
    var data = JSON.parse(event.data);
    var html = '';
    var user_id = $("#user_id").val();
    html += '<div class="side-item '+data['id']+'" onclick="confirm_rate('+data['id']+')">';
      html += '<div class="product-thumb clearfix">';
        html += '<div class="image">';
            html += '<img src="'+data['author']['img']+'" width="50px" alt="'+data['author']['name']+'" title="'+data['author']['name']+'" class="img-responsive">';
          html += '</div>';
        html += '<div class="caption">';
          html += '<h4>'+data['author']['name']+'</h4>';
          html += '<p class="price">'+data['amount']+' грн.</p>';
        html += '</div>';
      html += '</div>';
    html += '</div>';
    if($('.'+data['id']+'').length != 0){
      var amount = ''+data['amount']+' грн.';
      $('.'+data['id']+'').children().children('.caption').children('.price').html(amount);
    }else{
      $("#column-right").append(html);
    }

  }
  product_socket.onclose = function(){}

  $('.close').on('click', function(){
    $('.modal').attr('style', 'display: none;')
  });

  function parts(){
    $('#parts').on('input', function(){

      var parent = $('#parts').parent();

      if($('#parts').val() == ''){
        parent.children('.alert-danger').remove();
        parent.append('<div class="alert alert-danger" role="alert">Будь-ласка кажіть кількість платежів</div>');
      }
      else{
        if(Number($('#parts').val()) > 12){
          parent.children('.alert-danger').remove();
          parent.append('<div class="alert alert-danger" role="alert">Максимальна кількість це - 12 платежів</div>');
        }
        else if(Number($('#parts').val()) < 2){
          parent.children('.alert-danger').remove();
          parent.append('<div class="alert alert-danger" role="alert">Мінімальна кількість це - 2 платежа</div>');
        }
        else{
          parent.children('.alert-danger').remove();
      }
      }
    });
  }

  $("#pay").on('click', function(){
    if($("#pay").prop('checked') == true){
      if($(".modal-body").children('.parts').length == 0){
        var html = '';
        html += '<div class="form-control parts">';
          html += '<input type="number" id="parts" name="parts" class="form-control" placeholder="Кількість платежів" min="2" max="12">';
        html += '</div>';
        $(".modal-body").append(html);
         parts()
      }
    }
    else{
      $('.modal-body').children('.parts').remove();
    }
  });

  $('#description').on('input', function(){
    var p_d = $('#description').parent();
      if ($('#description').val() == ''){
        if (p_d.children('.alert-danger').length == 0){
          p_d.append('<div class="alert alert-danger" role="alert">Будь-ласка введіть опис вашого договору</div>');
        }
      }
      else{
        if (p_d.children('.alert-danger').length > 0){
          p_d.children('.alert-danger').remove();
        }
      }
  });

  $("#price").on('input', function(){
    var p_a = $("#price").parent();
    if($("#price").val() == ''){

      if (p_a.children('.alert-danger').length == 0){
        p_a.append('<div class="alert alert-danger" role="alert">Будь-ласка назначте ціну</div>');
      }
    }
    else{
      if (p_a.children('.alert-danger').length > 0){
        p_a.children('.alert-danger').remove();
      }
    }
  });

}
