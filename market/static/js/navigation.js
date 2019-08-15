function about_product(link){
  $.ajax({
    method: 'GET',
    url: link,
    success: function(data){

      var data = JSON.parse(data['data']);
      var title = data['title'];

      window.history.pushState({'about-product': data}, title, link);
      var html = gen_product_html(data);
      $('#container').attr('style', 'display: none;');
      $('.middle').children().remove();
      $('.middle').append(html);

      product();
      $('html').animate({scrollTop: 0}, 200);
      $('#switch-mode').attr('style', 'display: none');
    }
  });
}
function gen_first_html(main, sub, und){
  var html = '<div id="container"><div id="nav-categories"><div class="container"><div class="row"><div class="categories-block">';
    html += '<div class="col">';
      html += '<select class="form-control form-control-sm" id="main-category">';
        html += '<option value="" selected="" disabled="" hidden="">Оберіть рубрику</option>';
        for(var i in categories){
          if(i == main){
            html += '<option selected value="'+i+'">'+i+'</option>';
          }else{
            html += '<option value="'+i+'">'+i+'</option>';
          }
        }
      html += '</select>';
    html += '</div>';
    html += '<div class="col">';
      html += '<select class="form-control form-control-sm" id="sub-category">';
        html += '<option value="" selected="" disabled="" hidden="">Оберіть категорію</option>';
        for(var i in categories[main]){
          if(i == sub){
            html += '<option selected value="'+i+'">'+i+'</option>';
          }else{
            html += '<option value="'+i+'">'+i+'</option>';
          }
        }
      html += '</select>';
      html += '</div>';
      if(und != false){
        html += '<div class="col und-category"><select onclick="fin_category(\''+main+'\', \''+sub+'\', this)" class="form-control form-control-sm">';
        for(var i in categories[main][sub]){
          if (i != 'sub-category'){
            if(i != und){
              html += '<option value="'+ i +'">'+i+'</option>';
            }
            else{
              html += '<option selected value="'+ i +'">'+i+'</option>';
            }
          }
        }
        html += '</select></div>';
      }
      html += '</div>';
    html += '<div class="option-block">';
    html += '<div>';
    return html;
}
function create_html_data(dict, check_dict, main, sub=false, und=false){
  var html = '';

    var counter = 0;
    var res = 0;

      for(var category in dict){
        if(counter == 3){
          counter = 0;
          html += '</div><div>'
        }

        if(category.search('brand-select') != -1){
          res += 1;
          html += '<select onclick="auto_model(this)" name="Марка brand-select" class="form-control form-control-sm">';
          html += '<option value="" selected="" disabled="" hidden="">Марка </option>';

          if(check_dict[category] != undefined){
            html += '<option selected value="'+check_dict[category]+'">'+check_dict[category]+'</option>';
          }
          for(var i in dict[category]){

            if(i != check_dict[category] && i != 'Марка'){
              html += '<option value="'+i+'">'+i+'</option>';
            }
          }
          html += '</select>';
          html += '<select name="Модель select" class="form-control form-control-sm auto-model">';
          html += '<option value="" selected="" disabled="" hidden="">Модель</option>';

          if(check_dict['Модель select'] != ''){
            html += '<option value="'+ check_dict['Модель select'] +'" selected>'+ check_dict['Модель select'] +'</option>';
          }
          for(var i in dict['Марка brand-select'][check_dict[category]]){
          var model = dict['Марка brand-select'][check_dict[category]][i];

            if(model != check_dict['Модель select']){
              html += '<option value="'+model+'">'+model+'</option>';
            }
          }
          html += '</select>';
        }
        else if(category.search('select') != -1 && category.search('Модель')){
          res += 1;
          var ctg = category.replace('select', '');

          html += '<select name="'+category+'" class="form-control form-control-sm">';
          html += '<option value="" selected disabled hidden>'+ctg+'</option>';
          if(check_dict[category] != undefined && check_dict[category] != ''){
            html += '<option selected value="'+check_dict[category]+'">'+check_dict[category].replace('select', '')+'</option>';
          }

          for(var i in dict[category]){
            var criteria = dict[category][i];
            if(criteria != check_dict[category]){
              html += '<option value="'+criteria+'">'+criteria+'</option>';
            }
          }
          html += '</select>';
        }
        else if(category.search('checkbox') != -1){
          res += 1;
          html += '<div class="checkbox-block form-control from-control-sm">';
          var cat_name = category.replace('checkbox', '');

          html += '<label onclick="open_block(this)" class="label-block"><p>'+cat_name+'</p><i class="fas fa-sort-down"></i></label>';
          html += '<div style="display: none" class="first-children">';

          var checked_array = [];
          for(var i in check_dict[category]){
            html += '<div class="checkbox-label">';
              html += '<input checked name="'+category+'/'+i+'" type="checkbox">';
              html += '<label>'+i+'</label>';
            html += '</div>'
            checked_array.push(i);
          }

          for(var i in dict[category]){
            var check = dict[category][i];
            if(check in checked_array){
              continue;
            }
            else{
              html += '<div class="checkbox-label">';
                html += '<input name="'+category+'/'+check+'" type="checkbox">';
                html += '<label>'+check+'</label>'
              html += '</div>'
            }

          }
          html += '</div></div>';
        }
        else if(category.search('number') != -1){
          res += 1;

          var cat = category.replace('number', '');
          html += '<div class="form-group">'
            html += '<input type="number" value="'+ check_dict[category+'-min'] +'" class="form-control form-control-sm" placeholder="'+cat.slice(0, cat.length-1)+'-від" name="'+category+'-min'+'">'
          html += '</div>';
          html += '<div class="form-group">';
            html += '<input type="number" value="'+ check_dict[category+'-max'] +'" class="form-control form-control-sm" placeholder="'+cat.slice(0, cat.length-1)+'-до" name="'+category+'-max'+'">'
          html += '</div>';
        }
        counter += 1;
      }
      html += '<div><div class="form-group"><input name="Ціна number-min" type="number" value="'+check_dict['Ціна number-min']+'" class="form-control form-control-sm" placeholder="Ціна-від"></div>';
      html += '<div class="form-group"><input name="Ціна number-max" type="number" value="'+check_dict['Ціна number-max']+'" class="form-control form-control-sm" placeholder="Ціна-до"></div>';
      html += '</div>';
      html += '</div></div>';


  if(res == 0 && sub != false){
    return undefined;
  }
  else{
    return html;
  }
}

function filter_state(data){
  var html = '';
  var products_html = '';

  var m = false;
  var s = false;
  var u = false;

  var dict = data['category-data'];
  var products = data['products-data'];

  for(var main in dict){
    var check_dict = dict[main];
    var default_dict = categories[main];
    m = main;

    for(var sub in dict[main]){
        try{
          check_dict = check_dict[sub];
          default_dict = default_dict[sub];
          s = sub;
          var result = create_html_data(default_dict, check_dict, main, sub);

          if (result == undefined){

              for(var und in check_dict){
                u = und;
                check_dict = check_dict[und];
                default_dict = default_dict[und];

                var result = create_html_data(default_dict, check_dict, main, sub, und);
            }
          }
        }
        catch{
            var result = create_html_data(categories[main], dict[main], main);
        }
    }
  }
  var first = gen_first_html(m, s, u);
  html += first;
  html += result;
  html += '<div class="container">';
  html += '<div class="col products">';
  for(var i in products){

    var title = products[i]['title'];
    var location = products[i]['location'];
    var category = products[i]['category'];
    var price = products[i]['price'];
    var images = products[i]['images'];
    var id = products[i]['id'];


    html += '<div class="col product" style="border-radius: 10px">';
      html += '<div class="image">';
        html += '<p onclick="about_product(\'/market/about_product/'+id+'/\')">';
          if(images.length == 0){
            html += '<img src="/static/no-product-found.jpg" alt="'+title+'" title="'+title+'" class="img-responsive" style="width: 125px;height: 125px">';
          }
          else{
            html += '<img src="'+images+'" alt="'+title+'" title="'+title+'" class="img-responsive" style="width: 125px;height: 125px">';
          }
          html += '<div class="name" style="word-wrap: break-word;">';
            html += '<h5>'+title+'</h5>';
          html += '</div>';
        html += '</p>';
      html += '</div>';
      html += '<div class="caption">';
        html += '<p class="price">';
          html += '<span class="saving">'+price+' грн.</span>';
        html += '</p>';
      html += '</div>';
    html += '</div>';
  }
  html += '</div></div>';
  html += '</div>';

  $('.middle').children().remove();
  $('.middle').append(html);

}

function about_state(data){
  var html = gen_product_html(data);
  $('.middle').children().remove();
  $('.middle').append(html);
  product();
}
function choose_mode(){
  var data = window.history.state;

  if(data != null || data != undefined){
    if(data['products']){
      filter_state(data['products']);
      filter_data();

      $('.middle').append((paginator(data['products']['paginator-data'])));
      $('#switch-mode').attr('style', 'display: block');
      var mode = '';

      if(data['products']['mode'] == 'seller'){
        mode = 'Я хочу купити';
      }else{
        mode = 'Я хочу продати'
      }

      $('#switch-mode').children('div').children('a').html(mode);
    }
    else if (data['about-product']) {
      about_state(data['about-product']);
      $('#switch-mode').attr('style', 'display: none');
    }
  }
  else{}
  nav_categories();
}
function page_state(){
  addEventListener("popstate",function(e){
    try{
      product_socket.close();
    }
    catch{}

    choose_mode();
  },false);
  choose_mode();
}
page_state();
function paginator(data){
  html = '';
  if(data['count-pages'] != 0){
    html += '<nav class="paginator" aria-label="Page navigation example">';
      html += '<ul class="pagination">';

        html += '<li class="page-item">';
          if(data['page-number'] > 1){
            html += '<a class="page-link" onclick="page('+(data['page-number']-1)+')" aria-label="Previous">';
          }
          else{
            html += '<a class="page-link disabled" aria-label="Previous">';
          }
            html += '<span aria-hidden="true">&laquo;</span>';
            html += '<span class="sr-only">Previous</span>';
        html += '  </a>';
        html += '</li>';

        for(var i = 1; i <= data['count-pages']; i++){
          if(i == data['page-number']){
            if(data['page-number']-3 > 0){
              html += '<li class="page-item"><a class="page-link" onclick="page(1)">1</a></li>';
              html += '<li class="page-item disabled">';
                html += '<a class="page-link disabled">---</a>';
              html += '</li>';
            }
            if(data['page-number']-2 > 0){
              html += '<li class="page-item"><a class="page-link" onclick="page('+(data['page-number']-2)+')">'+(data['page-number']-2)+'</a></li>';
            }
            if(data['page-number']-1 > 0){
              html += '<li class="page-item"><a class="page-link" onclick="page('+(data['page-number']-1)+')">'+(data['page-number']-1)+'</a></li>';
            }
            html += '<li class="active page-item"><a class="page-link" onclick="page('+(data['page-number'])+')">'+data['page-number']+'</a></li>';
            if(data['page-number']+1 <= data['count-pages']){
              html += '<li class="page-item"><a class="page-link" onclick="page('+(data['page-number']+1)+')">'+(data['page-number']+1)+'</a></li>';
            }
            if(data['page-number']+1 < data['count-pages']){
              html += '<li class="page-item disabled">';
                html += '<a class="page-link disabled">---</a>';
              html += '</li>';
              html += '<li class="page-item"><a class="page-link" onclick="page('+data['count-pages']+')">'+data['count-pages']+'</a></li>';
            }
          }
        }

        html += '<li class="page-item">';
        if(data['page-number'] < data['count-pages']){
          html += '<a class="page-link" onclick="page('+(data['page-number']+1)+')" aria-label="next">';
        }
        else{
          html += '<a class="page-link disabled" aria-label="next">';
        }
            html += '<span aria-hidden="true">&raquo;</span>';
            html += '<span class="sr-only">Next</span>';
          html += '</a>';
        html += '</li>';

      html += '</ul>';
    html += '</nav>';
  }
  return html;
}
  function auto_model(elem){
    var val = elem.value;
    var html = '<option value="" selected="" disabled="" hidden="">Модель</option>';
    for (var i in categories['Транспорт']['Легкові автомобілі']['Марка brand-select'][val]){
      var cat = categories['Транспорт']['Легкові автомобілі']['Марка brand-select'][val][i];
      html += '<option value="'+cat+'">'+cat+'</option>';
    }
    $('.auto-model').children().remove();
    $('.auto-model').append(html);
  }
  var pre_checked = undefined;
  function open_block(elem){
    var checkbox_array = [];

    var chl = elem.parentElement.children[1];
    if(pre_checked != elem){
      for(var i in document.getElementsByClassName('first-children')){
        var el = document.getElementsByClassName('first-children');
        try{
          el[i].setAttribute('style', 'display: none');
        }
        catch{
          continue;
        }
      }
    }
    if (chl.getAttribute('style') == 'display: none'){
      chl.setAttribute('style', 'display: block');
      pre_checked = elem;
    }else{
      chl.setAttribute('style', 'display: none');
      pre_checked = undefined;
    }
  }
  function page(page_number){
    preproces_data(page_number);
    window.scroll(0, 0);
  }
  function get_filter_criterias(){
    var inputs = document.getElementsByTagName('input');
    var select = document.getElementsByTagName('select');

    var create_data = {};

    for(var s in select){
      create_data[select[s].name] = select[s].value;
    }
    for(var i in inputs){
      if(inputs[i].type == 'checkbox'){
        var category = inputs[i].name.split('/');

        if(create_data[category[0]]){
          if(inputs[i].checked == true){
            create_data[category[0]][category[1]] = inputs[i].checked;
          }
        }else{
          if(inputs[i].checked == true){
            create_data[category[0]] = {};
            create_data[category[0]][category[1]] = inputs[i].checked;
          }
        }
      }else{
          var name = inputs[i].name;
          create_data[name] = inputs[i].value;
      }
    }

    delete create_data[''];
    delete create_data['email'];
    delete create_data['item'];
    delete create_data['namedItem'];
    delete create_data['undefined'];

    var main_category = $('#main-category').val();
    var sub_category = $('#sub-category').val();
    var und_category = $('.und-category').children('select').val();

    var data = {};

    if(sub_category == undefined){
      data[main_category] = create_data;
    }
    else if(und_category == undefined){
      data[main_category] = {};
      data[main_category][sub_category] = create_data;
    }else{
      data[main_category] = {};
      data[main_category][sub_category] = {};
      data[main_category][sub_category][und_category] = create_data;
    }
    return data;
  }
  function gen_html(data){
    var html = '';
    for(var i in data){
      var title = data[i]['title'];
      var location = data[i]['location'];
      var category = data[i]['category'];
      var price = data[i]['price'];
      var images = data[i]['images'];
      var id = data[i]['id'];

      html += '<div class="col product" style="border-radius: 10px">';
        html += '<div class="image">';
          html += '<p onclick="about_product(\'/market/about_product/'+id+'/\')">';
            if(images.length == 0){
              html += '<img src="/static/no-product-found.jpg" alt="'+title+'" title="'+title+'" class="img-responsive" style="width: 125px;height: 125px">';
            }
            else{
              html += '<img src="'+images+'" alt="'+title+'" title="'+title+'" class="img-responsive" style="width: 125px;height: 125px">';
            }
            html += '<div class="name" style="word-wrap: break-word;">';
              html += '<h5>'+title+'</h5>';
            html += '</div>';
          html += '</p>';
        html += '</div>';
        html += '<div class="caption">';
          html += '<p class="price">';
            html += '<span class="saving">'+price+' грн.</span>';
          html += '</p>';
        html += '</div>';
      html += '</div>';
    }
    return html;
  }
  function preproces_data(page=1){
    var mode = $('#switch-mode').children('div').children('a').html();
    if(mode == 'Я хочу продати'){
      mode = 'customer';
    }else if (mode == 'Я хочу купити') {
      mode = 'seller';
    }
    var categories = get_filter_criterias();
    $.ajax({
      url: '/market/products/',
      method: 'GET',
      data: {
        'data': JSON.stringify(categories),
        'mode': mode,
        'page': page
      },
      success: function(data){
        var state = {'category-data': categories, 'products-data': JSON.parse(data['products']), 'mode': mode, 'paginator-data': data['paginator-data']};
        window.history.replaceState({'products': state}, 'HopePay', '/market/products/');
        var html = gen_html(JSON.parse(data['products']));
        $('.products').children().remove();
        $('.products').append(html);
        $('.middle').children('.paginator').remove();

        $('.middle').append((paginator(data['paginator-data'])));
      }
    });
  }
  var last_value = undefined;
  function filter_data(){
    $('input').on('change', function(){
      if($(this).val() != last_value){
        preproces_data();
      }
      last_value = $(this).val();
    });
    $('select').on('change', function(){
      if($(this).val() != last_value){
        preproces_data();
      }
      last_value = $(this).val();
    });
  }

  function fin_category(main, sub, und=false){
    var html = '<div>';
    counter = 0;
    if(und == false){
      for(var category in categories[main][sub]){
        if(counter == 3){
          counter = 0;
          html += '</div><div>'
        }
        if(category.search('brand-select') != -1){
          html += '<select onclick="auto_model(this)" name="Марка brand-select" class="form-control form-control-sm">';
          for(var i in categories[main][sub][category]){;
            if(i == 0){
              html += '<option value="" selected="" disabled="" hidden="">Марка </option>';
            }
            html += '<option value="'+i+'">'+i+'</option>';
          }
          html += '</select>';
          html += '<select name="Модель select" class="form-control form-control-sm auto-model">';
          html += '<option value="" selected="" disabled="" hidden="">Модель</option>';
          html += '</select>';
        }
        else if(category.search('select') != -1 && category.search('Модель')){
          html += '<select name="'+category+'" class="form-control form-control-sm">';
          for(var i in categories[main][sub][category]){
            var cat = categories[main][sub][category][i];
            if(i == 0){
              html += '<option value="" selected disabled hidden>'+category.replace('select', '')+'</option>';
            }
            html += '<option value="'+cat+'">'+cat+'</option>';
          }
          html += '</select>';
        }
        else if(category.search('checkbox') != -1){
          html += '<div class="checkbox-block form-control from-control-sm">';
          var cat_name = category.replace('checkbox', '');
          html += '<label onclick="open_block(this)" class="label-block"><p>'+cat_name+'</p><i class="fas fa-sort-down"></i></label>';
          html += '<div style="display: none" class="first-children">';
          for(var i in categories[main][sub][category]){
            var check = categories[main][sub][category][i];
            html += '<div class="checkbox-label">';
              html += '<input name="'+category+'/'+check+'" type="checkbox">';
              html += '<label>'+check+'</label>'
            html += '</div>'
          }
          html += '</div></div>';
        }
        else if(category.search('number') != -1){
          html += '<div class="form-group">'
            html += '<input type="number" class="form-control form-control-sm" placeholder="'+category.replace('number', '')+'-від" name="'+category+'-min">'
          html += '</div>';
          html += '<div class="form-group">';
            html += '<input type="number" class="form-control form-control-sm" placeholder="'+category.replace('number', '')+'-до" name="'+category+'-max">'
          html += '</div>';
        }
        counter += 1;
      }
    }else{
      for(var category in categories[main][sub][und.value]){
        if(counter == 3){
          counter = 0;
          html += '</div><div>'
        }

        if(category.search('select') != -1){
          html += '<select class="form-control form-control-sm">';
          for(var i in categories[main][sub][und.value][category]){
            var cat = categories[main][sub][und.value][category];
            if(i == 0){
              html += '<option value="" selected disabled hidden>'+category.replace('select', '')+'</option>';
            }
            html += '<option value="'+cat[i]+'">'+cat[i]+'</option>'
          }
          html += '</select>';
        }
        else if(category.search('checkbox') != -1){
          var cat_name = category.replace('checkbox', '');
          cat_name = cat_name.replace('(до 500 метрів)', '');
          html += '<div class="checkbox-block form-control from-control-sm">';
          html += '<label onclick="open_block(this)" class="label-block"><p>'+cat_name+'</p><i class="fas fa-sort-down"></i></label>';
          html += '<div style="display: none" class="first-children">';
          for(var i in categories[main][sub][und.value][category]){
            var check = categories[main][sub][und.value][category][i];
            html += '<div class="checkbox-label">';
              html += '<input name="'+category+'/'+check+'" type="checkbox">';
              html += '<label>'+check+'</label>'
            html += '</div>'
          }
          html += '</div></div>';
        }
        else if(category.search('number') != -1){
          html += '<div class="form-group">'
            html += '<input type="number" class="form-control form-control-sm" placeholder="'+category.replace('number', '')+'-від" name="'+category+'-min">'
          html += '</div>';
          html += '<div class="form-group">';
            html += '<input type="number" class="form-control form-control-sm" placeholder="'+category.replace('number', '')+'-до" name="'+category+'-max">'
          html += '</div>';
        }
        counter += 1;
      }

    }
    html += '<div><div class="form-group"><input name="Ціна number-min" type="number" class="form-control form-control-sm" placeholder="Ціна-від"></div>';
    html += '<div class="form-group"><input name="Ціна number-max" type="number" class="form-control form-control-sm" placeholder="Ціна-до"></div>';
    html += '</div>';
    $('.option-block').children().remove();
    $('.option-block').append(html);
    filter_data();

  }
  function sub_category(){
    $("#sub-category").on('click', function(){
      var category = categories[$('#main-category').val()][$('#sub-category').val()];
      if(category == undefined){
        var category = categories[$('#main-category').val()]
      }

      if (category['sub-category']){
        var html = '<div class="col und-category"><select onclick="fin_category(\''+$('#main-category').val()+'\', \''+$('#sub-category').val()+'\', this)" class="form-control form-control-sm">'

        for(var i in categories[$('#main-category').val()][$('#sub-category').val()]){
          if (i != 'sub-category'){
            html += '<option value="'+ i +'">'+i+'</option>';
          }
        }
        html += '</select></div>';

        $('.categories-block').children('.und-category').remove();
        $('.option-block').children().remove();
        $('.categories-block').append(html);
      }
      else{
        $('.categories-block').children('.und-category').remove();
        $('.option-block').children().remove();
        fin_category($('#main-category').val(), $('#sub-category').val());
      }
    });
  }
  function nav_categories(){
    $("#main-category").on('click', function(){
      $('.categories-block').children('.und-category').remove();
      $('.option-block').children().remove();
      try{
        var category = categories[$('#main-category').val()][$('#sub-category').val()];
      }
      catch{
        var category = categories[$('#main-category').val()];
      }


      var html = '<option value="" selected="" disabled="" hidden="">Оберіть категорію</option>';
      for(var i in categories[$('#main-category').val()]){
        html += '<option value="'+ i +'">'+ i +'</option>';
      }
      $('#sub-category').children().remove();
      $('#sub-category').append(html);

      sub_category();
    });
  }
  nav_categories();
  sub_category();
  filter_data();
