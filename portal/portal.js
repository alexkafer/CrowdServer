
var url = "http://ec2-18-220-127-31.us-east-2.compute.amazonaws.com";

function getPlayers(callback) {
	$.get(
		url + "/players",
		{},
		callback,
		"json"
	);
}

function kickPlayer(playerId) {
	console.log("Kicking " + playerId);
	$.post(
		url + "/kick/" + playerId.toString(),
		{},
		function(data, status, jqXHR) {
			if (status == "success") {
				console.log(playerId + " kicked");
				onload();
			} else {
				console.log("Problem kicking player " + playerId);
			}
		}
	);
}

function guiSetPlayers(players, divElement) {
	for (var i = 0; i < players.length; i++) {
		var player = players[i];
		if (player) {
			var itemDiv = document.createElement("div");
			itemDiv.appendChild(document.createTextNode(player.toString()));
			var btnKick = document.createElement("button");
			btnKick.setAttribute("style", "width:50px;height:20px;display:inline;margin:5px;");
			btnKick.setAttribute("onclick", "kickPlayer(" + player + ");");
			btnKick.appendChild(document.createTextNode("Kick"));
			itemDiv.appendChild(btnKick);
			divElement.appendChild(itemDiv);
		} else {
			console.log("Null player Alex!");
		}
	}
}

function clearChildren(elementId) {
	var node = document.getElementById(elementId);
	while (node.firstChild) {
		node.removeChild(node.firstChild);
	}
}

function onload() {
	// Clear old data
	clearChildren("ingame");
	clearChildren("queue");

	// Update data
	getPlayers(
		function(data, status, jqXHR) {
			if (status == "success") {
				var inQueue = data["players"];
				var inGame = data["in_game"];
				guiSetPlayers(inGame, document.getElementById("ingame"));
				guiSetPlayers(inQueue, document.getElementById("queue"));
			} else {
				console.log("Failure getting player data: " + status);
			}
		}
	);
}
