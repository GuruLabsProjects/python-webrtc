var WebsocketMessenger = WebsocketMessenger || {
	Models: {},
	Collections: {},
	Views: {},
}


// Conversation Model

WebsocketMessenger.Models.ChatModel = WebsocketMessenger.Models.BaseModel.extend({
	
	initialize: function(attributes, options) {
		attributes = attributes || {};
		options = options || {};
		
		// Initialize the base model
		WebsocketMessenger.Models.BaseModel.prototype.initialize.apply(this, [attributes, options, ]);
		
		// Add related models for participants and messages
		var pcollection = new WebsocketMessenger.Collections.BaseModelCollection({
			model: WebsocketMessenger.Models.BaseModel,
		});
		var mcollection = new WebsocketMessenger.Collections.BaseModelCollection({
			model: WebsocketMessenger.Models.BaseModel,
		});
		this.addRelatedCollection('participants', pcollection);
		this.addRelatedCollection('messages', mcollection);
		
		// Translate messages and users to their own related collections
		if (_.has(attributes, 'participants')) {
			// Create a participant object for each member of conversation
			_.each(attributes.participants, function(pid){ pcollection.add({ 'id' : pid }); });
			// Remove participants from the primary set of properties
			this.unset('participants');
		}
		if (_.has(attributes, 'messages')) {
			// Create a message object for each message in conversation
			_.each(attributes.messages, function(mid){ mcollection.add({ 'id' : mid, }); });
			// Remove messages from the primary set of properties
			this.unset('messages');
		}
	},

	createNewMessage: function(mtext) {
		// Add a new message to the conversation
		this.related.messages.add({ text : mtext });
	}

});