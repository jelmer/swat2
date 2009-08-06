window.addEvent("domready", function() {    
});

var FormSubmit = new Class({
    Implements: [Options, Events],

    options: {
        formId: ''
    },
    
    initialize: function(options) {
        this.setOptions(options);
        
        var elements = $$('a.form-submit-button');
        
        elements.each(function(el) {
            el.addEvent("click", function(ev) {
                ev = new Event(ev).preventDefault();
                
                this.changeTask(el.getProperty("href"));
                this.submitForm();
            }.bind(this));
        }.bind(this));
    },
    
    changeTask: function(link) {
        $(this.options.formId).setProperty("action", link);
    },
    
    submitForm: function() {
        $(this.options.formId).submit();
    }
});

var TabGroup = new Class({
    Implements: [Options, Events],

    options: {
        tabGroupClass: 'tab-list'
    },
    
    initialize: function(options) {
        this.setOptions(options);
        
        var tabContainers = $$('.' + this.options.tabGroupClass);
        var children = null;
        var clickedTabContent = null;

        tabContainers.each(function(el) {
            children = el.getChildren("li");
            
            if(children) {         
                children.each(function(c) {
                    clickedTabContent = $("content-" + c.getProperty("id"));
                    
                    if(clickedTabContent && Cookie.read(getCurrentUri() + "-tab")) {
                        if(Cookie.read(getCurrentUri() + "-tab") == c.getProperty("id")) {
                            c.addClass("active");
                            clickedTabContent.addClass("active");
                        } else {
                            c.removeClass("active");
                            clickedTabContent.removeClass("active");
                        }
                    }
                    
                    c.addEvent("click", function(event) {
                        event = new Event(event).preventDefault()
                        tabs.activateTab(this.getProperty("id"));
                    });
                });
            }
        });
    },
    
    activateTab: function(tabId) {
        var clickedTab = $(tabId);
        
        if(clickedTab) {
            var clickedTabContent = $("content-" + clickedTab.getProperty("id"));
            
            if(clickedTab && clickedTabContent) {
                clickedTab.addClass("active");
                clickedTabContent.addClass("active");
                
                Cookie.write(getCurrentUri() + "-tab", clickedTab.getProperty("id"), {duration: 1});
        
                var tabList = clickedTab.getParent().getChildren();
                var numTabs = tabList.length;
                var otherTab = null;
                
                for(var i = 0; i < numTabs; i++) {
                    if(tabList[i] && tabList[i].getProperty("id") != clickedTab.getProperty("id")) {
                        tabList[i].removeClass("active");
                        otherTab = $("content-" + tabList[i].getProperty("id"));
                        
                        if(otherTab) {
                            otherTab.removeClass("active");
                        }
                    }
                }
            }
        }
    }
});

/**
 *  Path Selection
 */
var PathSelector = new Class({
    Implements: [Options, Events],
    
    options: {
        request: null,
        element: '',
        copyTo: ''
    },
    
    initialize: function(options) {
        this.setOptions(options);
        this.request = new Request.HTML({
            update: this.options.element,
            onComplete: this.bindEvents
        });
    },
    
    bindEvents: function() {
        console.log("get to the binding man!");
    },
    
    get: function(url) {
        this.request.get(url);
    },
    
    add: function(path) {
        $(this.options.copyTo).value = path;
    },
    
    remove: function() {
        $(this.options.copyTo).value = "";
    }
});

var ItemList = new Class({
    Implements: [Options, Events],
    
    options: {
        request: null,
        element: '',
        copyTo: ''
    },
    
    initialize: function(options) {
        this.setOptions(options);
        this.addRemoveEvent();
        this.request = new Request.HTML({
            update: this.options.element
        });
    },
    
    addRemoveEvent: function() {
        elements = $$("a.delete-link");
        
        if(elements) {
            elements.each(function(a, i) {
                a.addEvent('click', function(ev) {
                    event = new Event(ev).stop();
                    this.options.copyTo = ev.target.getParent().getParent().getProperty("id");
                    this.remove(ev.target);
                }.bind(this));
            }.bind(this));
        }
    },
    
    effect: function(id, type) {
        var element = $(id);
        
        if(element) {
            element.set('tween', {duration: 100});
            
            if(type == "add") {
                element.tween('opacity', 0, 1);
            } else {
                element.tween('opacity', 1, 0);
            }
        }
    },
    
    get: function(url) {
        this.request.get(url);
    },
    
    add: function(name, type) {
        if(name.length == 0) {
            return;
        }

        if(type == "g") {
            name = "@" + name;
        }

        if(this.exists(name)) {
            alert("Already Exists!");
            return;
        }
        
        var numElements = $(this.options.copyTo).getChildren().length;
        var newElementId = 'delete-' + this.options.copyTo + '-' + (numElements + 1);
        
        var newLi = new Element('li');
        var newAnchor = new Element('a', {text:name, class:"delete-link", id:newElementId, title:"Remove this item from the list", href:"#"});

        newAnchor.addEvent('click', function(ev) {
            event = new Event(ev).preventDefault();
            this.options.copyTo = ev.target.getParent().getParent().getProperty("id");
            this.remove(ev.target);
        }.bind(this));
        
        newAnchor.injectInside(newLi);
        newLi.injectInside($(this.options.copyTo));
        
        this.effect(newElementId, "add");
        this.updateHiddenList("add");
    },
    
    addManual: function(from, to) {
        var items = null;
        var numItems = 0;
        
        from = $(from);
        this.options.copyTo = to;
        
        if(from) {
            items = from.value.split(',');
            numItems = items.length;

            for(var i = 0; i < numItems; i++) {
                this.add(items[i].trim());
            }
            
            from.value = "";
        }
    },
    
    remove: function(id, forReal) {
        var element = $(id);
        
        if(element) {
            this.effect(id, "remove");
            element.getParent().dispose();
            this.updateHiddenList("rem")
        }
    },
    
    exists: function(name) {
        var elements = $(this.options.copyTo).getChildren();
        var n = elements.length;
        var a = null;
        
        var exists = false;
        
        for(var i = 0; i < n; i++) {
            a = elements[i].getElement("a");
            
            if(a.get('text') == name) {
                exists = true;
                break;
            }
        }
        
        return exists;
    },
    
    updateHiddenList: function(operation) {
        var area = $(this.options.copyTo + "-textbox");
        var list = $(this.options.copyTo);
        var elements = null;

        if(area && list) {
            links = list.getElements("li a");
            area.setProperty("value", "");
            
            links.each(function(link, i) {
                console.log(link);
                area.setProperty("value", area.getProperty("value") + "," + link.get("text"));
            });

            area.setProperty("value", area.getProperty("value").substring(1));
        }
    }
});

function getCurrentUri() {
    var uri = new URI(window.location);
    return uri.toRelative();
}

function selectShareRow(checkbox) {
    var rowId = "";
    
    if(checkbox) {
        rowId = checkbox.id.substring(6);
        if(checkbox.checked) {
            $(rowId).addClass("selected-row");
        } else {
            $(rowId).removeClass("selected-row");
        }
    }
}

function clickableRow(url) {
    window.location = url;
}

function calcPermissions(base, copyTo) {
    var owner = $(base + "-owner");
    var group = $(base + "-group");
    var world = $(base + "-world");
    var target = $(copyTo);
    
    if(owner && group && world && copyTo) {
        target.setProperty("value", "0" +
                                owner.getProperty("value") +
                                group.getProperty("value") +
                                world.getProperty("value") + "L");
    }
}

function checkAllRows(parent, base) {
    var checkboxes = $$("input[id^=" + base + "]");
    var op = parent.checked ? "check" : "uncheck";
    
    if(checkboxes) {
        checkboxes.each(function(c) {
            if(op == "check") {
                c.checked = true;
            } else {
                c.checked = false;
            }
            
            selectShareRow(c);
        });
    }
}

var Popup = new Class({
    Implements: [Options, Events],
    
    options: {
        url: "",
        window: "",
        trigger: null
    },
    
    trigger: null,
    copyTo: null,
    isActive: false,
    htmlRequest: null,
    title: "",
    
    initialize: function(options) {
        this.setOptions(options);
        
        if(this.options.trigger) {
            this.parseUrl();
            this.setup();
        }
    },
    
    setup: function() {
        if(this.options.trigger) {
            /**
             *
             */
            var mainWindow = new Element('div', {opacity: 0, id: this.options.window, class:'popup-main-window round-2px'});
            mainWindow.injectInside(document.body);
            
            var titleBar = new Element('div', {'id': this.options.window + "-title-bar", 'class': 'popup-main-window-title-bar'});
            titleBar.injectInside(mainWindow);
            
            var titleBarTitle = new Element('span', {'id': this.options.window + "-title", class:'popup-main-window-title'});
            var titleBarClose = new Element('a', {'text': 'close', 'id': this.options.window + "-close", class:'popup-main-window-close'});
            
            titleBarTitle.injectInside(titleBar);
            titleBarClose.injectInside(titleBar);
            
            //var titleBarCloseLink = new Element('a', {'href': '#', 'id': this.options.window + "-close-link"});
            //titleBarCloseLink.injectInside(titleBarClose);
            
            var mainWindowContent = new Element('div', {'id': this.options.window + "-content", class:'popup-main-window-content'});
            mainWindowContent.injectInside(mainWindow);
            
            /**
             *
             */
            titleBarTitle.set("text", this.options.trigger.getProperty("title") || this.options.trigger.getProperty("name") || "");
            titleBarClose.addEvent('click', this.hide.bind(this));
            mainWindow.makeDraggable({handle: titleBar.getProperty("id")});
            
            this.options.trigger.addEvent("click", this.makeRequest.bind(this));
            this.htmlRequest = new Request.HTML({method: 'get', update: mainWindowContent.getProperty("id"), onComplete: this.show.bind(this)})
            
            //console.log(this.htmlRequest);
            
            this.options.window = mainWindow;
            //tb = $(this.options.window);
            
            //tb.setOpacity(0);
            //tb.addClass("round-2px");
            
            //tb.innerHTML += "<div id='" + this.options.window + "-title'><div id='TB_ajaxWindowTitle'></div><div id='TB_closeAjaxWindow'><a href='#' id='TB_closeWindowButton'>close</a></div></div><div id='TB_ajaxContent'></div>";
            //$("TB_closeWindowButton").onclick = TB_remove;
            
            //tb.makeDraggable({handle:'TB_title'})
        }
    },
    
    bind: function() {
        
    },
    
    show: function() {
        if(!this.isActive) {
            console.log(this.options.window);
            this.options.window.set('tween', {duration: 150});
            this.options.window.fade("in");
        }
    },
    
    makeRequest: function(ev) {
        new Event(ev).preventDefault();
        
        if(!this.isActive) {
            this.htmlRequest.get(this.options.url);
        }
    },
    
    hide: function() {
        console.log("hiding");
        
        
    },
    
    position: function() {
    },
    
    parseUrl: function() {
        var queryString = this.options.url.match(/\?(.+)/)[1];
        var params = queryString.parseQueryString();
    
        var element = $(params['copyto']);
        this.copyTo = element ? element : null;
    }
});

var Path = new Class({
    Extends: Popup,
    Implements: Options,
    
    options: {
    },
    
    initialize: function(id, element) {
        var href = element.getProperty("href");
        element.setProperty("id", id);
        
        this.parent({trigger: element, window: id + "-window", url: href});
    }
});    
