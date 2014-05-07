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

WebsocketMessenger.display_form_errors = function(fview, ferrors, etemplate) {
	// 	Add form errors to a view
	// 	@input fview: View which the errors should be added to
	//	@input ferrors (JavaScript object): List of errors that should be added to the view.
	//		Errors should be organized into lists and should be indexed to the fieldname.
	//		Example: { 
	//			'username' : ['This field is required', ],
	//			'password' : ['This field is required', 'Passwords must be at least characters long']
	//		}
	//	@input etemplate (underscore JavaScript microtemplate): Template function which should be used
	//		to render the errors to HTML. Should accept a object with form {'msg' : error_message }.

	ferrors = ferrors || {};
	if (!_.isFunction(etemplate)) throw new Error('The error template must be a function');
	_.each(ferrors, function(elist, fname){
		_.each(elist, function(emessage){
			var etext = etemplate({ msg : emessage });
			fview.$el.find('[name='+fname+']').after(etext);
		});
	});
}

WebsocketMessenger.remove_form_errors = function(fview, eselector) {
	// Remove all error messages from a view
	// @input fview: View from which the errors should be removed from
	// @input eselector: Selector string which should be used for removing errors from DOM
	fview.$el.find(eselector).remove();
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
	//	@signal 'form:submit:success' params=(JSON object of server response): Triggered
	//		when the form has been submitted successfully

	form_fieldnames: [],
	form_trackchanges: true,
	form_loaddata: true,

	errormessage_save: "Unable to save changes to the model",

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
			mview.model.attributes[fieldname] = fcontrol.val();
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

	cancel: function(event) {
		event.preventDefault();
		this.trigger('form:submit:cancel');
	},

	submitForm: function(event) {
		// Submit form changes to the web server
		event.preventDefault();
		var mview = this;
		this.trigger('form:submit');
		var mchanges = this.model.changedAttributes() || {};
		this.model.save(mchanges, {
			error: function(model, xhr, options) {
				// Error callback: trigger form:submit:errors with response from server
				if (_.has(xhr.responseJSON, 'error'))
					mview.trigger('form:submit:errors', xhr.responseJSON.error);
				// Notify user that the form could not be submitted
				mview.errorMessage(mview.errormessage_save);
			},
			success: function(model, response, options) {
				// Success callback
				// Update model instance with update URL
				if (_.has(response, 'href-update')) mview.model.updateurl = response['href-update'];
				// Update model isntance with ID generated from the server
				if (_.has(response, 'id')) mview.model.set('id', response.id);
				mview.trigger('form:submit:success', response);
			}
		});
	},

});