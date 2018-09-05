$(document).ready(function() {
	socket.onopen = function() {
            request = {
		"type" : "test",
		"message" : "hello world"
		};
		//socket.send(JSON.stringify(request));
	};
	socket.onmessage = function (evt) {
	    notify(evt.data);
	};

	socket.onclose = function(evt) {
	    
	};


function notify(raw_response){
	response = JSON.parse(raw_response);
	if( response.type == 'startGame' ) {
		startGame(raw_response);
	} 

	if( response.type == 'online_list_item' ) {
		var html = '<form action="/ajax/game/create/" method="post" class="ajaxForms"><p><input type="text" name="username1" placeholder="Username" class="flatTextbox" style="width:100px !important; float:left;" value="' + response.username + '" /><input type="text" name="username2" placeholder="Username" class="flatTextbox" style="width:100px !important; float:left;" value="" /><input type="submit" name="start-custom-match" value="Start Game" class="flatButton green" /></p></form>';

		// Get last form
		var last_form =	$('.online_list form:last');
		if( last_form.find('input[type="text"]:last').val() != "" ) {
			$('.online_list').append(html);
		} else {
			last_form.find('input[type="text"]:last').val(response.username);
		}
	}
}
	
});
