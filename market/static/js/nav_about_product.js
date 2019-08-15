$.ajax({
  method: 'GET',
  url: window.location.href,
  success: function(data){

    var data = JSON.parse(data['data']);
    var title = data['title'];

    var html = gen_product_html(data);
    $('#container').attr('style', 'display: none;');
    $('.middle').children().remove();
    $('.middle').append(html);

    product();
    $('html').animate({scrollTop: 0}, 200);
    $('#switch-mode').attr('style', 'display: none');
  }
});
