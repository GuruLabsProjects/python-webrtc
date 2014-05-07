var WebsocketMessenger = WebsocketMessenger || {
	Models: {},
	Collections: {},
	Views: {},
}


// Helper Functions
WebsocketMessenger.form_fieldnames = function(mform) {
	// 	Return an array of fieldnames from a form. Looks for inputs, text areas, and button elements
	// 	@input mform (jQuery element reference): The form (or form fieldset) that should be
	//		searched for form elements. Only children of "mform" will be searched
	var fnames = []
	mform.find(':input').each(function(){
		var control = $(this);
		if (!_.isUndefined(control.attr('name'))) fnames.push(control.attr('name'));
	});
	return fnames;
}


// Base - Views

WebsocketMessenger.Views.BaseView = Backbone.View.extend({
	// 	Backbone.js view used as a foundation for other WebsocketMessenger views

	//	@signal 'notification:user': Signal which can be used to notify users
	//		of events or to provide updates
	//	@signal 'notification:error': Signal which can be used to notify users
	//		of errors or issues

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

});

WebsocketMessenger.Views.BaseModelView = WebsocketMessenger.Views.BaseView.extend({
	// 	Backbone.js view used as a foundation for views associated with models.
	// 	Inherits from BaseView.

	removeView: function(options) {
		// 	Causes a view to fadeout and then removes it from the DOM. Calls the view's
		// 	"remove" function, which will deactivate listeners and event handlers.
		//	@input options (object): Options to control how the view is removed
		//	@callback afterFadeout(): Optional function which can be called after a view
		//		view has faded from the view, but before it is removed from the DOM.
		
		options = options || {};
		var view = this;
		_.defaults(options, { afterFadeout: function() { }, });
		view.$el.fadeOut(function(){
			if (_.isFunction(options.afterFadeout)) options.afterFadeout();
			view.remove();
		});
	},
})


WebsocketMessenger.Views.FormView = WebsocketMessenger.Views.BaseModelView.extend({
	// Backbone.js view which can be used to load form data into a Backbone.js model

	// 	@property form_fieldnames (default=model field names): Names of fields from
	//		which form data should be copied into the model
	//	@property form_trackchanges (default=true): Preference which controls whether 
	//		the view should track changes to form field inputs
	//	@property form_loaddata (default=true): Preference which controls whether 
	//		the view should load data from the form

	// 	@signal 'form:submit:cancel': Triggered when a form submission has been canceled
	// 	@signal 'form:submit' : Triggered when a form has been submitted
	// 	@signal 'form:submit:errors' params=(JSON object of errors): Triggered when an error
	//		was found when trying to save data to the server

	form_fieldnames: [],
	form_trackchanges: true,
	form_loaddata: true,

	initialize: function(options) {
		options = options || {};
		var mview = this;
		// Set view defaults
		_.defaults(options, { 
			form_fieldnames: WebsocketMessenger.model_fieldnames(mview.model),
			form_trackchanges: mview.form_trackchanges,
			form_loaddata: mview.form_loaddata,
		});
		this.form_trackchanges = options.form_trackchanges;
		this.form_loaddata = options.form_loaddata;
		this.form_fieldnames = options.form_fieldnames;
		// Load form data
		if (this.form_loaddata) this.loadFormData();
	},

	loadFormData: function() {
		// Copy form field data to the model.
		var mview = this;
		_.each(mview.form_fieldnames, function(fieldname){
			var fcontrol = mview.$('[name='+fieldname+']'); // Retrieve HTML control
			mview.model.attributes[fieldname] = fcontrol.val()
			if (mview.form_trackchanges) mview.trackFormChange(fieldname, fcontrol); // Track field changes
		});
	},

	trackFormChange: function(fieldname, fcontrol) {
		// Track form field changes
		// @input fieldname (string): Model field name to which changes should be written
		// @input fcontrol (jQuery element reference): Form field which should be watched for changes
		var mview = this;
		fcontrol.on('change', function(event){ mview.model.set(fieldname, fcontrol.val()); });
	},

	events: {
		'click .form-cancel' : 'cancel',
		'click .form-submit' : 'submitForm',
	},

	cancel: function() {
		this.trigger('form:submit:cancel');
	},

	submitForm: function() {
		this.trigger('form:submit');
		console.log(this.model.toJSON());
	},

});