// Start ws connection after document is loaded
$(document).ready(function() {	
  	
	// Connect if API_Key is inserted
	// Else show an error on the overlay
	if (typeof API_Key === "undefined") {
		$("body").html("No API Key found or load!<br>Rightclick on the script in ChatBot and select \"Insert API Key\"");
		$("body").css({"font-size": "20px", "color": "#ff8080", "text-align": "center"});
	}
	else {
		connectWebsocket();
	}
	
});

// Connect to ChatBot websocket
// Automatically tries to reconnect on
// disconnection by recalling this method
function connectWebsocket() {
	
	//-------------------------------------------
	//  Create WebSocket
	//-------------------------------------------
	var socket = new WebSocket("ws://127.0.0.1:3337/streamlabs");

	//-------------------------------------------
	//  Websocket Event: OnOpen
	//-------------------------------------------
	socket.onopen = function() {
		
		// AnkhBot Authentication Information
		var auth = {
			author: "GameTangent",
			website: "twitch.tv/gametangent",
			api_key: API_Key,
			events: [
				"EVENT_HYPE_LEVEL"
			]
		};
		
		// Send authentication data to ChatBot ws server
		socket.send(JSON.stringify(auth));
	};
	
	// Control Variables
	var lastHypeLevel = 0; // What was the hype as of the last socket message	
	
	//-------------------------------------------
	//  Websocket Event: OnMessage
	//-------------------------------------------
	socket.onmessage = function (message) {	
		
		// Parse message
		var socketMessage = JSON.parse(message.data);
		// EVENT_HYPE_LEVEL
		if (socketMessage.event == "EVENT_HYPE_LEVEL") {
			console.log("LOG DATA: " + socketMessage.data)
			
			// Parse the hypelevel from the message
			var eventData = JSON.parse(socketMessage.data);
			var newHypeLevel = eventData.hype_level;
			//1339px == Full Bottle
			
			// Animate the texts's value from x to y:
			$({hypeValue: lastHypeLevel}).animate({hypeValue: newHypeLevel}, {
				duration: 3000,
				easing:'swing', // can be anything
				step: function() { // called on every step
				  document.getElementById("spicy-full").style.height=Math.round(this.hypeValue*13.39) + "px";
				}
			});
			lastHypeLevel = newHypeLevel;
				
			console.log("CURRENT_HYPE_LEVEL: " + eventData.hype_level);
		}
	}

	//-------------------------------------------
	//  Websocket Event: OnError
	//-------------------------------------------
	socket.onerror = function(error) {	
		console.log("Error: " + error);
	}	
	
	//-------------------------------------------
	//  Websocket Event: OnClose
	//-------------------------------------------
	socket.onclose = function() {
		// Clear socket to avoid multiple ws objects and EventHandlings
		socket = null;		
		// Try to reconnect every 5s 
		setTimeout(function(){connectWebsocket()}, 5000);						
	}    

};