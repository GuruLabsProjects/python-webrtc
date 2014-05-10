var WebsocketMessenger = WebsocketMessenger || {
	Models: {},
	Collections: {},
	Views: {},
}


// Chat Manager View

WebsocketMessenger.Views.ChatManager = WebsocketMessenger.Views.BaseView.extend({
	// 	Backbone.js view used to manage the front page of the application

	// @signal 'socket:userlist': Triggered when a list of active users is received
	//		from the socket server

	user: undefined,

	url_create_conversation: undefined,

	$modalcontent: undefined,
	$conversations: undefined,
	$users: undefined,

	form_errors_selectorstring: 'small.error',

	tmpl_notification: undefined,
	tmpl_formerrors: undefined,
	tmpl_conversation: undefined,
	tmpl_messages: undefined,
	tmpl_activeuser: undefined,

	messenger: undefined,

	conversations: undefined,

	initialize: function(options) {
		options = options || {};

		// Set view options
		this.url_create_conversation = options.url_create_conversation;
		this.$modalcontent = options.modalcontent;

		this.user = options.user;

		// View HTML microtemplates
		this.tmpl_notification = options.tmpl_notification;
		this.tmpl_formerrors = options.tmpl_formerrors;
		this.tmpl_conversation = options.tmpl_conversation;
		this.tmpl_message = options.tmpl_message;
		this.tmpl_activeuser = options.tmpl_activeuser;

		// UI References
		this.$conversations = options.conversations_el;
		this.$users = options.users_el;

		if (_.isUndefined(this.$conversations))
			throw new Error('Please provide a valid conversation root element');
		if (_.isUndefined(this.$users))
			throw new Error('Please provide a valid user root element');

		// Websocket messenger and events
		this.messenger = options.messenger;
		this.listenTo(this.messenger, 'server:open', this.hideReconnectButton.bind(this));
		this.listenTo(this.messenger, 'server:message', this.socketServerMessage.bind(this));
		this.listenTo(this.messenger, 'websocket:closed', this.clearUserList.bind(this));
		this.listenTo(this.messenger, 'websocket:closed', this.showReconnectButton.bind(this));

		// Conversation Manager
		this.conversations = new WebsocketMessenger.Collections.BaseModelCollection({}, {
			modelname: 'conversations', 	// Model name
			model: WebsocketMessenger.Models.ChatModel,		// Model to use
			collectionurl: this.url_create_conversation, 	// URL for creating conversations
		});
		// Conversation manager events
		this.listenTo(this.conversations, 'add', this.initConversation.bind(this));
		// Retrieve conversations for the user
		this.conversations.fetch();

		// Active users
		this.active_users = new WebsocketMessenger.Collections.BaseModelCollection({}, {
			modelname: 'user-active',		// Model name
		});
		this.listenTo(this.active_users, 'add', this.initActiveUser.bind(this));

		// View events
		this.listenTo(this, 'socket:userlist', this.activeUserList.bind(this));

		this.websocketConnect();
	},

	events: {
		'click #btn-view-conversations' : 'viewConversationJSON',
		'click #btn-reconnect' : 'websocketConnect',
	},

	createConversation: function(umodel) {
		// Create a new conversation
		var cmodel = new WebsocketMessenger.Models.ChatModel({});
		cmodel.related.participants.add(umodel);
		if (!_.isUndefined(this.user))  cmodel.related.participants.add(this.user);
		this.conversations.add(cmodel);
	},

	initConversation: function(cmodel) {
		// Initialize a conversation model/view, render HTML, add to conversations list	
		// Add create/update url to conversation
		if (!_.isUndefined(this.url_create_conversation)) {
			cmodel.createurl = this.url_create_conversation;
			if (!_.isUndefined(cmodel.id))
				cmodel.updateurl = cmodel.createurl+cmodel.get('id')+'/';
			// Track ID changes, update URL appropriately
			cmodel.listenTo(cmodel, 'chage:id', function(){
				cmodel.updateurl = cmodel.createurl+cmodel.get('id')+'/';
			});
		}
		// Create conversation view
		var cview = new WebsocketMessenger.Views.ConversationView({
			model: cmodel,
			template: this.tmpl_conversation,
			tmpl_message: this.tmpl_message,
		});
		// Add conversation view to the conversation list
		this.$conversations.append(cview.render().$el);
		// Retrieve conversation messages
		if (cmodel.isNew()) {
			cmodel.once('change:id', function(){
				cmodel.updateurl = cmodel.createurl+cmodel.get('id')+'/';
				cmodel.getConversationMessages();
			});
			cmodel.save();
		} else { cmodel.getConversationMessages() }
	},

	socketServerMessage: function(serverdata) {
		console.log(serverdata);
		var sdata = JSON.parse(serverdata);
		// Create the active user list (from the server)
		if (sdata.opcode == 'user-activelist') {
			if (_.has(sdata, 'users'))  this.trigger('socket:userlist', sdata.users);
		}
	},

	activeUserList: function(userlist) {
		var mview = this;
		_.each(userlist, function(udata) { mview.active_users.add(udata); });
	},

	initActiveUser: function(auser) {
		var aview = new WebsocketMessenger.Views.UserView({
			model: auser,
			template: this.tmpl_activeuser,
		});
		this.$users.append(aview.render().$el);
		this.listenTo(aview, 'conversation:create', this.createConversation.bind(this));
	},

	clearUserList: function() {
		// Clear the active user list
		this.active_users.forEach(function(umodel){ umodel.trigger('destroy'); });
		this.active_users.reset();
	},

	hideReconnectButton: function() {
		this.$('#btn-reconnect').addClass('hidden');
	},

	showReconnectButton: function() {
		this.$('#btn-reconnect').removeClass('hidden');
	},

	websocketConnect: function() { this.messenger.connect(); },

});

$(document).ready(function() {
	
	// Initialize foundation and plugins
	$(document).foundation();

	// UI References
	var $apiref = $('api');
	var $userdata = $('userdata');
	var $modalref = $('#modal-content');
	var $userlist = $('#chat-user-list');
	var $conversationlist = $('#chat-conversation-list');


		// Logged in user
	var cuser = new WebsocketMessenger.Models.BaseModel({
		id: $userdata.attr('username'),
		displayname: $userdata.attr('displayname') || '',
	});

	// Compile templates
	var tmpl_notification = _.template($('#template-notification').html());
	var tmpl_formerror = _.template($('#template-formerror').html());
	var tmpl_conversation = _.template($('#template-conversation').html());
	var tmpl_message = _.template($('#template-message').html());
	var tmpl_activeuser = _.template($('#template-activeuser').html());

	// Create connection to websocket server
	var wsmessenger = new WebsocketMessenger.MessengerConnection({
		server: $apiref.attr('mserver'),
		port: $apiref.attr('mport'),
		user: cuser,
	});

	// Messenger events
	
	// Server connection opens
	wsmessenger.listenTo(wsmessenger, 'server:open', function(){
		wsmessenger.sendSocketData(JSON.stringify({
			'opcode' : 'user-identity',
			'user-identify' : cuser.toJSON() 
		}));
		wsmessenger.sendSocketData(JSON.stringify({
			'opcode' : 'user-active',
		}));
	});

	// Server message received
	wsmessenger.listenTo(wsmessenger, 'server:message', function(mdata) {
		console.log('Websocket Server Message:', mdata);
	});


	// Create the page view
	var cmanager = new WebsocketMessenger.Views.ChatManager({
		el: $('body'),			// View element. Created with existing element.
		user: cuser,			// User currently active on the page

		tmpl_notification: tmpl_notification,	// Microtemplate for user notifications
		tmpl_formerrors: tmpl_formerror,	// Microtemplate for form errors
		tmpl_conversation: tmpl_conversation, // Microtemplate for rendering conversations
		tmpl_message: tmpl_message, // Microtemplate for rendering messages
		tmpl_activeuser: tmpl_activeuser, // Microtemplate for rendering active user details
		
		modalcontent: $modalref,	// Modal content UI reference
		users_el: $userlist,		// User list UI reference
		conversations_el: $conversationlist, 	// Conversation list UI reference
		
		messenger: wsmessenger,		// Websocket connection
		url_create_conversation: $apiref.attr('conversation-create'), // API conversation endpoint
	});

});