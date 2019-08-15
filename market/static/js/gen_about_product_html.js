function gen_product_html(data){

  var title = data['title'];
  var price = data['price'];
  var description = data['description'];
  var json_data = data['json-data'];
  var location = data['location'];
  var images = data['images'];

  var html = '';

  html += '<div id="container about-product">';
    html += '<div class="container">';

      html += '<div class="modal" tabindex="-1" role="dialog">';
        html += '<div class="modal-dialog" role="document">';
          html += '<div class="modal-content">';
            html += '<div class="modal-header">';
              html += '<h5 class="modal-title">Запропонуйте свої умови</h5>';
              html += '<button type="button" class="close" data-dismiss="modal" aria-label="Close">';
                html += '<span aria-hidden="true">&times;</span>';
              html += '</button>';
            html += '</div>';
            html += '<div class="modal-body">';
              html += '<div class="form-group">';
                  html += '<input type="number" id="price" name="Ціна" class="form-control" placeholder="Ціна *" value=""/>';
              html += '</div>';
              html += '<div class="form-group">';
                html += '<label>Опис *</label>';
                html += '<textarea id="description" style="resize: none;" name="Опис" class="form-control" rows="4" cols="40"></textarea>';
              html += '</div>';
              html += '<div class="form-group">';
                html += '<input id="pay" type="checkbox" name="pay-parts">';
                html += '<label for="scales">Натиніть якщо ви хочете купити товар в рострочку</label>';
              html += '</div>';

            html += '</div>';

            html += '<div class="modal-footer">';
              html += '<button type="button" id="send-rate" class="btn btn-primary">Запропонувати</button>';
          html += '  </div>';
          html += '</div>';
        html += '</div>';
  html += '</div>';

      html += '<div class="row">';

        html += '<div id="content" class="col-sm-9">';
          html += '<div itemscope="" itemtype="http://schema.org/Product">';
            html += '<h1 class="title" itemprop="name">'+title+'</h1>';
            html += '<div class="row product-info">';
              html += '<div class="col-sm-6">';
                html += '<div class="image"><div style="height:350px;width:350px;" class="zoomWrapper">';
                  if(images[0] != undefined){
                    html += '<img class="img-responsive" itemprop="image" id="zoom_01" src="'+images[0]+'" title="'+title+'" alt="'+title+'" data-zoom-image="'+images[0]+'" style="width: 350px; height: 350px; position: relative"></div>';
                  }
                  else{
                    html += '<img class="img-responsive" itemprop="image" id="zoom_01" src="/static/no-product-found.jpg" title="'+title+'" alt="'+title+'" data-zoom-image="/static/no-product-found.jpg" style="width: 350px; height: 350px; position: relative"></div>';
                  }
                html += '</div>';
                html += '<div class="image-additional" id="gallery_01">';
                for(var img in images){
                  var image = images[img];

                  html += '<a class="thumbnail" href="#" data-zoom-image="'+image+'" data-image="'+image+'" title="'+title+'">';
                    html += '<img src="'+image+'" title="'+title+'" alt="'+title+'">';
                  html += '</a>';
                }

                html += '</div>';
              html += '</div>';

              html += '<div style="margin-left: 30px;" class="col-sm-5">';
              html += '  <ul class="list-unstyled description">';
              for(var ctg in json_data){
                if(ctg.search('select') != -1){
                  var category = ctg.replace('select', '');
                  category = category.replace('brand-', '');
                  html += '<li><b>'+category+': </b> <a href="#"><span itemprop="brand">'+json_data[ctg]+'</span></a></li>';
                }
                else if (ctg.search('checkbox') != -1){
                  html += '<li><b>'+ctg.replace('checkbox', '')+': </b>';
                  var counter = 0;
                  var length = 0;
                  for(var i in json_data[ctg]){
                    length += 1;
                  }
                  for(var i in json_data[ctg]){
                    counter += 1;

                    if(counter == length){
                      html += '<a href="#"><span itemprop="brand">'+i+'</span></a>';
                    }
                    else{
                      html += '<a href="#"><span itemprop="brand">'+i+', </span></a>';
                    }

                  }
                  html += '</li>'
                }
              }
              html += '  </ul>';
              html += '  <ul class="price-box">';
              html += '    <li class="price" itemprop="offers" itemscope="" itemtype="http://schema.org/Offer"><span itemprop="price">'+price+' грн.</span></li>';
              html += '  </ul>';
              html += '  <div id="product">';
              html += '    <div class="cart">';
                  html += '  <div>';
                      html += '<button type="button" id="rate" class="btn btn-primary btn-lg">Запропонувати свої умови</button>';
                    html += '</div>';
                  html += '</div>';
                html += '</div>';
            html += '  </div>';
            html += '</div>';
            html += '<ul class="nav nav-tabs">';
              html += '<li class="active"><a href="#tab-description" data-toggle="tab" aria-expanded="true">Опис</a></li>';
            html += '</ul>';
          html += '  <div class="tab-content">';
              html += '<div itemprop="description" id="tab-description" class="tab-pane active">';
              html += '  <div>';
              html += '<p>'+description+'</p>'
              html += '  </div>';
            html += '  </div>';
            html += '</div>';
        html += '  </div>';
      html += '  </div>';
      try{
        if(data['rates'].length > 0){
          html += '<aside id="column-right" style="max-width: 75%;flex: 73%" class="col-sm-3 hidden-xs">';
            html += '<h3 class="subtitle">Ставки</h3>';
            for(var rate in data['rates']){
              var data_rate = data['rates'][rate];

              html += '<div class="side-item '+data_rate['id']+'" onclick="confirm_rate('+data_rate['id']+')">';
                html += '<div class="product-thumb clearfix">';
                  html += '<div class="image">';
                      html += '<img src="'+data_rate['author-photo']+'" width="50px" alt="'+data_rate['author-name']+'" title="'+data_rate['author-name']+'" class="img-responsive">';
                    html += '</div>';
                  html += '<div class="caption">';
                    html += '<h4>'+data_rate['author-name']+'</h4>';
                    html += '<p class="price">'+data_rate['amount']+' грн.</p>';
                    if(data['parts'] != undefined){
                      html += '<p class="installments_count">Кількість платежів: '+data['parts']+'</p>';
                    }
                  html += '</div>';
                html += '</div>';
              html += '</div>';
            }
          html += '</aside>';
        }
      }
      catch{
        html += '';
      }
      var seller = data['like_products_seller'];
      var customer = data['like_products_customer'];

      html += '<aside id="column-right" style="max-width: 75%;flex: 73%" class="col-sm-3 hidden-xs">';
      if(customer.length != 0){
        html += '<h3 class="subtitle">Автор хоче купити</h3>';
        html += '<div class="side-item">';
        for(var i in customer){
          html += '<div class="product-thumb clearfix">';
          var image = '/static/no-product-found.jpg';
            if(i['image']){
              image = customer[i]['image'];
            }
            var link = '/market/about_product/'+customer[i]['id']+'/';
            html += '<div class="image"><a onclick="about_product(\''+link+'\')"><img width="50px" height="50px" src="'+image+'" alt="'+customer[i]['title']+'" title="'+customer[i]['title']+'" class="img-responsive"></a></div>';
            html += '<div class="caption">';
              html += '<h4><a onclick="about_product(\''+link+'\')">'+customer[i]['title']+'</a></h4>';
              html += '<p class="price">'+customer[i]['price']+' грн.</p>';
              try{
                var parts = Number(customer[i]['parts']);
                html += '<p>Кількість платежів: '+parts+'</p>';
              }
              catch{

              }
            html += '</div>';
          html += '</div>';
        }
        html += '</div>';
      }
      if(seller.length != 0){
        html += '<h3 class="subtitle">Автор хоче продати</h3>';
        html += '<div class="side-item">';
        for(var i in seller){
          html += '<div class="product-thumb clearfix">';
          var image = '/static/no-product-found.jpg';
            if(i['image']){
              image = seller[i]['image'];
            }
            var link = '/market/about_product/'+seller[i]['id']+'/';
            html += '<div class="image"><a onclick="about_product(\''+link+'\')"><img width="50px" height="50px" src="'+image+'" alt="'+seller[i]['title']+'" title="'+seller[i]['title']+'" class="img-responsive"></a></div>';
            html += '<div class="caption">';
              html += '<h4><a onclick="about_product(\''+link+'\')">'+seller[i]['title']+'</a></h4>';
              html += '<p class="price">'+seller[i]['price']+' грн.</p>';
              try{
                var parts = Number(seller[i]['parts']);
                html += '<p>Кількість платежів: '+parts+'</p>';
              }
              catch{

              }
            html += '</div>';
          html += '</div>';
        }
        html += '</div>';
      }

      html += '</aside>';
    html += '  </div>';
    html += '</div>';
    html += '</div>';
return html;
}
