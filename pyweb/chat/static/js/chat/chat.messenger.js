// Allows for sending and receiving of real-time messages
// Requires jQuery, Backbone.js, jQuery


// Messenger Connection
var WebsocketMessenger = WebsocketMessenger || {
	Models: {},
	Collections: {},
	Views: {},
}

WebsocketMessenger.MessengerConnection = Backbone.View.extend({
	
	server: undefined,
	port: undefined,
	
	connection: undefined,

	initialize: function(options) {
		options = options || {};
		this.server = options.server;
		this.port = options.port;
	},
	connect: function() {
		this.connection = new WebSocket('ws://'+this.server+':'+this.port+'/messages/');
		this.connection.onerror = this.socketError.bind(this);
		this.connection.onopen = this.socketConnectionOpen.bind(this);
		this.connection.onmessage = this.socketConnectionMessage.bind(this);
		this.connection.onclose = this.socketConnectionClose.bind(this);
	},
	socketError: function(event) {
		console.log(error);
	},
	socketConnectionOpen: function(event) {
		console.log('Connected to web socket server');
	},
	socketConnectionMessage: function(event) {
		console.log('Message received from socket server', event.data);
		this.trigger('server:message', event.data);
	},
	socketConnectionClose: function(event) {
		console.log('Connection to socket server terminated');
	},
});