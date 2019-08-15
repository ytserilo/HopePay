
function remittance_settings(remittance){

  html = '';
  html += '<div class="modal" style="display: block; background-color: rgba(0, 0, 0, 0.5);" id="remittance_settings" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">';
  html += '<div class="modal-dialog" role="document">';
    html += '<div class="modal-content">';
      html += '<div class="modal-header">';
        html += '<h5 class="modal-title" id="exampleModalLabel">Налаштування договору</h5>';
        html += '<button type="button" onclick="close_modal_remittance()" class="close" data-dismiss="modal" aria-label="Close">';
          html += '<span aria-hidden="true">×</span>';
        html += '</button>';
      html += '</div>';
      html += '<div class="modal-body" id="modal_body">';

        html += '<div class="input-group mb-3">';
            html += '<div class="form-group"> <textarea id="description" style="resize: none;" class="form-control" placeholder="Опис договору *" rows="2" cols="80">'+ remittance['description'] +'</textarea> </div>';
        html += '</div>';
        html += '<div class="input-group mb-3">';

            html += '<div class="form-group"> <input type="number" id="price" class="form-control" placeholder="Ціна *" value="'+ remittance['amount'] +'"> </div>';
        html += '</div>';
        html += '<div class="input-group mb-3">';
        	html += '<div class="form-group"> <select class="form-control" id="currency"> ';
            html += '<option selected value="UAH">UAH</option> ';
          html += '</select> </div>';
          html += '<div class="input-group mb-3">';
          html += '<div class="form-group">';
            if(remittance['postal_transfer']){
              html += '<input id="postal" type="checkbox" checked name="postal">';
            }
            else{
              html += '<input id="postal" type="checkbox" name="postal">';
            }
              html += '<label for="scales">Натисніть якщо товар прийде по пошті</label></div>';
            html += '<div class="form-group installment">';
              if(remittance['payment_by_installments'] == true){
                html += '<input type="checkbox" name="installment" checked id="installment"/>';
              }
              else{
                html += '<input type="checkbox" name="installment" id="installment"/>';
              }
              html += '<label for="installment">Можливість рострочки</label>';
            html += '</div>';

          html += '</div>';
          if(remittance['payment_by_installments']){
            html += '<div class="input-group parts mb-3">';
            html += '<div class="form-group">';
            html += '<label>Оберіть зручну для вас форму розстрочки</label>'
            	html += '<select id="installments_count" class="form-control">';
                for(var i = 2; i <= 12; i++){

                  if(i == remittance['installments_count']){
                    html += '<option selected>'+Math.ceil(remittance['amount'] / i)+'грн. на '+i+' місяців</option>';
                  }else{
                    html += '<option>'+Math.ceil(remittance['amount'] / i)+'грн. на '+i+' місяців</option>'
                  }
                }
              html += '</select>';
            html += '</div>';
            html += '</div>';
          }

        html += '</div>';
      html += '</div>';

      html += '<button class="btn btn-primary" style="background-color: #435f7a;" onclick="create_new_suggestions()">Зберегти</button>';
    html += '</div></div></div>';
    return html;
};
function close_modal_remittance(){
    $("#remittance_settings").remove()
};
function check_bool(el){
  var result = el.attr('checked');
  if(result == undefined){
    return false;
  }else{
    return true;
  }
}
