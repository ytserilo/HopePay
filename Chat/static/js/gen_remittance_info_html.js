
function modal_info(remittance){
  var card_number = $("#card_number").val();
  var phone_number = $("#phone_number").val();
  var user_id = Number($("#user_id").val());
  html = '';
  if(remittance['fin_remittance']){
    if(remittance['fin_remittance'] != 'None' && remittance['fin_remittance'] != undefined && remittance['fin_remittance']['count_of_paid_parts'] == null){

        html += '<div class="modal fade" id="confirm-modal" tabindex="-1" role="dialog">';
        html += '<div class="modal-dialog" role="document">';
          html += '<div class="modal-content">';
            html += '<div class="modal-header">';
              html += '<h5 class="modal-title">Перевірте чи дійсно на цей товар ви очікували</h5>';
              html += '<button type="button" onclick="close_confirm_modal()" class="close" data-dismiss="modal" aria-label="Close">';
                html += '<span aria-hidden="true">&times;</span>';
              html += '</button>';
            html += '</div>';
            if(remittance['fin_remittance']['postal_transfer'] == true){
              html += '<div class="modal-body">';
                html += '<a target="_blank" href="https://novaposhta.ua/tracking/?cargo_number='+ remittance['fin_remittance']['postal_code'] +'&newtracking=1">Натисніть сюди</a>';
                html += '<p>Якщо в відправленні якась помилка можете відміняти платіж</p>';
              html += '</div>';
            }
            html += '<div class="modal-footer">';
              html += '<p>Якщо ви натиснете підтвердити то продавець отримає гроші і ви більше не зможете відмінити платіж</p>';
              html += '<button type="button" onclick="confirm()" class="btn btn-primary">Підтвердити</button>';
            html += '</div>';
          html += '</div>';
        html += '</div>';
    html += '</div>';
    }
    console.log(remittance)
    if(remittance['fin_remittance']['count_of_paid_parts'] > 0 && remittance['fin_remittance']['seller_id'] != user_id){
      html += '<div class="modal fade" id="confirm-modal" tabindex="-1" role="dialog">';
      html += '<div class="modal-dialog" role="document">';
        html += '<div class="modal-content">';
          html += '<div class="modal-header">';
            html += '<h5 class="modal-title">Тут ви можете замінити картку для рострочки або змінити ціну</h5>';
            html += '<button type="button" onclick="close_confirm_modal()" class="close" data-dismiss="modal" aria-label="Close">';
              html += '<span aria-hidden="true">&times;</span>';
            html += '</button>';
          html += '</div>';

            html += '<div class="modal-body">';
              html += '<div class="input-group mb-3">';
                html += '<input type="text" value="'+ phone_number +'" maxlength="10" id="smash_phone" class="form-control" placeholder="Ваш номер мобільного" aria-label="Ваш номер мобільного" aria-describedby="basic-addon1">';
              html += '</div>';
              html += '<div class="input-group mb-3">';
                html += '<input type="text" value="'+ card_number +'" maxlength="16" id="smash_card" class="form-control" placeholder="Ваш номер картки" aria-label="Ваш номер картки" aria-describedby="basic-addon1">';
              html += '</div>';
              html += '<div class="input-group mb-3">';
                html += '<input type="text" maxlength="2" id="smash_card_exp_month" class="form-control" placeholder="MM" aria-label="MM" aria-describedby="basic-addon1">';
                html += '<input type="text" maxlength="2" id="smash_card_exp_year" class="form-control" placeholder="YY" aria-label="YY" aria-describedby="basic-addon1">';
                html += '<input type="password" maxlength="3" id="smash_card_cvv" class="form-control" placeholder="CVV" aria-label="CVV" aria-describedby="basic-addon1">';
              html += '</div>';

              html += '<div class="input-group mb-3">';
              html += '<label>Оберіть зручну для вас форму розстрочки</label>'
                html += '<div class="form-group">'
                html += '<select class="form-control" id="smash">';
                  var price_to_one_part = Math.ceil(remittance['fin_remittance']['amount'] / remittance['fin_remittance']['installments_count']);
                  price_to_one_part *= remittance['fin_remittance']['count_of_paid_parts'];

                  for(var i = 1; i <= 12 - remittance['fin_remittance']['count_of_paid_parts']-1; i++){
                      html += '<option>'+Math.ceil((remittance['fin_remittance']['amount'] - price_to_one_part) / i)+'грн. на '+i+' місяців</option>'
                  }
                html += '</select>';
                html += '</div>';
              html += '</div>';

            html += '</div>';
          html += '<div class="modal-footer">';
            html += '<button type="button" onclick="send_smash()" class="btn btn-primary">Змінити</button>';

          html += '</div>';
        html += '</div>';
      html += '</div>';
  html += '</div>';
  }
}


  html += '<div class="modal" style="display: block;background-color: rgba(0, 0, 0, 0.5);" id="remittance_settings" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">';
    html += '<div class="modal-dialog" role="document">';
      html += '<div class="modal-content">';
        html += '<div class="modal-header">';
          if(remittance['fin_remittance'] != 'None' && remittance['fin_remittance'] != undefined){
            html += '<h5 class="modal-title" id="exampleModalLabel">Умови договору</h5>';
          }
          else if (remittance['other_remittance'] == 'None') {
            html += '<h5 class="modal-title" id="exampleModalLabel">Ваші умови договору</h5>';
          }
          else{
            html += '<h5 class="modal-title" id="exampleModalLabel">Ваші умови договору та запропоновані</h5>';
          }
          html += '<button type="button" onclick="close_modal_remittance()" class="close" data-dismiss="modal" aria-label="Close">';
            html += '<span aria-hidden="true">×</span>';
          html += '</button>';
        html += '</div>';
        html += '<div class="modal-body" id="modal_body">';
          html += '<div class="input-group mb-3">';
            if(remittance['fin_remittance'] != 'None' && remittance['fin_remittance'] != undefined){
              html += '<div class="alert" role="alert">';

                html += '<p id="fin_description">Опис: '+ remittance['fin_remittance']['description'] +'</p>';
                html += '<p id="fin_price">Ціна: '+ remittance['fin_remittance']['amount'] +'</p>';
                html += '<p id="fin_currency">Валюта: '+ remittance['fin_remittance']['currency'] +'</p>';
                html += '<p id="fin_postal">Чи э почтовим переказом: ';
                if(remittance['fin_remittance']['postal_transfer'] == true){
                    html += '<i class="fa fa-check-circle"></i></p>';
                }
                else{
                    html += '<i class="fa fa-ban"></i></p>';
                }
                if(remittance['fin_remittance']['payment_by_installments'] == true && remittance['fin_remittance']['count_of_paid_parts'] == null){
                  html += '<p>Кількість платежів: '+ remittance['fin_remittance']['installments_count'] +'</p>';
                  html += '<p>Сума місячного платежу: '+ Math.ceil(remittance['fin_remittance']['amount'] / remittance['fin_remittance']['installments_count']) +'</p>';
                }
                if(remittance['fin_remittance']['payment_by_installments'] == true && remittance['fin_remittance']['count_of_paid_parts'] != null){
                  html += '<p>Кількість платежів: '+ remittance['fin_remittance']['installments_count'] +'</p>';
                  html += '<p>Сума місячного платежу: '+ Math.ceil(remittance['fin_remittance']['amount'] / remittance['fin_remittance']['installments_count']) +'</p>';
                  html += '<p>Кількість оплачених платежів '+remittance['fin_remittance']['count_of_paid_parts']+'/'+remittance['fin_remittance']['installments_count']+'</p>';
                }

                html += '<hr>';
                if(remittance['fin_remittance']['paid'] == true){
                  html += '<p class="pay-status">Статус оплати: Оплачено</p>';
                }else{
                  if(remittance['fin_remittance']['seller_id'] != user_id){
                    html += '<p class="pay-status">Статус оплати: потребується оплата </p>';

                    html += '<div id="modal-status">';
                      html += '<div class="input-group mb-3">';
                        html += '<input type="text" value="'+ phone_number +'" maxlength="10" id="phone" class="form-control" placeholder="Ваш номер мобільного" aria-label="Ваш номер мобільного" aria-describedby="basic-addon1">';
                      html += '</div>';
                      html += '<div class="input-group mb-3">';
                        html += '<input type="text" value="'+ card_number +'" maxlength="16" id="card" class="form-control" placeholder="Ваш номер картки" aria-label="Ваш номер картки" aria-describedby="basic-addon1">';
                      html += '</div>';
                      html += '<div class="input-group mb-3">';
                        html += '<input type="text" maxlength="2" id="card_exp_month" class="form-control" placeholder="MM" aria-label="MM" aria-describedby="basic-addon1">';
                        html += '<input type="text" maxlength="2" id="card_exp_year" class="form-control" placeholder="YY" aria-label="YY" aria-describedby="basic-addon1">';
                        html += '<input type="password" maxlength="3" id="card_cvv" class="form-control" placeholder="CVV" aria-label="CVV" aria-describedby="basic-addon1">';
                      html += '</div>';
                      html += '<button onclick="pay()" class="btn btn-primary">Оплатити</button>';
                    html += '</div>';

                  }
                  else{
                    html += '<p class="pay-status">Статус оплати: потребується оплата</p>';
                  }
                }
                if(remittance['fin_remittance']['shipped'] == true){
                  if(remittance['fin_remittance']['postal_transfer'] == true){
                    html += '<a target="_blank" href="https://novaposhta.ua/tracking/?cargo_number='+ remittance['fin_remittance']['postal_code'] +'&newtracking=1">Натисніть щоб відстежети посилку</a>';
                  }

                  html += '<p class="shipped-status">Статус відправлення: товар чи послуга була відправленна</p>';
                }
                else{
                  if(user_id == remittance['fin_remittance']['seller_id']){
                    html += '<p class="modal-status">Статус відправлення: товар чи послуга потребує відправки </p>';
                    if(remittance['fin_remittance']['postal_transfer'] == true){
                      html += '<div id="postal-modal">';
                        html += '<div class="input-group mb-3">';
                            html += '<input type="text" id="postal_code" class="form-control" placeholder="Номер накладної" aria-label="Номер накладної" aria-describedby="basic-addon1">';
                        html += '</div>';
                        html += '<div class="input-group mb-3">';
                            html += '<input type="text" id="phone_number" class="form-control" placeholder="Ваш мобільний телефон" aria-label="Ваш мобільний телефон" aria-describedby="basic-addon1">';
                        html += '</div>';
                        html += '<button onclick="send()" class="btn btn-primary">Відправити</button>';
                      html += '</div>';
                    }
                    else{
                      html += '<div id="postal-modal">';
                          html += '<button onclick="send()" class="btn btn-primary">Відправити</button>';
                      html += '</div>';
                    }
                  }
                  else{
                    if(remittance['fin_remittance']['paid'] == true){
                      html += '<div id="postal-modal">';
                        html += '<p>Статус відправлення: товар чи послуга не відпраленна очікуйте дій продавця</p>';
                      html += '</div>';
                    }
                    else{
                      html += '<div id="postal-modal">';
                        html += '<p>Статус відправлення: товар чи послуга не відпраленна по причині не оплати</p>';
                      html += '</div>';
                    }
                  }
                }

              html += '</div>';
            }
            else{
              if(remittance['self_remittance'] != 'None' && remittance['other_remittance'] == 'None'){
                  html += '<div class="alert" role="alert">';
                    html += '<h1>Ваш варіант договору</h1>';
                    html += '<p id="self_description">Опис: '+ remittance['self_remittance']['description'] +'</p>';
                    html += '<p id="self_price">Ціна: '+ remittance['self_remittance']['amount'] +'</p>';
                    html += '<p id="self_currency">Валюта: '+ remittance['self_remittance']['currency'] +'</p>';
                    html += '<p id="self_postal">Чи э почтовим переказом: ';
                    if(remittance['self_remittance']['postal_transfer'] == true){
                        html += '<i class="fa fa-check-circle"></i></p>';
                    }
                    else{
                        html += '<i class="fa fa-ban"></i></p>';
                    }
                    if(remittance['self_remittance']['payment_by_installments'] == true){
                      html += '<p>Кількість платежів: '+ remittance['self_remittance']['installments_count'] +'</p>';
                      html += '<p>Сума місячного платежу: '+ Math.ceil(remittance['self_remittance']['amount'] / remittance['self_remittance']['installments_count']) +'</p>';
                    }
                  html += '</div>';

                  html += '<div class="alert" role="alert">';
                    html += '<p>Ваш варіант договору ще не підтверджений очікуйте на дії партнера</p>';
                  html += '</div>';
                  html += '<div id="modal-status"></div>';


              }
              else if(remittance['self_remittance'] == 'None' && remittance['other_remittance'] != 'None'){
                var changes_id = remittance['other_remittance']['changes_id'];

                html += '<div class="alert" role="alert">';
                  html += '<p id="other_description">Опис: '+ remittance['other_remittance']['description'] +'</p>';
                  html += '<p id="other_price">Ціна: '+ remittance['other_remittance']['amount'] +'</p>';
                  html += '<p id="other_currency">Валюта: '+ remittance['other_remittance']['currency'] +'</p>';
                  html += '<p id="other_postal">Чи э почтовим переказом: ';
                  if(remittance['other_remittance']['postal_transfer'] == true){
                      html += '<i class="fa fa-check-circle"></i></p>';
                  }
                  else{
                      html += '<i class="fa fa-ban"></i></p>';
                  }
                  if(remittance['other_remittance']['payment_by_installments'] == true){
                    html += '<p>Кількість платежів: '+ remittance['other_remittance']['installments_count'] +'</p>';
                    html += '<p>Сума місячного платежу: '+ Math.ceil(remittance['other_remittance']['amount'] / remittance['other_remittance']['installments_count']) +'</p>';
                  }
                  html += '<div id="modal-status"></div>';
                  html +=  '<button onclick="accept_confirmation({})" class="btn btn-primary" style="background-color: #435f7a;">Підтвердити умови договору</button>'.replace('{}', changes_id);
                html += '</div>';
              }
              else if(remittance['self_remittance'] != 'None' && remittance['other_remittance'] != 'None'){
                var changes_id = remittance['other_remittance']['changes_id'];

                html += '<div class="alert" role="alert">';
                  html += '<h3>Ваш договір</h3>';
                  html += '<p id="self_description">Опис: '+ remittance['self_remittance']['description'] +'</p>';
                  html += '<p id="self_price">Ціна: '+ remittance['self_remittance']['amount'] +'</p>';
                  html += '<p id="self_currency">Валюта: '+ remittance['self_remittance']['currency'] +'</p>';
                  html += '<p id="self_postal">Чи э почтовим переказом: ';
                  if(remittance['self_remittance']['postal_transfer'] == true){
                      html += '<i class="fa fa-check-circle"></i></p>';
                  }
                  else{
                      html += '<i class="fa fa-ban"></i></p>';
                  }
                  if(remittance['self_remittance']['payment_by_installments'] == true){
                    html += '<p>Кількість платежів: '+ remittance['self_remittance']['installments_count'] +'</p>';
                    html += '<p>Сума місячного платежу: '+ Math.ceil(remittance['self_remittance']['amount'] / remittance['self_remittance']['installments_count']) +'</p>';
                  }
                html += '</div>';
                html += '<div class="alert" role="alert">';
                  html += '<p id="other_description">Опис: '+ remittance['other_remittance']['description'] +'</p>';
                  html += '<p id="other_price">Ціна: '+ remittance['other_remittance']['amount'] +'</p>';
                  html += '<p id="other_currency">Валюта: '+ remittance['other_remittance']['currency'] +'</p>';
                  html += '<p id="other_postal">Чи э почтовим переказом: ';
                  if(remittance['other_remittance']['postal_transfer'] == true){
                      html += '<i class="fa fa-check-circle"></i></p>';
                  }
                  else{
                      html += '<i class="fa fa-ban"></i></p>';
                  }
                  if(remittance['other_remittance']['payment_by_installments'] == true){
                    html += '<p>Кількість платежів: '+ remittance['other_remittance']['installments_count'] +'</p>';
                    html += '<p>Сума місячного платежу: '+ Math.ceil(remittance['other_remittance']['amount'] / remittance['other_remittance']['installments_count']) +'</p>';
                  }
                  html +=  '<button onclick="accept_confirmation({})" class="btn btn-primary" style="background-color: #435f7a;">Підтвердити умови договору</button>'.replace('{}', changes_id);
                  html += '<div id="modal-status"></div>';
                html += '</div>';
              }
            }
          html += '</div>';
              html += '<div class="input-group mb-3">';
              if(remittance['fin_remittance']){
                if(remittance['fin_remittance']['seller_id'] == user_id){
                  html += '<button type="button" onclick="confirm()" class="btn btn-success" style="width: 50%;">Підтвердити</button>'
                }else{
                  html += '<button type="button" onclick="open_confirm()" class="btn btn-success" style="width: 50%;">Підтвердити</button>'
                }

              }else{
                html += '<button type="button" onclick="confirm()" class="btn btn-success" style="width: 50%;">Підтвердити</button>';
              }
          html += '<button type="button" onclick="cencell()" class="btn btn-danger" style="width: 50%;">Відмінити</button></div>';
        html += '</div>';
    html += '</div>';
  html += '</div>';
  html += '</div>';
  return html;
}
function close_modal_remittance(){
    $("#remittance_settings").remove()
};
function open_confirm(){
  $("#confirm-modal").css({'display': 'block', 'z-index': '9999999', 'background-color': 'rgba(0, 0, 0, 0.5)'});
  $("#confirm-modal").attr('class', 'modal');
}
function close_confirm_modal(){
  $("#confirm-modal").css({'display': 'none', 'z-index': '0', 'background-color': 'rgba(0, 0, 0, 0)'});
  $("#confirm-modal").attr('class', 'modal fade');
}
