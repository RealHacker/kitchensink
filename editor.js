
(function($) {
	$.fn.neoEditor = function(config) {
		// first add the toolbar and content-editable div
		var generateToolbar = function(config){
			var toolbarHtml = '\
				<div class="neo-editor-toolbar">\
					<span id="neo_bold_button" name="bold" class="neo-btn inactive">B</span>\
					<span id="neo_italic_button" name="italic" class="neo-btn inactive">I</span>\
					<span id="neo_underline_button" name="underline" class="neo-btn inactive">U</span>\
				</div>\
			';
			return $(toolbarHtml);
		}

		this.textStyle = {
			bold: false,
			italic: false,
			underline: false
		};
		this.btnCallbacks = {
			bold: this.clickBoldButton,
			italic: this.clickItalicButton,
			underline: this.clickUnderlineButton
		};
		
		var isEmptyRange = function(range){
			if
		};
		this.clickBoldButton = function(){
			this.textStyle.bold = !this.textStyle.bold;
			// If selected range contains text, apply new style
			
			// change the appearance of button itself
		};
		this.clickItalicButton = function(){
			this.textStyle.italic = !this.textStyle.italic;
		};
		this.clickUnderlineButton = function(){
			this.textStyle.underline = !this.textStyle.underline;			
		};

		this.initToolbar = function(){
			this.toolbarButtons = this.toolbar.children("span");
			this.toolbarButtons.each(function(btn){
				var btnName = $(btn).attr("name");
				var callback = this.btnCallbacks[btnName];
				$(btn).click(callback);				
			});	
		};

		this.toolbar = generateToolbar(config);
		this.initToolbar();
		
		this.contentElement = $("<div contenteditable='true' class='neo-editor-content'></div>");
		this.append(this.toolbar);
		this.append(this.contentElement);
		// get current selection range
		
		this._sel = null;
		this._range = null;
		this.updateSelectionRange = function(){
			this._sel = window.getSelection();
			this._range = sel.getRangeAt(0);
		};
		/*
			This function iterates each node within selected range, and call callback on the node
			The signature of callback is 
			callback(node, props, partial, offset)
			- node is the DOM node currently visiting
			- props is a dictionary of properties for the current node
			- partial is boolean, whether the node is partially contained in range
			- offset is {start: offset} for "start" node and {end: offset} for "end" node
		*/
		this.iterateOverNodesInRange = function(callback){
			var topNode = this._range.commonAncestorContainer;
			var partial = true;
			if(this._sel.containsNode(topNode, false))
				partial = false;
			this.applyCallbackOnNode(topNode, {}, partial, callback);
		};
		this.addPropsByTagName = function(tagName, props) {
			if(tagName==="b"){
				props.bold = true;
			} else if (tagName=="i") {
				props.italic = true;
			} else if (tagName === "u") {
				props.underline = true;
			}
		};
		// recursive function 
		this.applyCallbackOnNode = function(node, props, partial, callback){
			this.addPropsByTagName(node.tagName, props);
			var children = $(node).children();
			if(!partial){
				// Whole node can be handled here
				callback(node, props, false);
			} else if(children.length==0) {
				// partial leaf node
				var offset = {};
				if(node==this._range.startContainer){
					offset.start = this._range.startOffset;
				}
				if(node==this._range.endContainer){
					offset.end = this.range.endOffset;
				}
				callback(node, props, true, offset);
			} else {
				// partial high-level node
				for(var i=0;i<children.length;i++) {
					var child = children[i];
					if(!this._sel.containsNode(child, true)) continue;
					var partial = this._sel.containsNode(child, false);
					this.applyCallbackOnNode(child, props, partial, callback);
				}
			}
		};

		return this;
	};
})(jQuery);
