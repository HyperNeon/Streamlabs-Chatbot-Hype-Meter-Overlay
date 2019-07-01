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
	
	//------------------------------------------------------
	//  Setup the Guage
	//  SEE http://bernii.github.io/gauge.js/#! 
	//	For Configuration Details
	//------------------------------------------------------
	var opts = {
	  angle: -0.2, // The span of the gauge arc
	  animationSpeed: 100, // How fast to swing the pointer
	  lineWidth: 0.25, // The guage thickness
	  radiusScale: 1.1, // Relative radius size
	  fontSize: 24,
	  pointer: {
		length: 0.56, // Relative to gauge radius
		strokeWidth: 0.044, // The thickness
		color: '#000000' // Fill color
	  },
	  limitMax: true,     // If false, max value increases automatically if value > maxValue
	  limitMin: true,     // If true, the min value of the gauge will be fixed
	  colorStart: "#6F6EA0", // Colors
	  colorStop: "#C0C0DB", // just experiment with them 
	  strokeColor: "#A9A9A9",  // to see which ones work best for you
	  percentColors: [[0.0, "#32CD32" ], [0.49, "#f9c802"], [1.0, "#ff0000"]],
	  generateGradient: true, //Run a gradient over the the above colors instead of hard lines
	  highDpiSupport: true,     // High resolution support
	  // For adding labels on the outside of the gauge
/* 	  staticLabels: { 
		font: "10px sans-serif",  // Specifies font
		labels: [25, 50, 75, 100],  // Print labels at these values
		color: "#000000",  // Optional: Label text color
		fractionDigits: 0  // Optional: Numerical precision. 0=round off.
	  }, */
	  // You can fill in the background bar in zones. This is not compatible with gradient
/* 	  staticZones: [ 
	   {strokeStyle: "#F03E3E", min: 100, max: 130}, // Red from 100 to 130
	   {strokeStyle: "#FFDD00", min: 130, max: 150}, // Yellow
	   {strokeStyle: "#30B32D", min: 150, max: 220}, // Green
	   {strokeStyle: "#FFDD00", min: 220, max: 260}, // Yellow
	   {strokeStyle: "#F03E3E", min: 260, max: 300}  // Red
	  ], */
	};

	var target = document.getElementById('gauge'); // your canvas element
	var gauge = new Gauge(target).setOptions(opts); // create sexy gauge!
	gauge.maxValue = 100; // set max gauge value
	gauge.setMinValue(0);  // Prefer setter over gauge.minValue = 0
	gauge.set(0); // set preliminary value
	
	// Control Variables
	var lastHypeLevel = 0; // What was the hype as of the last socket message
	var hypeReached = false; // Are we currently Hyped?
	
	
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

			gauge.set(newHypeLevel); // set guage value and animate it
			
			// Animate the texts's value from x to y:
			$({hypeValue: lastHypeLevel}).animate({hypeValue: newHypeLevel}, {
				duration: 3000,
				easing:'swing', // can be anything
				step: function() { // called on every step
				  // Update the element's text with rounded-up value:
				  $("#hypeLevelText").html("Hype Level: " + Math.round(this.hypeValue));
				}
			});
			lastHypeLevel = newHypeLevel;

			// Let's play at gif at 100%
			var image = new Image();
			image.src='explosion.gif';
			if (newHypeLevel >= 100 && hypeReached == false) {
				hypeReached = true;
				// Delay by a few seconds before showing gif to allow the bar to animate up
				setTimeout(function() {
					$('#gif').attr('src',image.src);
					// Allow a few seconds for the gif to play 1 time and then remove it
					setTimeout(function() { $("#gif").attr('src',''); }, 3000);
				}, 2500);
				// Do something with this if you'd like some sound
				// $("#sound").html("<embed src=\"" + settings.InSound + "\" hidden=\"true\" />");
			}
			
			if (newHypeLevel < 100) { hypeReached = false; }
				
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