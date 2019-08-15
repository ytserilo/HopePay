function IndividualChat(){
	function gen_secret_key(str){
		var result = '';
		for(var i = 0; i < 6; i++){
			result += String(str.charCodeAt(i));
		}

		return BigInt(result.slice(0, 4));
	}
	var remittance_data = undefined;
  var remittance_socket = undefined;
	var hash_text = undefined;
	var mac_text = undefined;
	var send_key = undefined;
	var p_key = undefined;
	var chat_socket = undefined;
	var user_id = $("#user_id").val();
	var secret = undefined;


	this.encrypt = function(msgString) {
			var key = CryptoJS.enc.Utf8.parse(String(hash_text).slice(0, 16));
	    var iv = CryptoJS.lib.WordArray.random(16);
	    var encrypted = CryptoJS.AES.encrypt(msgString, key, {
	        iv: iv
	    });
			var result = iv.concat(encrypted.ciphertext).toString(CryptoJS.enc.Base64)

	    return result;
	}

	this.decrypt = function(ciphertextStr) {
			var key = CryptoJS.enc.Utf8.parse(String(hash_text).slice(0, 16));

	    var ciphertext = CryptoJS.enc.Base64.parse(ciphertextStr);

	    var iv = ciphertext.clone();
	    iv.sigBytes = 16;
	    iv.clamp();
	    ciphertext.words.splice(0, 4);
	    ciphertext.sigBytes -= 16;
	    var decrypted = CryptoJS.AES.decrypt({ciphertext: ciphertext}, key, {
	        iv: iv
	    });

	    return decrypted.toString(CryptoJS.enc.Utf8);
	}

	this.create_connect = function(unique_link){
		$.ajax({
			method: 'GET',
			url: '/chat/dh/',
			data: {
				'id': String(unique_link),
			},
			success: function(data) {
				secret = gen_secret_key($.cookie('csrftoken'));
				if (data['update_key']){
					if (data['update_key']['key_for_other']){
						send_key = data['update_key']['key_for_other'];

						var self_key = BigInt(data['update_key']['self_key']);
						p_key = BigInt(data['update_key']['p'])
						hash_text = self_key**secret % p_key;
						mac_text = CryptoJS.SHA256(String(hash_text)).toString();
					}
					else{
						var shared_key = BigInt(data['update_key']['shared_key']);
						p_key = BigInt(data['update_key']['p']);

						hash_text = shared_key**secret % BigInt(p_key);
						mac_text = CryptoJS.SHA256(String(hash_text)).toString();
					}

				}
				else{
					var shared_key = BigInt(data['shared_key']);
					p_key = BigInt(data['p']);

					hash_text = shared_key**secret % p_key;
					mac_text = CryptoJS.SHA256(String(hash_text)).toString();

				}
			}
		});

	}

	this.web_socks = function(){
		var can_send = true;
		var pathname = window.location.pathname;
		var self = this;
			var socket_url = 'ws://' + window.location.host + pathname;
			try{
				chat_socket.close();
				chat_socket = new WebSocket(socket_url);
			}
			catch{
				chat_socket = new WebSocket(socket_url);
			}

			chat_socket.onopen = function(event){

				if (send_key != undefined){
					data = {
						'shared_key': String(send_key),
					}

					chat_socket.send(JSON.stringify(data));
				}
					if(can_send == true){
						can_send = false;
						$('#send_message').on('click', function(elem) {
							if(document.getElementById('input_chat').value != ''){
								var text = String($("#input_chat").val());
								var data = {
									'message_text': text,
									'id': user_id
								};
								data = self.encrypt(JSON.stringify(data));
								var message = {
									'message_data': data,
									'mac': CryptoJS.HmacSHA256(data, mac_text).toString()
								};

								var send_data = self.encrypt(JSON.stringify(message));

								document.getElementById('input_chat').value = '';
								chat_socket.send(send_data);
							}
						})
					}
			}

			chat_socket.onmessage = function(event){
					var data = event.data;

					try{
						var key_data = JSON.parse(data);
						if(key_data['shared_key'] != send_key){

							hash_text = BigInt(key_data['shared_key'])**secret % p_key;
							mac_text = CryptoJS.SHA256(String(hash_text)).toString();
						}
					}
					catch{
						data = JSON.parse(self.decrypt(String(data)));
						var message_mac = CryptoJS.HmacSHA256(data['message_data'], mac_text).toString();

						if(data['mac'] == message_mac){
							data = JSON.parse(self.decrypt(String(data['message_data'])));

							var message_text = data['message_text'];
							var author_name = data['author_name'];
							var author_photo = data['author_photo'];
							var date_created = data['date_created'];

							if(data['user_id'] == user_id){
								html = '';
								html += '<li class="sent">';
									html += '<img src="'+ author_photo +'" alt="'+ author_name +'" />';
									html += '<p>'+ message_text +'</p>';
								html += '</li>';
								var messages = $(".messages");
								messages.children('ul').append(html);
								messages.animate({scrollTop: document.getElementsByClassName("messages")[0].scrollHeight});
								can_send = true;
							}
							else{
								html = '';
								html += '<li class="replies">';
									html += '<img src="'+ author_photo +'" alt="'+ author_name +'" />';
									html += '<p>'+ message_text +'</p>';
								html += '</li>';
								var messages = $(".messages");
								messages.children('ul').append(html);
								messages.animate({scrollTop: document.getElementsByClassName("messages")[0].scrollHeight});
								can_send = true;
							}
						}
					}
			}
	}
	this.send_smash = function(){
	  var data = {
	    'phone': $('#smash_phone').val(),
	    'card': $('#smash_card').val(),
	    'card_exp_month': $('#smash_card_exp_month').val(),
	    'card_exp_year': $('#smash_card_exp_year').val(),
	    'card_cvv': $('#smash_card_cvv').val(),
	    'smash': $("#smash").val()
	  };

	  data = JSON.stringify({'smash': data});
	  data = this.encrypt(data);
	  var send_data = {
	    'smash': data,
	    'mac': CryptoJS.HmacSHA256(data, mac_text).toString(),
	  };
	  send_data = JSON.stringify(send_data);

	  remittance_socket.send(this.encrypt(send_data));
	}
  this.create_new_suggestions = function(){
    try{
      if(remittance_data['fin_remittance']['paid'] != true){

				var postal = $('#postal').prop('checked');
			  var description = $("#description").val();
			  var amount = $("#price").val();
			  var currency = $("#currency").val();
			  var installment = $("#installment").prop('checked');
			  var installments_count = $('#installments_count').val();

			  var data = {
			    'description': description,
			    'amount': amount,
			    'currency': currency,
			    'postal_transfer': postal,
			    'installment': installment,
			    'installments_count': installments_count,
			  };

			  data = JSON.stringify({'changes': data});
			  data = this.encrypt(data);
			  var send_data = {
			    'changes_data': data,
			    'mac': CryptoJS.HmacSHA256(data, mac_text).toString()
			  };
			  send_data = JSON.stringify(send_data);
			  remittance_socket.send(this.encrypt(send_data));
      }
      else{
        if($("#modal_body").children('.alert-danger').length == 0){
          $("#modal_body").append('<div class="alert alert-danger">Не можна запропонувати свої умови договору коли покупець уже оплатив товар</div>');
        }
      }
    }
    catch{
			var postal = $('#postal').prop('checked');
			var description = $("#description").val();
			var amount = $("#price").val();
			var currency = $("#currency").val();
			var installment = $("#installment").prop('checked');
			var installments_count = $('#installments_count').val();

			var data = {
				'description': description,
				'amount': amount,
				'currency': currency,
				'postal_transfer': postal,
				'installment': installment,
				'installments_count': installments_count,
			};

			data = JSON.stringify({'changes': data});
			data = this.encrypt(data);
			var send_data = {
				'changes_data': data,
				'mac': CryptoJS.HmacSHA256(data, mac_text).toString()
			};
			send_data = JSON.stringify(send_data);
			remittance_socket.send(this.encrypt(send_data));
    }

  }
  this.accept_confirmation = function(changes_id){
    var data = {
      'changes_id': changes_id
    };

    data = JSON.stringify({'accept': data});
    data = this.encrypt(data);
    var send_data = {
      'accept_data': data,
      'mac': CryptoJS.HmacSHA256(data, mac_text).toString(),
    };
    send_data = JSON.stringify(send_data);

    remittance_socket.send(this.encrypt(send_data));
  }
  this.pay = function(){
    var data = {
      'phone': $('#phone').val(),
      'card': $('#card').val(),
      'card_exp_month': $('#card_exp_month').val(),
      'card_exp_year': $('#card_exp_year').val(),
      'card_cvv': $('#card_cvv').val(),
    };
    data = JSON.stringify({'pay': data});
    data = this.encrypt(data);
    var send_data = {
      'pay_data': data,
      'mac': CryptoJS.HmacSHA256(data, mac_text).toString(),
    };
    send_data = JSON.stringify(send_data);
    remittance_socket.send(this.encrypt(send_data));
  }
  this.send = function(){
    var data = {
      'postal_code': $('#postal_code').val(),
      'phone_number': $('#phone_number').val(),
    };
    data = JSON.stringify({'shipped': data});
    data = this.encrypt(data);
    var send_data = {
      'shipped_data': data,
      'mac': CryptoJS.HmacSHA256(data, mac_text).toString(),
    };
    send_data = JSON.stringify(send_data);

    remittance_socket.send(this.encrypt(send_data));
  }
  this.confirm = function(){
    var data = this.encrypt(JSON.stringify({"confirm": "confirm"}));
    var send_data = {
      'confirm_data': data,
      'mac': CryptoJS.HmacSHA256(data, mac_text).toString(),
    };
    send_data = JSON.stringify(send_data);
    remittance_socket.send(this.encrypt(send_data));
  }
  this.cencell = function(){
    var data = this.encrypt(JSON.stringify({"cencell": "cencell"}));
    var send_data = {
      'cencell_data': data,
      'mac': CryptoJS.HmacSHA256(data, mac_text).toString(),
    };
    send_data = JSON.stringify(send_data);
    remittance_socket.send(this.encrypt(send_data));
  }

  function change_remittance_info(pre, data){
    $("#"+ pre +"_description").text('Опис : ' + data['description']);
    $("#"+ pre +"_price").text('Ціна : ' + data['amount']);
    $("#"+ pre +"_currency").text('Валюта : ' + data['currency']);
    $("#"+ pre +"_postal").text('Поштовий переказ : ' + data['postal_transfer']);
  }

  this.remittance_changes = function(){
    var socket_url = 'ws://' + window.location.host + '/remittance/'+ room_id +'/';
		var self = this;
    try{
      remittance_socket.close();
      remittance_socket = new WebSocket(socket_url);
    }
    catch{
      remittance_socket = new WebSocket(socket_url);
    }

    remittance_socket.onopen = function(event){}
    remittance_socket.onmessage = function(event){
      var data = JSON.parse(self.decrypt(event.data));
      try{
        data = JSON.parse(data);
      }
      catch{
          data = data;
      }

      if(data['shipped_data']){
        if(data['mac'] == CryptoJS.HmacSHA256(data['shipped_data'], mac_text)){
          data = JSON.parse(self.decrypt(data['shipped_data']));

          if(data['shipped-status']['success'] != undefined){
            remittance_data['fin_remittance']['shipped'] = true;
            if(remittance_data['fin_remittance']['postal_transfer'] == true){
              remittance_data['fin_remittance']['postal_code'] = data['shipped-status']['postal_code'];
            }

            var postal_modal = $("#modal_body");
            postal_modal.children(".alert-danger").remove();
            postal_modal.children(".alert-success").remove();

            if(user_id == data['shipped-status']['user_id']){
              postal_modal.append('<div class="alert alert-success">'+ data['shipped-status']['success'] +'</div>');
              $("#postal-modal").children().remove();
              $('.modal-status').remove();
              if(remittance_data['fin_remittance']['postal_transfer'] == true){
                $("#postal-modal").append('<a target="_blank" href="https://novaposhta.ua/tracking/?cargo_number='+ data['shipped-status']['postal_code'] +'&amp;newtracking=1">Натисніть щоб відстежети посилку</a><p class="shipped-status">Статус відправлення: товар чи послуга була відправленна</p>');
              }
              else{
                $("#postal-modal").append('<p class="shipped-status">Статус відправлення: товар чи послуга була відправленна</p>');
              }
            }
            else{
              $("#postal-modal").children().remove();
              if(remittance_data['fin_remittance']['postal_transfer'] == true){
                $("#postal-modal").append('<a target="_blank" href="https://novaposhta.ua/tracking/?cargo_number='+ data['shipped-status']['postal_code'] +'&amp;newtracking=1">Натисніть щоб відстежети посилку</a><p class="shipped-status">Статус відправлення: товар чи послуга була відправленна</p>');
              }
              else{
                $("#postal-modal").append('<p class="shipped-status">Статус відправлення: товар чи послуга була відправленна</p>');
              }

            }
          }
          else{
            if(user_id == data['shipped-status']['user_id']){
              var postal_modal = $("#modal_body");

              postal_modal.children(".alert-danger").remove();
              postal_modal.children(".alert-success").remove();
              postal_modal.append('<div class="alert alert-danger">'+ data['shipped-status']['error'] +'</div>');
            }

          }
        }

      }
      else if(data['confirm_data']){
        if(data['mac'] == CryptoJS.HmacSHA256(data['confirm_data'], mac_text)){
          data = JSON.parse(self.decrypt(data['confirm_data']));
          try{
            data = JSON.parse(data);
          }
          catch{
              data = data;
          }

          if(data['confirm']['error']){
            if(user_id == data['confirm']['user_id']){
              var postal_modal = $("#modal_body");
              postal_modal.children(".alert-danger").remove();
              postal_modal.append('<div class="alert alert-danger">'+ data['confirm']['error'] +'</div>');
            }
          }
          else{
            var html = '<div class="content">';
            html += '<div class="messages" style="text-align: center;">';
            html += '<i class="fa fa-check-circle" style="display: flex;justify-content: center;font-size: 150px;margin-top: 45%;text-align: center;"></i>';
            html += '<p style="font-size: 40px;">Договір успішний</p></div></div>';
            $("#remittance_settings").remove();
            $("#frame").children('.content').remove();
            $('#frame').append(html);
          }
        }
      }
      else if(data['cencell']){
        if(data['mac'] == CryptoJS.HmacSHA256(data['cencell'], mac_text)){
          data = JSON.parse(self.decrypt(data['cencell']));
          try{
            data = JSON.parse(data);
          }
          catch{
              data = data;
          }
          if(data['cencell']['error']){
            var postal_modal = $("#modal-status");
            postal_modal.children(".alert-danger").remove();
            postal_modal.append('<div class="alert alert-danger">'+ data['cencell']['error'] +'</div>');
          }
          else{
            var html = '';
            html += '<div class="content">';
            html += '<div class="messages" style="text-align: center;">';
            html += '<i class="fa fa-exclamation-triangle" style="display: flex;justify-content: center;font-size: 150px;margin-top: 45%;text-align: center;"></i>';
            html += '<p style="font-size: 40px;">Договір відкликаний</p></div></div>';
            $("#remittance_settings").remove();
            $("#frame").children('.content').remove();
            $('#frame').append(html);
          }
        }
      }
      else if(data['pay_data']){
        if(data['mac'] == CryptoJS.HmacSHA256(data['pay_data'], mac_text)){

          data = JSON.parse(self.decrypt(data['pay_data']));

          try{
            data = JSON.parse(data);
          }
          catch{
              data = data;
          }

          if(data['pay-status']['success']){
            remittance_data['fin_remittance']['paid'] = true;
            var pay_modal = $("#modal-status");
            if(user_id == data['pay-status']['user_id']){
              pay_modal.children(".alert-danger").remove();
              pay_modal.children(".alert-success").remove();
              pay_modal.append('<div class="alert alert-success">'+ data['pay-status']['success'] +'</div>');
             $('#modal-status').children().remove();
            }
            $(".pay-status").html('Статус оплати: Оплачено');
          }
          else{
            var pay_modal = $("#modal-status");
            if(user_id == data['pay-status']['user_id']){
              pay_modal.children(".alert-danger").remove();
              pay_modal.children(".alert-success").remove();
              pay_modal.append('<div class="alert alert-danger">'+ data['pay-status']['error'] +'</div>');
            }
          }
        }
      }
			else if(data['smash']){
				if(data['mac'] == CryptoJS.HmacSHA256(data['smash'], mac_text)){
					data = JSON.parse(self.decrypt(data['smash']));
					if(data['smash_data']['error']){
						alert('error');
					}
					else if (data['smash_data']['success']) {
						alert('success');
					}
				}
			}
      else{
        if(data['mac'] == CryptoJS.HmacSHA256(data['changes_data'], mac_text)){
          data = JSON.parse(self.decrypt(data['changes_data']));
          try{
            data = JSON.parse(data);
          }
          catch{
              data = data;
          }

          var self_remittance = undefined;
          var other_remittance = undefined;
          var fin_remittance = undefined;

          if(data['fin_remittance']){
            fin_remittance = data['fin_remittance'];
          }

          else if(data['self_remittance']){
            if(data['self_remittance']['id'] == $("#user_id").val()){
              self_remittance = data['self_remittance'];
              other_remittance = data['other_remittance'];
            }
            else if(data['self_remittance']['id'] != $("#user_id").val()){
              self_remittance = data['other_remittance'];
              other_remittance = data['self_remittance'];
            }
          }


          remittance_data = {
            'fin_remittance': fin_remittance,
            'self_remittance': self_remittance,
            'other_remittance': other_remittance
          };

          if(fin_remittance != undefined){
            var html = modal_info(remittance_data);
            $("#remittance_settings").remove();
            $("body").prepend(html);
          }
          else {
            if(self_remittance != undefined && other_remittance == undefined){
              if($("#remittance_settings").length != 0){
                var html = modal_info(remittance_data);
                $("#remittance_settings").remove();

                $("body").prepend(html);
              }

            }
            else if(self_remittance == undefined && other_remittance != undefined){

              if($("#remittance_settings").length != 0){
                var html = modal_info(remittance_data);
                $("#remittance_settings").remove();

                $("body").prepend(html);
              }

            }
            else if(self_remittance != undefined && other_remittance != undefined){

              var html = modal_info(remittance_data);
              $("#remittance_settings").remove();

              $("body").prepend(html);
            }
          }
        }

      }

    }
    remittance_socket.onclose = function(event){}
  }
	this.remittance_settings_and_info = function(){
	  var settings_remittance = $("#settings-remittance");
	  var info_remittance = $("#info-remittance");

	  info_remittance.on('click', function(){
	    var dom = modal_info(remittance_data);
	    $("body").prepend(html);
	  });
		settings_remittance.on('click', function(){
	    var remittance = undefined;
	    if(remittance_data['fin_remittance']){
	      var html = remittance_settings(remittance_data['fin_remittance']);
	      remittance = remittance_data['fin_remittance'];
	    }
	    else{
	      var html = remittance_settings(remittance_data['self_remittance']);
	      remittance = remittance_data['self_remittance'];
	    }

	    $("body").prepend(html);

			$("#price").on('input', function(){
			  $("#installments_count").children('option').remove();

			  var html = '';
			  for(var i = 2; i <= 12; i++){
			    if(i == 2){
			      html += '<option selected>'+Math.ceil(Number($("#price").val()) / i)+'грн. на '+i+' місяців</option>';
			    }else{
			      html += '<option>'+Math.ceil(Number($("#price").val()) / i)+'грн. на '+i+' місяців</option>'
			    }
			  }
				$("#installments_count").append(html);
			});

	    $("#installment").on('click', function(){

	      var parent = $("#installment").parent().parent().parent();
	      if($("#installment").prop('checked') == true){
	        var html = '';
	        html += '<div class="input-group parts mb-3">';
	        html += '<div class="form-group">';
	        html += '<label>Оберіть зручну для вас форму розстрочки</label>'
	          html += '<select id="installments_count"  class="form-control">';
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
	        parent.append(html);
	      }else{

	        parent.children('.parts').remove();
	      }
	    });
	  });
	}
	this.open_chat = function(unique_link){
	  room_id = unique_link;
		var self = this;
	  $.ajax({
	    url: '/chat/chat_room/'+String(unique_link)+'/',
	    method: 'GET',
	    data: {
	      'start': -20,
	      'finish': 0,
	      'key': load_chat_key
	    },
	    success: function(data){
	      if (data['error']){
	        window.history.replaceState('string', 'title', '/chat/chat_room/'+unique_link+'/');

	        var dom = gen_html(data);
	        if($("#frame").children('.content').length > 0){

	          $('.messages').children().remove();
	          $("#frame").children('.messages').append(dom);
	          if($('#unread').length == 0){
	            $(".messages").animate({ scrollTop: $('.messages').prop('scrollHeight') }, "fast");
	          }
	          else{
	            $('.messages').animate({scrollTop: $('#unread').offset().top - $('.messages').prop('clientHeight')}, 'fast');
	          }
	        }else{
	          $('.messages').children().remove();
	          $("#frame").children('.messages').append(dom);
	          if($('#unread').length == 0){
	            $(".messages").animate({ scrollTop: $('.messages').prop('scrollHeight') }, "fast");
	          }
	          else{
	            $('.messages').animate({scrollTop: $('#unread').offset().top - $('.messages').prop('clientHeight')}, 'fast');
	          }

	        }

	        self.create_connect(unique_link);
	        self.web_socks();
	        create_invite();
	        remittance_settings_and_info();
	        self.remittance_changes();


	      }else{
	        var data = encrypt_chat(crypt, data);

	          window.history.replaceState('string', 'title', '/chat/chat_room/'+unique_link+'/');
	          remittance_data = data;
	          var dom = gen_html(data);
	          if($("#frame").children('.content').length > 0){
	            $("#frame").children('.content').remove();
	            $("#frame").append(dom);
	            if($('#unread').length == 0){
	              $(".messages").animate({ scrollTop: $('.messages').prop('scrollHeight') }, "fast");
	            }
	            else{
	              $('.messages').animate({scrollTop: $('#unread').offset().top - $('.messages').prop('clientHeight')}, 'fast');
	            }
	          }else{
	            $("#frame").append(dom);
	            if($('#unread').length == 0){
	              $(".messages").animate({ scrollTop: $('.messages').prop('scrollHeight') }, "fast");
	            }
	            else{
	              $('.messages').animate({scrollTop: $('#unread').offset().top - $('.messages').prop('clientHeight')}, 'fast');
	            }
	          }

	          self.create_connect(unique_link);
	          self.web_socks();

	          load_content();
	          create_invite();
	          remittance_settings_and_info();
	          self.remittance_changes();

	      }
	    }
	  })
	}
}
