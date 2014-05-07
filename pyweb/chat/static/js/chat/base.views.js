var WebsocketMessenger = WebsocketMessenger || {
	Models: {},
	Collections: {},
	Views: {},
}


// Base - Views

WebsocketMessenger.Views.BaseView = Backbone.View.extend({
	// 	Backbone.js view used as a foundation for other WebsocketMessenger views
	//	@signal 'notification:user': Signal which can be used to notify users
	//		of events or to provide updates
	//	@signal 'notification:error': Signal which can be used to notify users
	//		of errors or issues

	odefaults: {},

	usermessage_notificationtype: 'info',
	errormessage_notificationtype: 'error',

	userMessage: function(usermessage, options) {
		options = options || {};
		_.defaults(options, { type: this.usermessage_notificationtype, });
		this.trigger('notification:user', usermessage, options);
	},

	errorMessage: function(errormessage, options) {
		options = options || {};
		_.defaults(options, { type: this.errormessage_notificationtype, });
		this.trigger('notification:error', errormessage, options);
	},

	removeView: function(options) {
		// 	Causes a view to fadeout and then removes it from the DOM. Calls the view's
		// 	"remove" function, which will deactivate listeners and event handlers.
		//	@input options (object): Options to control how the view is removed
		//	@callback afterFadeout(): Optional function which can be called after a view
		//		view has faded from the view, but before it is removed from the DOM.
		options = options || {};
		var view = this;
		_.defaults(options, {
			afterFadeout: function() { },
		});
		view.$el.fadeOut(function(){
			if (_.isFunction(options.afterFadeout)) options.afterFadeout();
			view.remove();
		});
	},

});