var WebsocketMessenger = WebsocketMessenger || {
	Models: {},
	Collections: {},
	Views: {},
}


// Chat Manager View

WebsocketMessenger.Views.ChatManager = WebsocketMessenger.Views.BaseView.extend({
	// 	Backbone.js view used to manage the front page of the application

	url_create_conversation: undefined,

	$modalcontent: undefined,
	$conversations: undefined,
	$users: undefined,

	form_errors_selectorstring: 'small.error',

	tmpl_notification: undefined,
	tmpl_formerrors: undefined,
	tmpl_conversation: undefined,
	tmpl_messages: undefined,

	messenger: undefined,

	conversations: undefined,

	initialize: function(options) {
		options = options || {};

		// Set view options
		this.url_create_conversation = options.url_create_conversation;
		this.$modalcontent = options.modalcontent;

		// View HTML microtemplates
		this.tmpl_notification = options.tmpl_notification;
		this.tmpl_formerrors = options.tmpl_formerrors;
		this.tmpl_conversation = options.tmpl_conversation;
		this.tmpl_message = options.tmpl_message;

		// UI References
		this.$conversations = options.conversations_el;
		this.$users = options.users_el;

		if (_.isUndefined(this.$conversations))
			throw new Error('Please provide a valid conversation root element');
		if (_.isUndefined(this.$users))
			throw new Error('Please provide a valid user root element');

		// Websocket messenger
		this.messenger = options.messenger;
		this.messenger.connect();

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
	},

	events: {
		'click #btn-view-conversations' : 'viewConversationJSON',
	},

	createConversation: function() {
		// Create a new conversation
		console.log('Create a new conversation');
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
		var cview = new WebsocketMessenger.Views.ConversationView({
			model: cmodel,
			template: this.tmpl_conversation,
			tmpl_message: this.tmpl_message,
		});
		this.$conversations.append(cview.render().$el);
	},

	viewConversationJSON: function(event) {
		event.preventDefault();
		console.log(JSON.stringify(this.conversations.toJSON()));
	},




});

$(document).ready(function() {
	
	// Initialize foundation and plugins
	$(document).foundation();

	// UI References
	var $apiref = $('api');
	var $modalref = $('#modal-content');
	var $userlist = $('#chat-user-list');
	var $conversationlist = $('#chat-conversation-list');

	// Compile templates
	var tmpl_notification = _.template($('#template-notification').html());
	var tmpl_formerror = _.template($('#template-formerror').html());
	var tmpl_conversation = _.template($('#template-conversation').html());
	var tmpl_message = _.template($('#template-message').html());

	// Create connection to websocket server
	var wsmessenger = new WebsocketMessenger.MessengerConnection({
		server: $apiref.attr('mserver'),
		port: $apiref.attr('mport'),
	});

	wsmessenger.listenTo(wsmessenger, 'server:message', function(mdata) {
		console.log('Server Message:' + mdata);
	});

	// Create the page view
	var cmanager = new WebsocketMessenger.Views.ChatManager({
		el: $('body'),			// View element. Created with existing element.

		tmpl_notification: tmpl_notification,	// Microtemplate for user notifications
		tmpl_formerrors: tmpl_formerror,	// Microtemplate for form errors
		tmpl_conversation: tmpl_conversation, // Microtemplate for rendering conversations
		tmpl_message: tmpl_message, // Microtemplate for rendering messages
		
		modalcontent: $modalref,	// Modal content UI reference
		users_el: $userlist,		// User list UI reference
		conversations_el: $conversationlist, 	// Conversation list UI reference
		
		messenger: wsmessenger,		// Websocket connection
		url_create_conversation: $apiref.attr('conversation-create'), // API conversation endpoint
	});

});