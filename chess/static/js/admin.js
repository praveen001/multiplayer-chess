window.onload = function() {
/*
	socket.onmessage = function (evt) {
	    notify(evt.data);
	};

	function notify(raw_response){

		response = JSON.parse(raw_response);
		if(response.type == "gameReport" ) {
			//alert(raw_response);
			// Reports are available here
		}
	}

*/
	$('.checkOnline').blur(function(e) {
		var self = this;
		if($(this).val().length != 0) {
			socket.send(JSON.stringify({
				"type" : "isOnline",
				"user" : $(self).val(),
			}));
		}
	});

	$('.reportgame').click(function() {
		var self = this;
		if($('input[name="master"]').val().length != 0) {
			var temp_socket = new WebSocket("ws://" + $('input[name="master"]').val() + ":8080/socket?id=admin");
			temp_socket.onopen = function() {
				temp_socket.send(JSON.stringify({
					"type" : "gameReport",
					"report" : $(self).attr('data-json'),
				}));
			};
			alert("Game Reported");
		} else {
			alert("Enter master ip");
		}
	});

	$('.deletegame').click(function() {
		var self = this;
		socket.send(JSON.stringify({
			"type" : "deleteGame",
			"gameid" : $(self).attr('data-gameid')
		}));
	});

	// Center The Login Form
	try {
		loginForm = document.getElementsByClassName('loginform')[0];
	} catch(e) {
		error = true;
	}

	if( undefined != loginForm) {
		loginForm.style.top = ( window.innerHeight / 2 )  - ( loginForm.clientHeight / 2 ) + 'px';
		loginForm.style.left = ( window.innerWidth / 2 ) - ( loginForm.clientWidth / 2 ) + 'px';
	}

	$(document).on("submit", ".redirectForm", function(e) {
		socket.send(JSON.stringify({
			"type" : "redirect",
			"ip" : $('input[name="ip"]').val(),
			"user" : $('input[name="redirectuser"]').val(),
		}));
		e.preventDefault();
	});
	
	$(document).on("submit", '.ajaxForms', function(e) {
		xhr = new XMLHttpRequest();
		xhr.open( 'POST', this.getAttribute('action') );
		xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
		xhr.send(JSON.stringify($(this).serializeArray()));
		form = this;
		xhr.onreadystatechange = function() {
		if( xhr.readyState == 4 ) {
				response = JSON.parse(xhr.response);
				if(response.hasOwnProperty('error')) {
					alert(response.error);
				}
				if(response.hasOwnProperty('success')) {
					alert(response.success);
					form.reset();
				}
				if(response.hasOwnProperty('route')) {
					socket.send(xhr.response);
				}
			}
		}
		
		e.preventDefault();
	});

	// refreshing
	$('.refresh').click(function(e) {
		request = {
			"type" : "adminRefresh"
		}
		socket.send(JSON.stringify(request));
	});
}


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = $.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
