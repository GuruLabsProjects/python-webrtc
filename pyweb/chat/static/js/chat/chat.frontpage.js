// FrontPage Manager View
var WebsocketMessenger = WebsocketMessenger || {
	Models: {},
	Collections: {},
	Views: {},
}

WebsocketMessenger.Views.FrontPageView = WebsocketMessenger.Views.BaseView.extend({
	// 	Backbone.js view used to manage the front page of the application

	// 	@signal 'user:form:create:retrieved' args=(request data):
	//		Signal fired after the view has successfully retrieved an HTML 
	// 		form that can be used to create user accounts for the site.
	//	@signal 'user:form:create:init' args=(user model, create user form view):
	//		Signal fired after a create user form has been initialized.
	//		The user model and view are passed as input arguments for the signal.

	url_form_createuser: undefined,
	$modalcontent: undefined,
	tmpl_notification: undefined,

	initialize: function(options) {
		options = options || {};
		var mview = this;
		// Set view default options
		this.url_form_createuser = options.url_form_createuser;
		this.$modalcontent = options.modalcontent;
		// View HTML microtemplates
		this.tmpl_notification = options.tmpl_notification;
		// Set internal view signals/handlers
		this.listenTo(this, 'user:form:create:retrieved', this.initCreateUserForm.bind(this));
	},

	events: {
		'click #btn-create-account' : 'getCreateUserForm',
	},

	checkModalContentElement: function() {
		if (_.isUndefined(this.$modalcontent))
			throw new Error(
				'Please provide a reference to the element which should be used '
				+ 'for modal content');
	},

	getCreateUserForm: function() {
		// 	Retrieve the create user form from the web server
		// 	This method provides an example of how a Backbone view can wrap
		// 	a JavaScript asset and make it easier to work with. Simple callbacks
		// 	can be provided which trigger view signals, allowing other internal 
		// 	view methods to respond as well as external listeners that may be 
		// 	interested in responding to events (such as if the view fails to
		// 	retrieve the form).
		var mview = this;
		if (_.isUndefined(this.url_form_createuser))
			throw new Error('No URL for retrieving the create-user form was provided');
		this.checkModalContentElement();
		this.$modalcontent.foundation('reveal', 'open', {
			url: mview.url_form_createuser,
			success: function(data) {
				mview.$modalcontent.one("opened", function(){
					mview.trigger('user:form:create:retrieved', data);
				});
			},
			error: function() {
				var emessage = 'Unable to retrieve create user form';
				if (_.isFunction(mview.tmpl_notification)) {
					emessage = mview.tmpl_notification({ msg : emessage });
				}
				mview.errorMessage(emessage);
			}, 
		});
	}, 

	initCreateUserForm: function(rdata) {
		// Initialize the user form retrieved by the view
		var mview = this;
		this.checkModalContentElement();
		var umodel = new WebsocketMessenger.Models.BaseModel({});
		var uview = new WebsocketMessenger.Views.FormView({
			el: this.$modalcontent,
			model: umodel,
			form_fieldnames: WebsocketMessenger.form_fieldnames(this.$modalcontent),
		});
		// Add event handerls for form submission events
		uview.listenTo(uview, 'form:submit:cancel', function(){
			mview.$modalcontent.foundation('reveal', 'close');
		});
		mview.trigger('user:form:create:init', umodel, uview);
	}

});

$(document).ready(function(){
	
	// Initialize foundation and plugins
	$(document).foundation();

	// Retrieve page api reference
	var apiref = $('api');
	var modalref = $('#modal-content');

	// Compile HTML Templates for the Page
	var tmpl_notification = _.template($('#template-notification').html())
	
	// Create a page view
	var fpview = new WebsocketMessenger.Views.FrontPageView({
		el: $('body'),
		url_form_createuser: apiref.attr('user-create'),
		tmpl_notification: tmpl_notification,
		modalcontent: modalref,
	});
});