var WebsocketMessenger = WebsocketMessenger || {
	Models: {},
	Collections: {},
	Views: {},
}

// Helper data structures
WebsocketMessenger._positive = ['true', 'positive', 'yes', '1', 'yup', 'y', 't']

// Helper Functions
WebsocketMessenger.remove_newlines = function(rstring) {
	// 	Remove new lines from the input string
	// 	@input rstring: String from which to remove all newline characters
	return rstring.replace(/(\r\n|\n|\r)/gm,"");
}

WebsocketMessenger.model_fieldnames = function(imodel) {
	// 	Return an array of field names from a model instance
	//	@input imodel: Model from which to retrieve the field names
	return _.without(_.keys(imodel.toJSON()), 'id', 'cid');
}

WebsocketMessenger.str2bool = function(istring) {
	// Convert the input string value to a boolean
	return _.contains(WebsocketMessenger._positive, istring.toLowerCase());
}

WebsocketMessenger.csrfSafeMethod = function(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

// Setup Ajax Requests to add the CSRF token to the headers
$.ajaxSetup({
    crossDomain: false, 
    beforeSend: function(xhr, settings) {
    	var csrftoken = $.cookie('csrftoken');
        if (!WebsocketMessenger.csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

// Convenience method for setting cookies
function setPrefCookie(cookie_name, cookie_value) {
    var edate = new Date();
    edate.setTime(edate.getTime() + (30*24*60*60*1000)); // Expire in 30 days
    $.cookie(cookie_name, cookie_value, {expires: edate});
}


WebsocketMessenger.Models.BaseModel = Backbone.Model.extend({
	// 	Base model from which all other WebsocketMessenger models inherit

	//	@property createurl: URL which should be used when first creating objects
	// 	@property updateurl: URL which should be used when updating an 
	//		existing instance of an object
	//	@property related (default={}): JS object which can be used to store
	//		named collections of objects. When the model's toJSON method is called,
	//		all objects in the collection are serialized to a JSON array
	//	@method ovveride toJSON: Serializes model data to JSON. Includes of the IDs
	//		of collections that have been added to related

	related: undefined,
	createurl: undefined,
	updateurl: undefined,
	
	initialize: function(attributes, options) {
		options = options || {};
		_.defaults(options, { related: {} });
		var bmodel = this;
		// Default options
		this.related = {};
		this.createurl = options.createurl;
		this.updateurl = options.updateurl;
		// Add related model collections
		_.each(options.related, function(rcollection, rname){
			bmodel.addRelatedCollection(rname, rcollection);
		});
		// Model events
		bmodel.listenTo(bmodel, 'sync', bmodel.serverResponse.bind(bmodel));
	},

	addCollection: function(group_name, cname, collection) {
		// 	Add a model collection to a named group object
		// 	@input group_name (string): Group to which the named collection should be added.
		//		The model must have a property name which matches the group name.
		//		Otherwise an error will be thrown.
		//	@input cname (string): Name of the collection to be added to the group
		//		object. Collections are indexed by the collection name.
		//	@input collection (Backbone.Collection): Collection object to be added to the group
		var bmodel = this;
		if (!_.has(this, group_name)) throw new Error('addCollection(): The model does not have '
			+ 'a "' + group_name + '" property ');
		if (!_.isObject(this[group_name])) throw new Error('addCollection(): ' + group_name 
			+ 'is not a JavaScript object')
		this[group_name][cname] = collection;
		this.listenTo(collection, 'add', function(rmodel){
			bmodel.trigger('related:model:add', rmodel);
			bmodel.trigger('related:collection:'+cname+':model:add', rmodel);
			bmodel.trigger('related:collection:'+cname+':change');
			bmodel.trigger('change');
			bmodel.trigger('change:related');
		});
		this.listenTo(collection, 'remove', function(rmodel) {
			bmodel.trigger('related:model:remove', rmodel);
			bmodel.trigger('related:collection:'+cname+':model:remove', rmodel);
			bmodel.trigger('related:collection:'+cname+':change');
			bmodel.trigger('change');
			bmodel.trigger('change:related');
		});
	},

	addRelatedCollection: function(cname, collection) {
		// 	Add related collection to the model
		//	@signal: When new items are added to the collection, two events are triggered:
		//		"relate:model:add" and "related:collection:{{ collection-name }}:model:add"
		//	@signal: When items are removed from the collection, two events are triggered:
		//		"related:model:remove" and "related:collection:{{ collection-name }}:model:remove"
		this.addCollection('related', cname, collection);
	},

	toJSON: function(options) {
		options = options || {};
		// Retrieve model base properties
		var mjson = Backbone.Model.prototype.toJSON.apply(this, [options,]);
		// Add Backbone.js cid to new models
		if (this.isNew()) mjson.cid = this.cid;
		// Add ID objects from related models
		_.each(this.related, function(rcollection, rname){
			mjson[rname] = _.pluck(rcollection.filter(function(model){
				return model.get('id') !== undefined;
			}), 'id')
		});
		return mjson;
	},

	url: function() {
		if (this.isNew()) {
			if (_.isUndefined(this.createurl)) 
				throw new Error('Unable to provide url, no create url defined');
			return(this.createurl);
		}
		return(this.updateurl);
	},

	serverResponse: function(model, response, options) {
		// Process a successful server sync
		// Retrieves the model ID, update URL, and other important information
		if (_.has(response, 'id')) model.set('id', response.id);
		if (_.has(response, 'href-update')) model.updateurl = reponse['href-update'];
	},

});

WebsocketMessenger.Collections.BaseModelCollection = Backbone.Collection.extend({
	// 	Base collection from which all other WebsocketMessenger collections inherit

	// 	@property modelname (default=undefined): Name of the collection model.
	//		When added to the model's related object, the modelname is frequently
	//		used as the key. The modelname can be passed as a parameter in the options

	collectionurl: undefined,

	modelname: undefined,
	model: WebsocketMessenger.Models.BaseModel,
	initialize: function(initmodels, options) {
		options = options || {};
		_.defaults(options, { model : this.model });
		this.model = options.model;
		this.modelname = options.modelname;
		this.collectionurl = options.collectionurl;
	},
	url: function() { 
		return(this.collectionurl);
	},
});