//jQuery Translate plugin and related components

/*! 
 * jQuery Translate plugin 
 * 
 * Version: null
 * 
 * http://code.google.com/p/jquery-translate/
 * 
 * Copyright (c) 2009 Balazs Endresz (balazs.endresz@gmail.com)
 * Dual licensed under the MIT and GPL licenses.
 * 
 * This plugin uses the 'Google AJAX Language API' (http://code.google.com/apis/ajaxlanguage/)
 * You can read the terms of use at http://code.google.com/apis/ajaxlanguage/terms.html
 * 
 */
;(function($){

function $function(){}

var True = true, False = false, undefined, replace = "".replace,
    Str = String, Fn = Function, Obj = Object,
    GL, GLL, toLangCode, inverseLanguages = {},
    loading, readyList = [], appid,
    defaults = {
        from: "",
        to: "",
        start: $function,
        error: $function,
        each: $function,
        complete: $function,
        onTimeout: $function,
        timeout: 0,
        
        stripComments: True,
        stripWhitespace: True,
        stripScripts: True,
        separators: /\.\?\!;:/,
        limit: 1750,
        

        walk: True,
        returnAll: False,
        replace: True,
        rebind: True,
        data: True,
        setLangAttr: False,
        subject: True,
        not: "",
        altAndVal:True,
        async: False,
        toggle: False,
        fromOriginal: True,
        
        parallel: false,
        trim: true,
        alwaysReplace: false
        //,response: $function
        
    };


function google_loaded(){
    $.translate.GL = GL = google.language;
    $.translate.GLL = GLL = GL.Languages;

    loaded();
}

function ms_loaded(languageCodes, languageNames){
    GLL = {};
    for(var i = 0; i < languageCodes.length; i++){
        GLL[languageNames[i].toUpperCase()] = languageCodes[i];
    }

    //$.translate.GL = GL = google.language;
    $.translate.GLL = GLL; // = GL.Languages;

    loaded();
}

function loaded(){
    toLangCode = $.translate.toLanguageCode;
    
    $.each(GLL, function(l, lc){
        inverseLanguages[ lc.toUpperCase() ] = l;
    });
    
    $.translate.isReady = True;
    var fn;
    while((fn = readyList.shift())) fn();
}

function filter(obj, fn){
    var newObj = {};
    $.each(obj, function(lang, langCode){
        if( fn(langCode, lang) === True) newObj[ lang ] = langCode;
    });
    return newObj;
}

function bind(fn, thisObj, args){
    return function(){
        return fn.apply(thisObj === True ? arguments[0] : thisObj, args || arguments);
    };
}

function isSet(e){
    return e !== undefined;
}

function validate(_args, overload, error){
    var matched, obj = {}, args = $.grep(_args, isSet);
    
    $.each(overload, function(_, el){
        var matches = $.grep(el[0], function(e, i){
                return isSet(args[i]) && args[i].constructor === e;
            }).length;
        if(matches === args.length && matches === el[0].length && (matched = True)){
            $.each(el[1], function(i, prop){
                obj[prop] = args[i];
            });
            return False;
        }
    });
    //TODO
    if(!matched) throw error;
    return obj;
}


function getOpt(args0, _defaults){
    //args0=[].slice.call(args0, 0)
    var args = validate(args0 , $.translate.overload, "jQuery.translate: Invalid arguments" ),
        o = args.options || {};
    delete args.options;
    o = $.extend({}, defaults, _defaults, $.extend(o, args));
    
    if(o.fromOriginal) o.toggle = True;
    if(o.toggle) o.data = True;
    if(o.async === True) o.async = 2;
    if(o.alwaysReplace === true){ //see issue #58
        o.toggle = false;
        o.fromOriginal = false;
    }

    return o;
}


function T(){
    //copy over static methods during each instantiation
    //for backward compatibility and access inside callback functions
    this.extend($.translate);
    delete this.defaults;
    delete this.fn;
}

T.prototype = {
    version: "null",
    
    _init: function(t, o){
        var separator = o.separators.source || o.separators,
            isString = this.isString = typeof t === "string",
            lastpos = 0, substr;
        
        $.each(["stripComments", "stripScripts", "stripWhitespace"], function(i, name){
            var fn = $.translate[name];
            if( o[name] )
                t = isString ? fn(t) : $.map(t, fn);
        });

        this.rawSource = "<div>" + (isString ? t : t.join("</div><div>")) + "</div>";
        this._m3 = new RegExp("[" + separator + "](?![^" + separator + "]*[" + separator + "])");
        this.options = o;
        this.from = o.from = toLangCode(o.from) || "";
        this.to = o.to = toLangCode(o.to) || "";
        this.source = t;
        this.rawTranslation = "";
        this.translation = [];
        this.i = 0;
        this.stopped = False;
        this.elements = o.nodes;
        
        //this._nres = 0;
        //this._progress = 0;
        this._i = -1; //TODO: rename
        this.rawSources = [];
        
        while(True){
            substr = this.truncate( this.rawSource.substr(lastpos), o.limit);
            if(!substr) break;
            this.rawSources.push(substr);
            lastpos += substr.length;
        }
        this.queue = new Array(this.rawSources.length);
        this.done = 0;
        
        o.start.call(this, t , o.from, o.to, o);
        
        if(o.timeout)
            this.timeout = setTimeout(bind(o.onTimeout, this, [t, o.from, o.to, o]), o.timeout);
        
        (o.toggle && o.nodes) ?	
            (o.textNodes ? this._toggleTextNodes() : this._toggle()) : 
            this._process();
    },
    
    _process: function(){
        if(this.stopped)
            return;
        var o = this.options,
            i = this.rawTranslation.length,
            lastpos, subst, divst, divcl;
        var that = this;
        
        while( (lastpos = this.rawTranslation.lastIndexOf("</div>", i)) > -1){

            i = lastpos - 1;
            subst = this.rawTranslation.substr(0, i + 1);
            /*jslint skipLines*/		
            divst = subst.match(/<div[> ]/gi);	
            divcl = subst.match(/<\/div>/gi);
            /*jslint skipLinesEnd*/
            
            divst = divst ? divst.length : 0;
            divcl = divcl ? divcl.length : 0;
            
            if(divst !== divcl + 1) continue; //if there are some unclosed divs

            var divscompl = $( this.rawTranslation.substr(0, i + 7) ), 
                divlen = divscompl.length, 
                l = this.i;
            
            if(l === divlen) break; //if no new elements have been completely translated
            
            divscompl.slice(l, divlen).each( bind(function(j, e){
                if(this.stopped)
                    return False;
                var e_html = $(e).html(), tr = o.trim ? $.trim(e_html) : e_html,
                    i = l + j, src = this.source,
                    from = !this.from && this.detectedSourceLanguage || this.from;
                this.translation[i] = tr;//create an array for complete callback
                this.isString ? this.translation = tr : src = this.source[i];
                
                o.each.call(this, i, tr, src, from, this.to, o);
                
                this.i++;
            }, this));
            
            break;
        }
        
        if(this.rawSources.length - 1 == this._i)
            this._complete();
        
        var _translate = bind(this._translate, this);
        
        if(o.parallel){
            if(this._i < 0){
                if(!o.parallel){
                    $.each(this.rawSources, _translate);
                }else{
                    var j = 0, n = this.rawSources.length;
                    function seq(){
                        _translate();
                        if(j++ < n)
                            setTimeout( seq, o.parallel );
                    }
                    seq();
                }
            }
        }else
            _translate();
            
    },
    
    _translate: function(){
        this._i++;		
        var i = this._i, src = this.rawSourceSub = this.rawSources[i];
        if(!src) return;
        if(!appid){
            GL.translate(src, this.from, this.to, bind(function(result){
                //this._progress = 100 * (++this._nres) / this.rawSources.length;
                //this.options.response.call(this, this._progress, result);
                if(result.error)
                    return this.options.error.call(this, result.error, this.rawSourceSub, this.from, this.to, this.options);
            
                this.queue[i] = result.translation || this.rawSourceSub;
                this.detectedSourceLanguage = result.detectedSourceLanguage;
                this._check();
            }, this));
        }else{
            $.ajax({
                url: "http://api.microsofttranslator.com/V2/Ajax.svc/Translate",
                dataType: "jsonp",
                jsonp: "oncomplete",
                crossDomain: true,
                context: this,
                data: {appId: appid, form: this.from, to: this.to, contentType: "text/html", text: src}
            }).success(function(data, status){
                //console.log(data);
                this.queue[i] = data || this.rawSourceSub;
                //this.detectedSourceLanguage = result.detectedSourceLanguage;
                this._check();
            });
        }
    },
    
    _check: function(){
        if(!this.options.parallel){
            this.rawTranslation += this.queue[this._i];
            this._process();
            return;
        }
        
        var done = 0;
        jQuery.each(this.queue, function(i, n) {
            if (n != undefined) done = i;
            else return false;
        });			
        
        if ((done > this.done) || (done === this.queue.length - 1)) {
            for(var i = 0; i <= done; i++)
                this.rawTranslation += this.queue[i];
            this._process();
        }
        this.done = done;
        
    },
    
    _complete: function(){
        clearTimeout(this.timeout);

        this.options.complete.call(this, this.translation, this.source, 
            !this.from && this.detectedSourceLanguage || this.from, this.to, this.options);
    },
    
    stop: function(){
        if(this.stopped)
            return this;
        this.stopped = True;
        this.options.error.call(this, {message:"stopped"});
        return this;
    }
};



$.translate = function(t, a){
    if(t == undefined)
        return new T();
    if( $.isFunction(t) )
        return $.translate.ready(t, a);
    var that = new T();
    
    var args = [].slice.call(arguments, 0);
    args.shift();
    return $.translate.ready( bind(that._init, that, [t, getOpt(args, $.translate.defaults)] ), False, that );
};


$.translate.fn = $.translate.prototype = T.prototype;

$.translate.fn.extend = $.translate.extend = $.extend;


$.translate.extend({
    
    _bind: bind,
    
    _filter: filter,
    
    _validate: validate,
    
    _getOpt: getOpt,
    
    _defaults: defaults, //base defaults used by other components as well //TODO
    
    defaults: $.extend({}, defaults),
    
    capitalize: function(t){ return t.charAt(0).toUpperCase() + t.substr(1).toLowerCase(); },
    
    truncate: function(text, limit){
        var i, m1, m2, m3, m4, t, encoded = encodeURIComponent( text );
        
        for(i = 0; i < 10; i++){
            try { 
                t = decodeURIComponent( encoded.substr(0, limit - i) );
            } catch(e){ continue; }
            if(t) break;
        }
        
        return ( !( m1 = /<(?![^<]*>)/.exec(t) ) ) ? (  //if no broken tag present
            ( !( m2 = />\s*$/.exec(t) ) ) ? (  //if doesn't end with '>'
                ( m3 = this._m3.exec(t) ) ? (  //if broken sentence present
                    ( m4 = />(?![^>]*<)/.exec(t) ) ? ( 
                        m3.index > m4.index ? t.substring(0, m3.index+1) : t.substring(0, m4.index+1)
                    ) : t.substring(0, m3.index+1) ) : t ) : t ) : t.substring(0, m1.index);
    },

    getLanguages: function(a, b){
        if(a == undefined || (b == undefined && !a))
            return GLL;
        
        var newObj = {}, typeof_a = typeof a,
            languages = b ? $.translate.getLanguages(a) : GLL,
            filterArg = ( typeof_a  === "object" || typeof_a  === "function" ) ? a : b;
                
        if(filterArg)
            if(filterArg.call) //if it's a filter function
                newObj = filter(languages, filterArg);
            else //if it's an array of languages
                for(var i = 0, length = filterArg.length, lang; i < length; i++){
                    lang = $.translate.toLanguage(filterArg[i]);
                    if(languages[lang] != undefined)
                        newObj[lang] = languages[lang];
                }
        else //if the first argument is true -> only translatable languages
            newObj = filter(GLL, GL.isTranslatable);
        
        return newObj;
    },
    

    toLanguage: function(a, format){
        var u = a.toUpperCase();
        var l = inverseLanguages[u] || 
            (GLL[u] ? u : undefined) || 
            inverseLanguages[($.translate.languageCodeMap[a.toLowerCase()]||"").toUpperCase()];
        return l == undefined ? undefined :
            format === "lowercase" ? l.toLowerCase() : format === "capitalize" ? $.translate.capitalize(l) : l;				
    },
    
    toLanguageCode: function(a){
        return GLL[a] || 
            GLL[ $.translate.toLanguage(a) ] || 
            $.translate.languageCodeMap[a.toLowerCase()];
    },
        
    same: function(a, b){
        return a === b || toLangCode(a) === toLangCode(b);
    },
        
    isTranslatable: function(l){
        return GL ? GL.isTranslatable( toLangCode(l) ) : !!toLangCode(l);
    },

    //keys must be lower case, and values must equal to a 
    //language code specified in the Language API
    languageCodeMap: {
        "pt": "pt-PT",
        "pt-br": "pt-PT",		
        "he": "iw",
        "zlm": "ms",
        "zh-hans": "zh-CN",
        "zh-hant": "zh-TW"
        //,"zh-sg":"zh-CN"
        //,"zh-hk":"zh-TW"
        //,"zh-mo":"zh-TW"
    },
    
    //use only language codes specified in the Language API
    isRtl: {
        "ar": True,
        "iw": True,
        "fa": True,
        "ur": True,
        "yi": True
    },
    
    getBranding: function(){
        return $( GL.getBranding.apply(GL, arguments) );
    },
    
    load: function(key, version){
        loading = True;

        if(!key || (key.length < 40)){ //Google API
            function _load(){ 
                google.load("language", version || "1", {"callback" : google_loaded});
            }
        
            if(typeof google !== "undefined" && google.load)
                _load();
            else
                $.getScript(((document.location.protocol == "https:") ? "https://" : "http://") +
                            "www.google.com/jsapi" + (key ? "?key=" + key : ""), _load);
        }else{ //Microsoft API
            appid = key;
            $.ajax({
                url: "http://api.microsofttranslator.com/V2/Ajax.svc/GetLanguagesForTranslate",
                dataType: "jsonp",
                jsonp: "oncomplete",
                crossDomain: true,
                context: this,
                data: {appId: appid}
            }).success(function(languageCodes, status){
                $.ajax({
                    url: "http://api.microsofttranslator.com/V2/Ajax.svc/GetLanguageNames",
                    dataType: "jsonp",
                    jsonp: "oncomplete",
                    crossDomain: true,
                    context: this,
                    data: {appId: appid, locale: "en", languageCodes: '["'+languageCodes.join('", "')+'"]'}
                }).success(function(languageNames, status){
                    ms_loaded(languageCodes, languageNames);
                });

            });

        }

        return $.translate;
    },
    
    ready: function(fn, preventAutoload, that){
        $.translate.isReady ? fn() : readyList.push(fn);
        if(!loading && !preventAutoload)
            $.translate.load();
        return that || $.translate;
    },
    
    isReady: False,
    
    overload: [
        [[],[]],
        [[Str, Str, Obj],	["from", "to", "options"]	],
        [[Str, Obj], 		["to", "options"]			],
        [[Obj], 			["options"]					],
        [[Str, Str], 		["from", "to"]				],
        [[Str], 			["to"]						],
        [[Str, Str, Fn],	["from", "to", "complete"]	],
        [[Str, Fn], 		["to", "complete"]			]
         //TODO
        //,[[Str, Str, Fn, Fn], ["from", "to", "each", "complete"]]
    ]
    /*jslint skipLines*/
    ,
    //jslint doesn't seem to be able to parse some regexes correctly if used on the server,
    //however it works fine if it's run on the command line: java -jar rhino.jar jslint.js file.js
    stripScripts: bind(replace, True, [/<script[^>]*>([\s\S]*?)<\/script>/gi, ""]),
    
    stripWhitespace: bind(replace, True, [/\s\s+/g, " "]),
    
    stripComments: bind(replace, True, [/<![ \r\n\t]*(--([^\-]|[\r\n]|-[^\-])*--[ \r\n\t]*)>/g, ""])
    /*jslint skipLinesEnd*/
});


})(jQuery);
