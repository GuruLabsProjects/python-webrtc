var WebsocketMessenger = WebsocketMessenger || {
	Models: {},
	Collections: {},
	Views: {},
}


// Conversation View

WebsocketMessenger.Views.ConversationView = WebsocketMessenger.Views.BaseModelView.extend({

	template: undefined,
	tmpl_message: undefined,
	$participants: undefined,
	$messages: undefined,
	$messagetext: undefined,	

	initialize: function(options) {
		options = options || {};
		this.template = options.template;
		this.tmpl_message = options.tmpl_message;

		// View events
		this.listenTo(this.model, 'destroy', this.removeView.bind(this));
		this.listenTo(this.model, 'related:collection:messages:model:add', 
			this.initMessage.bind(this));
		this.listenTo(this.model, 'related:collection:messages:change',
			this.updatePlaceholderMessage.bind(this))
	},

	events: {
		'click .conversation-controls a.remove-conversation' : 'removeConversation',
		'click .btn-send-message' : 'sendMessageButtonClick',
	},

	render: function() {
		// Render the view template
		if (!_.isFunction(this.template))
			throw new Error('No template function provided for the view');
		this.$el.html(this.template(this.model.toJSON()));
		this.initUserInterface();
		return this;
	},

	sendMessage: function() {
		// Create a new message, save to the server
		if (_.isUndefined(this.$messagetext))
			throw new Error('Unable to send message, initialize view UI first');
		this.model.createNewMessage(this.$messagetext.val());
		this.$messagetext.val('');
	},

	initMessage: function(cmessage) {
		// Initialize message model/view, render message HTML, add to message list
		// Add create message/update url to message
		if (!_.isUndefined(this.model.updateurl)) {
			cmessage.createurl = this.model.updateurl+'message/';
			if (!_.isUndefined(cmessage.id))
				cmessage.updateurl = cmessage.createurl+cmessage.get('id')+'/';
			// Track changes to ID and modify updateurl
			cmessage.listenTo(cmessage, 'change:id', function(){
				cmessage.updateurl = cmessage.createurl+cmessage.get('id')+'/';
			});
		}
		// Save message if new
		if (cmessage.isNew()) cmessage.save();
		// Create message view
		var mview = new WebsocketMessenger.Views.MessageView({
			model: cmessage,
			template: this.tmpl_message,
		});
		this.$messages.append(mview.render().$el);
	},

	initUserInterface: function() {
		this.$participants = this.$('.conversation-participants');
		this.$messages = this.$('.conversation-messages');
		this.$messagetext = this.$('input.conversation-message-input');
	},

	removeConversation: function(event) {
		event.preventDefault();
		this.model.destroy();
	},

	sendMessageButtonClick: function(event) {
		event.preventDefault();
		this.sendMessage();
	},

	updatePlaceholderMessage: function(event) {
		if (this.$('.message-text').length > 0) this.$('.placeholder').hide();
		else this.$('.placeholder').show();
	},
});

WebsocketMessenger.Views.MessageView = WebsocketMessenger.Views.BaseModelView.extend({

	template: undefined,

	initialize: function(options) {
		options = options || {};
		this.template = options.template;
	}, 

	render: function() {
		// Render the view template
		if (!_.isFunction(this.template))
			throw new Error('No template function provided to the view');
		this.$el.html(this.template(this.model.toJSON()));
		return this;
	},

});


WebsocketMessenger.Views.UserView = WebsocketMessenger.Views.BaseModelView.extend({

	template: undefined,
	initialize: function(options) {
		options = options || {};
		this.template = options.template;
		this.listenTo(this.model, 'destroy', this.removeView.bind(this));
	},

	render: function() {
		// Render the view templates
		if (!_.isFunction(this.template))
			throw new Error('No template function provided to the view');
		this.$el.html(this.template(this.model.toJSON()));
		return this;
	},
});