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

	form_errors_selectorstring: 'small.error',

	tmpl_notification: undefined,
	tmp_formerrors: undefined,

	initialize: function(options) {
		options = options || {};

		// Set view options
		this.url_create_conversation = options.url_create_conversation;
		this.$modalcontent = options.modalcontent;

		// View HTML microtemplates
		this.tmpl_notification = options.tmpl_notification;
		this.tmpl_formerrors = options.tmpl_formerrors;
	},

	events: {
		'click #btn-create-conversation' : "createConversation",
	},

	createConversation: function() {
		// Create a new conversation
	},


});

$(document).ready(function() {
	
	// Initialize foundation and plugins
	$(document).foundation();

	// UI References
	var $apiref = $('api');
	var $modalref = $('#modal-content');

	// Compile templates
	var tmpl_notification = _.template($('#template-notification').html());
	var tmpl_formerror = _.template($('#template-formerror').html());

	// Create the page view
	var cmanager = new WebsocketMessenger.Views.ChatManager({
		el: $('body'),
		tmpl_notification: tmpl_notification,
		tmpl_formerrors: tmpl_formerror,
		modalcontent: $modalref,
	});

});