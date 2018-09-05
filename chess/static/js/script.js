var white_clock, black_clock, allowUnload = true, isGameOver = false, move;
var billegal = 0, willegal = 0, isGameOver = false, touchpiece = '', touchpiecesquare = '',touchpiecesquarecolor = '', promotion_piece = 'q';

var init = function(color, me, enemy) {
	// Variable Declarations
	var board, movecount = 0, game = new Chess(), statusEl = $('.status'), fenEl = $('.fen'), pgnEl = $('.pgnn');
	var max_illegal_moves = 2, has_made_illegal = 0;

	var onPieceSelect = function(source, piece, position, orientation, e) {
		// If this user has the turn to play
		
		if( (game.turn() == 'w' && color == "white" )  || (game.turn() == 'b' && color == "black" ) ) {
			// If yes, check if game has ended already
			if( isGameOver ) {
				allowToMove = false;
			} else {
				allowToMove = true;
			}
		} else {
			allowToMove = false;
		}


		// Check if this user can move this piece
		if (allowToMove == false || game.game_over() === true || (game.turn() === 'w' && piece.search(/^b/) !== -1) || 	(game.turn() === 'b' && piece.search(/^w/) !== -1)) {
			return false;
		} else {
			// If touchpiece is not set
			if( touchpiece == '' ) {
				// Check if it has possible legal moves
				var moves = game.moves({
					square : source,
					verbose: true
				});
				
				// If it has valid moves, set touch piece
				if( moves.length != 0) {
					touchpiece = source;
					touchpiecesquare = e;
					touchpiecesquarecolor = $(e).css('background-color');
					$(e).css({'background-color':'red'});
					$('.touchpiece').html(touchpiece);
					if( (piece == 'wP') && ( source.charAt(1) == 7 ) ) {
						$('.promotion').show();
					}
					if( (piece == 'bP') && (source.charAt(1) == 2) ) {
						$('.promotion').show();
					}
					$('input[name="pawn_promotion"]').click(function(e) {
						promotion_piece = $('input[name="promotion"]:checked').val();
						$('.promotion').hide();
						e.preventDefault();
					});
				}
				// Allow to pick up piece
				return true;

			} else {
				// Restrict touch piece
				if( source == touchpiece ) {
					return true;
				} else {
					return false;
				}
			}
			
		}
	}

	// Drop piece
	var onDrop = function(source, target, piece) {
		// Prevent move if dropped on same square
		if( source == target ) return;
		
		movecount++;

		var move = game.move({
			from: source,
			to: target,
			promotion : promotion_piece
		});
		
		if( move !== null ) {
			has_made_illegal = 0;
		}
		if( (has_made_illegal != 1) && ((game.turn() == 'b' && move !== null) || (game.turn() == 'w' && move === null)) ) {
			var mn = parseInt($('.col1 p:last').html()) + 1 ;
			$('.col1').append('<p>'+mn+'</p>');
			$('.col2').append('<p>' + source + ' - ' + target + '</p>');
		} else if( has_made_illegal != 1 ) {
			var mn = parseInt($('.col3 p:last').html()) + 1 ;
			$('.col3').append('<p>'+mn+'</p>');
			$('.col4').append('<p>' + source + ' - ' + target + '</p>');
		} 

		// illegal move
		if (move === null && source != target ) {
			// Count illegal move
			if( game.turn() == 'b' && has_made_illegal == 0 ) {
				billegal++;

				// Give a warning
				if( billegal == 1 ) {
					alert('One more illegal move, you will lose the game');
				}
				// Mark last illegal move
				$('.col4 p:last').css({"color":"#FF0000"});
				$('.billegal').html('Illegal Moves : ' + billegal);
				// Update Database
				socket.send(JSON.stringify({
					"type" : "illegal",
					"from" : source,
					"to" : target,
					"recipient" : enemy,
					"by" : 'b',
					"count" : billegal,
					"black_time" : black_clock.getTime().toString(),
					"white_time" : white_clock.getTime().toString(),
					"billegal" : billegal,
					"willegal" : willegal
				}));
			} 
			if( game.turn() == 'w' && has_made_illegal == 0 ) {
				willegal++;
				if( willegal == 1 ) {
					alert('One more illegal move, you will lose the game');
				}
				$('.col2 p:last').css({"color":"#FF0000"});
				$('.willegal').html('Illegal Moves : ' + willegal);
				socket.send(JSON.stringify({
					"type" : "illegal",
					"from" : source,
					"to" : target,
					"recipient" : enemy,
					"by" : 'w',
					"count" : willegal,
					"black_time" : black_clock.getTime().toString(),
					"white_time" : white_clock.getTime().toString(),
					"billegal" : billegal,
					"willegal" : willegal
				}));
			}
			has_made_illegal = 1;
			updateStatus();
			return 'snapback';
		}
	
		if( source != target ) {
			touchpiece = "";
			has_made_illegal = 0;
			$(touchpiecesquare).css({'background-color':touchpiecesquarecolor});
			$('.touchpiece').html('NONE');
		}
	
		updateStatus();
		if( isGameOver == true ) {
			gameEnded = 1
		} else {
			gameEnded = 0
		}
	
		var movet = {
			from: source,
			to: target,
			by : color,
			promotion: promotion_piece, // NOTE: always promote to a queen for example simplicity
			type : 'syncMove',
			recipient : enemy,
			fen : game.fen(),
			sender : me,
			status : statusEl.html(),
			turn : game.turn(),
			end : gameEnded, 
			wtime : parseInt(white_clock.getTime()),
			btime : parseInt(black_clock.getTime())
		};
	
		if( movecount == 5 ) {
			socket.send( JSON.stringify({
				type : 'clockSync',
				black_time : black_clock.getTime().toString(),
				white_time : white_clock.getTime().toString(),
				recipient : enemy
			}));
			movecount = 0;
		}
		socket.send(JSON.stringify(movet));
	};

	// update the board position after the piece snap 
	// for castling, en passant, pawn promotion
	var onSnapEnd = function() {
		board.position(game.fen());
	};

	var updateStatus = function() {
		var status = '';
		if( game.turn() == 'w' ) {
			allowToMove = true;
			var moveColor = 'White';
		}
		if (game.turn() === 'b') {
			allowToMove = true;
			moveColor = 'Black';
		}

		// checkmate?
		if (game.in_checkmate() === true) {
			isGameOver = true;
			allowUnload = true;
			status = 'Game over, ' + moveColor + ' is in checkmate.';
			black_clock.stop();
			white_clock.stop();
			if( game.turn() == 'w' ) {
				alert( "Game Over! Black Wins" );
			} else {
				alert("Game Over! White Wins" );
			}
		}

		// draw?
		else if (game.in_draw() === true) {
			isGameOver = true;
			allowUnload = true;
			status = 'Game over, drawn position';
			black_clock.stop();
			white_clock.stop();
			alert("Draw");
		}
	
		// game still on
		else {
			status = moveColor + '\'s turn to move';

			// check?
			if (game.in_check() === true) {
				status += ', ' + moveColor + ' is in check';
			}
		}

		if( billegal >= max_illegal_moves ) {
			isGameOver = true;
			allowUnload = true;
			status = 'Game Over, Black made 2 illegal moves';
			black_clock.stop();
			white_clock.stop();
			isGameOver = true;
			alert( "Game Over! White Wins" );
		}

		if( willegal >= max_illegal_moves ) {
			isGameOver = true;
			allowUnload = true;
			status = 'Game Over, White made 2 illegal moves';
			black_clock.stop();
			white_clock.stop();
			isGameOver = true;
			alert("Game Over! Black Wins" );
		}

		statusEl.html(status);
		fenEl.html(game.fen());
		pgnEl.html(game.pgn());
	};

	var cfg = {
		draggable: true,
		position: 'start',
		//onDragStart: onDragStart,
		onDrop: onDrop,
		onSnapEnd: onSnapEnd,
		onPieceSelect:onPieceSelect,
		showErrors : 'alert'
	};
	board = new ChessBoard('board1', cfg);
	if( color == "black" ) {
		board.flip();
	}
//	board.start()
	updateStatus();
	return {
		myboard : board,
		mygame : game,
		update : updateStatus
	};
};

//////////////////////////////////////////////////////////

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

var myGame;

function startGame(response) {	
	allowUnload = false;
	$('.bclock').show();
	$('.wclock').show();
	key = getCookie('userCookie');
	response = JSON.parse(response);
	color = (key == response.game.white.key) ? "white" : "black";
	enemy = ( color == "white" ) ? response.game.black.id : response.game.white.id ;
	me = ( color == "white" ) ? response.game.white.id : response.game.black.id;
	myGame = init(color, me, enemy);	
	// start delay here
	white_clock.start();
}

function restoreGame(response) {
	response = JSON.parse(response);
	$('.bclock, .wclock').show();
	key = getCookie('userCookie');
	if( response.game.black.key == getCookie('userCookie') ) {
		color = "black";
		me = response.user2;
		enemy = response.user1;
	} else {
		color = "white";
		me = response.user1;
		enemy = response.user2; 
	}
	myGame = init(color, me, enemy);
	$('.willegal').html('Illegal Moves : ' + response.willegal);
	$('.billegal').html('Illegal Moves : ' + response.billegal);
	billegal = parseInt(response.billegal);
	willegal = parseInt(response.willegal);
	black_clock.setTime(response.btime);
	white_clock.setTime(response.wtime);
	if( response.turn == 'w' ) {
		status = "White's turn to move"
		white_clock.start();
	} else {
		status = "Black's turn to move"
		black_clock.start();
	}
	$('.status').html(status);
	myGame.myboard.position( response.fen );
	myGame.mygame.load(response.fen);
	moveColor = ( myGame.mygame.turn() == 'w' ) ? "white" : "black";
	isGameOver = false;
	allowUnload = false;
}

$(document).ready(function() {
	$('.promotion').each(function() {
		var dialog = this;
		dialog.style.top = ( $(window).innerHeight() - $(this).height()  ) / 2 - 100 + 'px';
		dialog.style.left =( $(window).innerWidth() - $(this).width() ) / 2 + 'px';
	});

	//init("white", "123", "456");
	
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
		if(response.type == "alert" ) {
			alert(response.msg);
		}
		if(response.type == "redirect") {
			 window.location.assign("http://"+response.ip+":8080");
		}
		if(response.type == "report" ) {
			
		}
		if( response.type == "onlinestatus" ) {
			alert( response.user + ' is ' + response.status );
		}
		if( response.type == 'refresh' ) {
			location.reload();
		}
		if( response.type == 'startGame' || response.type == "pairup" ) {
			startGame(raw_response);
		} 
		if( response.type == 'pause' ) {
			black_clock.stop();
			white_clock.stop();
			isGameOver = true;
		}
		if( response.type == 'restore' ) {
			restoreGame(raw_response);
		}
		if( response.type == 'resume' ) {
			black_clock.setTime(response.btime);
			white_clock.setTime(response.wtime);
			if( myGame.mygame.turn() == 'w' ) {
				white_clock.start();
			} else {
				black_clock.start();
			}
			isGameOver = false;
		}
		if( response.type == 'clockSync') {
			black_clock.setTime(response.black_time);
			white_clock.setTime(response.white_time);
		}

		if( response.type == 'illegal' ) {
			$('.' + response.by + 'illegal').html('Illegal Moves : ' + response.count );
			if( response.by == 'w' ) {
				$('.col1').append('<p>' + (parseInt($('.col1 p:last').html()) + 1) + '</p>' );
				$('.col2').append('<p>' + response.from + ' - ' + response.to + '</p>');
				$('.col2 p:last').css({"color":"#FF0000"});
			} else {
				$('.col3').append('<p>' + (parseInt($('.col3 p').html()) + 1) + '</p>');
				$('.col4').append('<p>' + response.from + ' - ' + response.to + '</p>');
				$('.col4 p:last').css({"color":"#FF0000"});
			}
			if( response.count >= 2 ) {
				if( response.by == 'w' ) {
					status = 'Game Over, White made 2 illegal moves';
					alert("Game Over! Black Wins");
				} else {
					status = 'Game Over, Black made 2 illegal moves';
					alert("Game over! White Wins");
				}
				$('.status').html(status);
				black_clock.stop();
				white_clock.stop();
				isGameOver = true;
			}
		}		

		if( response.type == 'syncTime' && isGameOver == false ) {
			if( response.turn == 'b' ) {
				black_clock.start();
				white_clock.stop();
				white_clock.setTime( parseInt(white_clock.getTime()) + 5 );
			} else {
				black_clock.stop();
				white_clock.start();
				black_clock.setTime( parseInt(black_clock.getTime()) + 5 );
			}			
		}

		if( response.type == "syncMove" ) {
			$('.status').html(response.status);
			var m = myGame.mygame.move({
				from: response.from,
				to: response.to,
				promotion: response.promotion, // NOTE: always promote to a queen for example simplicity
			});

			myGame.myboard.position( response.fen );
			var tokens = response.fen.split(' ');
			moveColor = ( myGame.mygame.turn() == 'w' ) ? "black" : "white";
			
			if( myGame.mygame.turn() == 'b' ) {
				var mn = parseInt($('.col1 p:last').html()) + 1 ;
				$('.col1').append('<p>'+mn+'</p>');
				$('.col2').append('<p>' + response.from + ' - ' + response.to + '</p>');
			} else {
				var mn = parseInt($('.col3 p:last').html()) + 1 ;
				$('.col3').append('<p>'+mn+'</p>');
				$('.col4').append('<p>' + response.from + ' - ' + response.to + '</p>');
			}

			// checkmate?
			if (myGame.mygame.in_checkmate() === true) {
				isGameOver = true;
				allowUnload = true;
				black_clock.stop();
				white_clock.stop();
				status = 'Game over, ' + moveColor + ' is in checkmate.';
				winner = ( myGame.mygame.turn() == 'b' ) ? "white" : "black";
				socket.send(JSON.stringify({
					"type" : "result",
					"result" : winner,
					"whitetimer" : white_clock.getTime().toString(),
					"blacktimer" : black_clock.getTime().toString()
				}));
				alert("Game Over! " + winner + ' Wins');
			

			// draw?

			} else if( myGame.mygame.insufficient_material() === true ) {
				isGameOver = true;
				allowUnload = true;
				black_clock.stop();
				white_clock.stop();
				status = 'Draw, Insufficient material';
				socket.send(JSON.stringify({
					"type" : "result",
					"result" : "draw",
					"whitetimer" : white_clock.getTime().toString(),
					"blacktimer" : black_clock.getTime().toString()
				}));
				alert("Draw");
			} else if( myGame.mygame.in_stalemate() === true ) {
				isGameOver = true;
				allowUnload = true;
				black_clock.stop();
				white_clock.stop();
				status = 'Draw, Stalemate';
				socket.send(JSON.stringify({
					"type" : "result",
					"result" : "draw",
					"whitetimer" : white_clock.getTime().toString(),
					"blacktimer" : black_clock.getTime().toString()
				}));
				alert("Draw");
			} else if( myGame.mygame.in_threefold_repetition() === true ) {
				isGameOver = true;
				allowUnload = true;
				black_clock.stop();
				white_clock.stop();
				status = 'Draw, Threefold repetition';
				socket.send(JSON.stringify({
					"type" : "result",
					"result" : "draw",
					"whitetimer" : white_clock.getTime().toString(),
					"blacktimer" : black_clock.getTime().toString()
				}));
				alert("Draw");
			} else if (myGame.mygame.in_draw() === true) {
				isGameOver = true;
				allowUnload = true;
				black_clock.stop();
				white_clock.stop();
				status = 'Game over, drawn position';
				socket.send(JSON.stringify({
					"type" : "result",
					"result" : "draw",
					"whitetimer" : white_clock.getTime().toString(),
					"blacktimer" : black_clock.getTime().toString()
				}));
				alert("Draw");
			}
	
			// game still on
			else {
				status = moveColor + '\'s turn to move';

				// check?
				if (myGame.mygame.in_check() === true) {
					status += ', ' + moveColor + ' is in check';
				}
			}		
		} 	
	}



/////////////////////////////////////
// Clock ///////////////////////////
///////////////////////////////////
	
	
	//$('.bclock').hide();
	//$('.wclock').hide();
	white_clock = $('.wclock').FlipClock(600, {
        	clockFace: 'MinuteCounter',
        	countdown: true,
       	 	autoStart: false,
       	 	callbacks: {
        		start: function() {
        			$('.message').html('The clock has started!');
        		},
			stop : function() {
				$('.message').html('The clock has stopped');
			}
       	 	}
	});

	black_clock = $('.bclock').FlipClock(600, {
        	clockFace: 'MinuteCounter',
        	countdown: true,
        	autoStart: false,
        	callbacks: {
        		start: function() {
        			$('.message').html('The clock has started!');
        		},
			stop : function() {
				$('.message').html('The clock has stopped');
			}
       	 	}
    	});


	var bflag = 0, wflag = 0;
	setInterval(function() {
		var time = black_clock.getTime();
		if( time == 0 && bflag ) { 
			// code here
			if( isGameOver == false ) {
				socket.send(JSON.stringify({
					"type" : "result",
					"result" : "white",
					"whitetimer" : white_clock.getTime().toString(),
					"blacktimer" : black_clock.getTime().toString()
				}));
				isGameOver = true;
				alert("Game over! White wins");
			}
		}
		if( time == 0 ) {
			bflag = 1;
		}
	}, 1000);
	setInterval(function() {
		var time = white_clock.getTime();
		if( time == 0 && wflag ) { 
			// code here
			if( isGameOver == false ) {
				socket.send(JSON.stringify({
					"type" : "result",
					"result" : "black",	
					"whitetimer" : white_clock.getTime().toString(),
					"blacktimer" : black_clock.getTime().toString()
				}));
				isGameOver = true;
				alert("Game over! Black wins");
			}
		}
		if( time == 0 ) {
			wflag = 1;
		}
	}, 1000);

	$(window).bind('beforeunload', function(){
		if( !allowUnload ) { 
			socket.send(JSON.stringify({
				"type" : "result",
				"result" : "pending",
				"whitetimer" : white_clock.getTime().toString(),
				"blacktimer" : black_clock.getTime().toString()
			}));
		}
	});
});		
