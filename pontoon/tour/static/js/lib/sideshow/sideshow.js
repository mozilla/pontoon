/**
 @license
 Sideshow - An incredible Javascript interactive help Library
 Version: 0.4.3
 Date: 2015-03-19
 Author: Fortes Informática http://www2.fortesinformatica.com.br/
 Available under Apache License 2.0 (https://raw2.github.com/fortesinformatica/sideshow/master/LICENSE)
 **/

;
(function (global, $, jazz, markdown) {
  (function (name, module) {
    var ss = module();

    if (typeof define === 'function' && define.amd) {
      define(module);
    } else {
      global[name] = ss;
    }
  })('sideshow', function () {
    //jQuery is needed
    if ($ === undefined) throw new SSException("2", "jQuery is required for Sideshow to work.");

    //Jazz is needed
    if (jazz === undefined) throw new SSException("3", "Jazz is required for Sideshow to work.");

    //Pagedown (the Markdown parser used by Sideshow) is needed
    if (markdown === undefined) throw new SSException("4", "Pagedown (the Markdown parser used by Sideshow) is required for Sideshow to work.");
    var globalObjectName = "Sideshow",
        $window, $body, $document, pollingDuration = 150,
        longAnimationDuration = 100,
        
        
        
        /** 
         The main class for Sideshow
         
         @class SS 
         @static
         **/
        
        SS = {
        /**
         The current Sideshow version
         
         @property VERSION
         @type String
         **/
        get VERSION() {
          return "0.4.3";
        }
        },
        
        
        controlVariables = [],
        flags = {
        lockMaskUpdate: false,
        changingStep: false,
        skippingStep: false,
        running: false
        },
        wizards = [],
        currentWizard,
        
        
        /**
         Possible statuses for an animation
         
         @@enum AnimationStatus
         **/
        
        AnimationStatus = jazz.Enum("VISIBLE", "FADING_IN", "FADING_OUT", "NOT_DISPLAYED", "NOT_RENDERED", "TRANSPARENT");



    /**
     A custom exception class for Sideshow
     
     @class SSException
     @extends Error
     @param {String} code                                  The error code
     @param {String} message                               The error message
     **/

    function SSException(code, message) {
      this.name = "SSException";
      this.message = "[SIDESHOW_E#" + ("00000000" + code).substr(-8) + "] " + message;
    }

    SSException.prototype = new Error();
    SSException.prototype.constructor = SSException;


    /**
     Shows a warning  in a pre-defined format
     
     @@function showWarning
     @param {String} code                                  The warning code
     @param {String} message                               The warning message
     **/

    function showWarning(code, message) {
      console.warn("[SIDESHOW_W#" + ("00000000" + code).substr(-8) + "] " + message);
    }

    /**
     Shows a deprecation warning in a pre-defined format
     
     @@function showDeprecationWarning
     @param {String} message                               The warning message
     **/

    function showDeprecationWarning(message) {
      console.warn("[DEPRECATION_WARNING] " + message);
    }


    /**
     Parses a string in the format "#px" in a number
     
     @@function parsePxValue
     @param {String} value                                 A value with/without a px unit
     @return Number                                        The number value without unit 
     **/

    function parsePxValue(value) {
      if (value.constructor !== String) return value;
      var br = value === "" ? "0" : value;
      return +br.replace("px", "");
    }

    /**
     Gets a string from the dictionary in the current language
     
     @@function getString
     @param {Object} stringKeyValuePair                    A string key-value pair in dictionary
     @return String                                        The string value in the current language
     **/

    function getString(stringKeyValuePair) {
      if (!(SS.config.language in stringKeyValuePair)) {
        showWarning("2001", "String not found for the selected language, getting the first available.");
        return stringKeyValuePair[Object.keys(stringKeyValuePair)[0]];
      }

      return stringKeyValuePair[SS.config.language];
    }

    /**
     Registers hotkeys to be used when running Sideshow
     
     @@function registerInnerHotkeys
     **/

    function registerInnerHotkeys() {
      $document.keyup(innerHotkeysListener);
    }

    /**
     Unregisters hotkeys used when running Sideshow
     
     @@function Unregisters
     **/

    function unregisterInnerHotkeys() {
      $document.unbind("keyup", innerHotkeysListener);
    }

    function innerHotkeysListener(e) {
      //Esc or F1
      if (e.keyCode == 27 || e.keyCode == 112) SS.close();
    }

    /**
     Registers global hotkeys
     
     @@function registerGlobalHotkeys
     **/

    function registerGlobalHotkeys() {
      $document.keyup(function (e) {
        //F2
        if (e.keyCode == 113) {
          if (e.shiftKey) SS.start({
            listAll: true
          });
          else SS.start();
        }
      });
    }

    /**
     Removes nodes created by Sideshow (except mask, which remains due to performance reasons when recalling Sideshow)
     
     @@function removeDOMGarbage
     **/

    function removeDOMGarbage() {
      $("[class*=\"sideshow\"]").not(".sideshow-mask-part, .sideshow-mask-corner-part, .sideshow-subject-mask").remove();
    }


    /**
     Strings Dictionary
     
     @@object strings
     **/
    var strings = {
      availableWizards: {
        "en": "Available Tutorials",
        "pt-br": "Tutoriais Disponíveis",
        "es": "Tutoriales Disponibles",
        "fr": "Tutoriels Disponibles"
      },
      relatedWizards: {
        "en": "Related Wizards",
        "pt-br": "Tutoriais Relacionados",
        "es": "Tutoriales Relacionados",
        "fr": "Tutoriels Similaires"
      },
      noAvailableWizards: {
        "en": "There's no tutorials available.",
        "pt-br": "Não há tutoriais disponíveis para esta tela.",
        "es": "No hay tutoriales disponibles.",
        "fr": "Il n'y a pas de tutoriels disponibles"
      },
      close: {
        "en": "Close",
        "pt-br": "Fechar",
        "es": "Cerrar",
        "fr": "Fermer"
      },
      estimatedTime: {
        "en": "Estimated Time",
        "pt-br": "Tempo Estimado",
        "es": "Tiempo Estimado",
        "fr": "Temps estimées"
      },
      next: {
        "en": "Next",
        "pt-br": "Continuar",
        "es": "Continuar",
        "fr": "Continuer"
      },
      finishWizard: {
        "en": "Finish Wizard",
        "pt-br": "Concluir Tutorial",
        "es": "Concluir Tutorial",
        "fr": "Terminer Tutoriel"
      }
    };


    /**
     Sideshow Settings
     
     @@object config
     **/
    SS.config = {};

    /**
     Application route to persists user preferences
     
     @@field userPreferencesRoute
     @type String
     @@unused
     @@todo Implement persistence logic
     **/
    SS.config.userPreferencesRoute = null;

    /**
     Logged in user
     
     @@field loggedInUser
     @type String
     @@unused
     **/
    SS.config.loggedInUser = null;

    /**
     Chosen language for sideshow interface
     
     @@field language
     @type String
     **/
    SS.config.language = "en";

    /**
     Defines if the intro screen (the tutorial list) will be	skipped when there's just one 
     tutorial available. This way, when Sideshow is invoked, the first step is directly shown.
     
     @@field autoSkipIntro
     @type boolean
     **/
    SS.config.autoSkipIntro = false;


    /**
     Stores the variables used in step evaluators 
     
     @class ControlVariables
     @static
     **/
    SS.ControlVariables = {};

    /**
     Sets a variable value
     
     @method set
     @param {String} name                                  The variable name
     @param {String} value                                 The variable value
     @return {String}                                      A formatted key=value pair representing the defined variable 
     **/
    SS.ControlVariables.set = function (name, value) {
      var variable = {};
      if (this.isDefined(name)) {
        variable = this.getNameValuePair(name);
      } else controlVariables.push(variable);

      variable.name = name;
      variable.value = value;
      return name + "=" + value;
    };

    /**
     Sets a variable if not defined yet
     
     @method setIfUndefined
     @param {String} name                                  The variable name
     @param {String} value                                 The variable value
     @return {String}                                      A formatted key=value pair representing the defined variable 
     **/
    SS.ControlVariables.setIfUndefined = function (name, value) {
      if (!this.isDefined(name)) return this.set(name, value);
    };

    /**
     Checks if some variable is already defined
     
     @method isDefined
     @param {String} name                                  The variable name
     @return {boolean}                                     A boolean indicating if the variable is already defined
     **/
    SS.ControlVariables.isDefined = function (name) {
      return this.getNameValuePair(name) !== undefined;
    };

    /**
     Gets a variable value
     
     @method get
     @param {String} name                                  The variable name
     @return {any}                                         The variable value
     **/
    SS.ControlVariables.get = function (name) {
      var pair = this.getNameValuePair(name);
      return pair ? pair.value : undefined;
    };

    /**
     Gets a pair with name and value 
     
     @method getNameValuePair
     @param {String} name                                  The variable name
     @return {Object}                                      A pair with the variable name and value
     **/
    SS.ControlVariables.getNameValuePair = function (name) {
      for (var i = 0; i < controlVariables.length; i++) {
        var variable = controlVariables[i];
        if (variable.name === name) return variable;
      }
    };

    /**
     Remove some variable from the control variables collection
     
     @method remove
     @param {String} name                                  The variable name
     @return {Object}                                      A pair with the removed variable name and value
     **/
    SS.ControlVariables.remove = function (name) {
      return controlVariables.splice(controlVariables.indexOf(this.getNameValuePair(name)), 1);
    };

    /**
     Clear the control variables collection 
     
     @method clear
     **/
    SS.ControlVariables.clear = function () {
      controlVariables = [];
    };


    /**
     A visual item 
     
     @class VisualItem
     @@abstract
     **/
    var VisualItem = jazz.Class().abstract;

    /**
     The jQuery wrapped DOM element for the visual item
     
     @@field $el
     @type Object 
     **/
    VisualItem.field("$el");

    /**
     The jQuery wrapped DOM element for the visual item
     
     @@field $el
     @type AnimationStatus 
     **/
    VisualItem.field("status", AnimationStatus.NOT_RENDERED);

    /**
     Renders the item's DOM object
     
     @method render
     **/
    VisualItem.method("render", function ($parent) {
      ($parent || $body).append(this.$el);
      this.status = AnimationStatus.NOT_DISPLAYED;
    });

    /**
     Destroys the item's DOM object
     
     @method destroy
     **/
    VisualItem.method("destroy", function () {
      this.$el.remove();
    });

    /**
     A visual item which can be shown and hidden
     
     @class HidableItem
     @@abstract
     @extends VisualItem
     **/
    var HidableItem = jazz.Class().extending(VisualItem).abstract;

    /**
     Shows the visual item
     
     @method show
     @param {boolean} displayButKeepTransparent            The item will hold space but keep invisible
     **/
    HidableItem.method("show", function (displayButKeepTransparent) {
      if (!this.$el) this.render();
      if (!displayButKeepTransparent) this.$el.removeClass("sideshow-invisible");
      this.$el.removeClass("sideshow-hidden");
      this.status = AnimationStatus.VISIBLE;
    });

    /**
     Hides the visual item
     
     @method hide
     **/
    HidableItem.method("hide", function (keepHoldingSpace) {
      if (!keepHoldingSpace) this.$el.addClass("sideshow-hidden");
      this.$el.addClass("sideshow-invisible");
      this.status = AnimationStatus.NOT_DISPLAYED;
    });

    /**
     A visual item which holds fading in and out capabilities
     
     @class FadableItem
     @@abstract
     @extends HidableItem
     **/
    var FadableItem = jazz.Class().extending(HidableItem).abstract;

    /**
     Does a fade in transition for the visual item
     
     @method fadeIn
     **/
    FadableItem.method("fadeIn", function (callback, linearTimingFunction) {
      var item = this;
      item.status = AnimationStatus.FADING_IN;

      if (!item.$el) this.render();
      if (linearTimingFunction) item.$el.css("animation-timing-function", "linear");
      item.$el.removeClass("sideshow-hidden");

      //Needed hack to get CSS transition to work properly
      setTimeout(function () {
        item.$el.removeClass("sideshow-invisible");

        setTimeout(function () {
          item.status = AnimationStatus.VISIBLE;
          if (linearTimingFunction) item.$el.css("animation-timing-function", "ease");
          if (callback) callback();
        }, longAnimationDuration);
      }, 20); //<-- Yeap, I'm really scheduling a timeout for 20 milliseconds... this is a dirty trick =)
    });

    /**
     Does a fade out transition for the visual item
     
     @method fadeOut
     **/
    FadableItem.method("fadeOut", function (callback, linearTimingFunction) {
      var item = this;
      if (item.status != AnimationStatus.NOT_RENDERED) {
        item.status = AnimationStatus.FADING_OUT;

        if (linearTimingFunction) item.$el.css("animation-timing-function", "linear");
        item.$el.addClass("sideshow-invisible");

        setTimeout(function () {
          item.$el.addClass("sideshow-hidden");
          item.status = AnimationStatus.NOT_DISPLAYED;
          if (linearTimingFunction) item.$el.css("animation-timing-function", "ease");
          if (callback) callback();
        }, longAnimationDuration);
      }
    });


    /**
     Represents a tutorial
     
     @class Wizard
     @@initializer
     @param {Object} wizardConfig                          The wizard configuration object                        
     **/
    var Wizard = jazz.Class(function (wizardConfig) {
      this.name = wizardConfig.name;
      this.title = wizardConfig.title;
      this.description = wizardConfig.description;
      this.estimatedTime = wizardConfig.estimatedTime;
      this.affects = wizardConfig.affects;
      this.preparation = wizardConfig.preparation;
      this.listeners = wizardConfig.listeners;
      this.showStepPosition = wizardConfig.showStepPosition;
      this.relatedWizards = wizardConfig.relatedWizards;
    });

    /**
     A function to prepare the environment for running a wizard (e.g. redirecting to some screen)
     
     @@field preparation
     @type Function
     **/
    Wizard.field("preparation");

    /**
     An object with listeners to this wizard (e.g. beforeWizardStarts, afterWizardEnds)
     
     @@field listeners
     @type Object
     **/
    Wizard.field("listeners");

    /**
     A configuration flag that defines if the step position (e.g. 2/10, 3/15, 12/12) will be shown
     
     @@field showStepPosition
     @type boolean
     **/
    Wizard.field("showStepPosition");

    /**
     An array with related wizards names. These wizards are listed after the ending of the current wizard.
     
     @@field relatedWizards
     @type Array
     **/
    Wizard.field("relatedWizards");

    /**
     The wizard unique name (used internally as an identifier)
     
     @@field name
     @type String
     **/
    Wizard.field("name");

    /**
     The wizard title (will be shown in the list of available wizards)
     
     @@field title
     @type String
     **/
    Wizard.field("title");

    /**
     The wizard description (will be shown in the list of available wizards)
     
     @@field description
     @type String
     **/
    Wizard.field("description");

    /**
     The wizard estimated completion time (will be shown in the list of available wizards)
     
     @@field estimatedTime
     @type String
     **/
    Wizard.field("estimatedTime");

    /**
     A collection of rules to infer whether a wizard should be available in a specific screen
     
     @@field affects
     @type Array
     **/
    Wizard.field("affects");

    /**
     The sequence of steps for this wizard
     
     @@field storyline
     @private
     @type Object
     **/
    Wizard.field("_storyline");

    /**
     Points to the current step object in a playing wizard
     
     @@field currentStep
     @type Object
     **/
    Wizard.field("currentStep");

    /**
     Sets the storyline for the wizard
     
     @method storyLine
     **/
    Wizard.method("storyLine", function (storyline) {
      this._storyline = storyline;
    });

    /**
     Runs the wizard
     
     @method play
     **/
    Wizard.method("play", function () {
      var wiz = this;

      Polling.enqueue("check_composite_mask_subject_changes", function () {
        Mask.CompositeMask.singleInstance.pollForSubjectChanges();
      });

      Polling.enqueue("check_arrow_changes", function () {
        Arrows.pollForArrowsChanges(true);
      });

      //Checks if the wizard has a storyline
      if (!this._storyline) throw new SSException("201", "A wizard needs to have a storyline.");
      var steps = this._storyline.steps;

      //Checks if the storyline has at least one step
      if (steps.length === 0) throw new SSException("202", "A storyline must have at least one step.");

      DetailsPanel.singleInstance.render();

      StepDescription.singleInstance.render();

      var listeners = this.listeners;
      if (listeners && listeners.beforeWizardStarts) listeners.beforeWizardStarts();

      flags.changingStep = true;
      this.showStep(steps[0], function () {
        //Releases the polling for checking any changes in the current subject
        //flags.lockMaskUpdate = false;
        //Register the function that checks the completing of a step in the polling queue
        Polling.enqueue("check_completed_step", function () {
          wiz.pollForCheckCompletedStep();
        });
      });

      Mask.CompositeMask.singleInstance.fadeIn();
    });

    /**
     Shows a specific step
     
     @method showStep
     @param {Object} step                                  The step to be shown
     @param {Function} callback                            A callback function to be called
     **/
    Wizard.method("showStep", function (step, callback) {
      var wizard = this;
      flags.skippingStep = false;

      Arrows.clear();

      if (this.currentStep && this.currentStep.listeners && this.currentStep.listeners.afterStep) this.currentStep.listeners.afterStep();

      function skipStep(wiz) {
        flags.skippingStep = true;
        wizard.next();
      }

      if (step && step.listeners && step.listeners.beforeStep) step.listeners.beforeStep();

      //The shown step is, of course, the current
      this.currentStep = step;

      //If the step has a skipIf evaluator and it evaluates to true, we'll skip to the next step!
      if (step.skipIf && step.skipIf()) skipStep(this);

      if (flags.changingStep && !flags.skippingStep) {
        //Sets the current subject and updates its dimension and position
        if (step.subject) SS.setSubject(step.subject);
        else SS.setEmptySubject();
        //Updates the mask
        Mask.CompositeMask.singleInstance.update(Subject.position, Subject.dimension, Subject.borderRadius);

        var sm = Mask.SubjectMask.singleInstance;
        sm.fadeOut(function () {
          if (step.lockSubject) sm.show(true);
        });
        //The details panel (that wraps the step description and arrow) is shown
        DetailsPanel.singleInstance.show();
        //Repositionate the details panel depending on the remaining space in the screen
        DetailsPanel.singleInstance.positionate();
        //Sets the description properties (text, title and step position)
        var description = StepDescription.singleInstance;
        var text = step.text;
        text = text instanceof Function ? SS.heredoc(text) : text;
        if (step.format == "html") {
          description.setHTML(text);
        } else if (step.format == "markdown") {
          description.setHTML(new markdown.Converter().makeHtml(text));
        } else {
          description.setText(text);
        }

        description.setTitle(step.title);
        description.setStepPosition((this.getStepPosition() + 1) + "/" + this._storyline.steps.length);
        //If this step doesn't have its own passing conditions/evaluators, or the flag "showNextButton" is true, then, the button is visible
        if (step.showNextButton || step.autoContinue === false || !(step.completingConditions && step.completingConditions.length > 0)) {
          var nextStep = this._storyline.steps[this.getStepPosition() + 1];
          if (nextStep) {
            description.nextButton.setText(getString(strings.next) + ": " + this._storyline.steps[this.getStepPosition() + 1].title);
          } else {
            description.nextButton.setText(getString(strings.finishWizard));
          }
          description.nextButton.show();

          if (step.autoContinue === false) description.nextButton.disable();
        } else {
          description.nextButton.hide();
        }

        if (step.targets && step.targets.length > 0) {
          Arrows.setTargets(step.targets);
          Arrows.render(step.arrowPosition);
          Arrows.positionate();
          Arrows.fadeIn();
        }

        //Step Description is shown, but is transparent yet (since we need to know its dimension to positionate it properly)
        description.show(true);
        if (!Mask.CompositeMask.singleInstance.scrollIfNecessary(Subject.position, Subject.dimension)) {
          description.positionate();
          //Do a simple fade in for the description box
          description.fadeIn();
        }


        //If a callback is passed, call it    
        if (callback) callback();
        flags.changingStep = false;
      }
    });

    /**
     Shows the next step of the wizard
     
     @method next 
     @param {Function} callback                            A callback function to be called
     **/
    Wizard.method("next", function (callback, nextStep) {
      if (!flags.changingStep || flags.skippingStep) {
        flags.changingStep = true;
        var currentStep = this.currentStep;
        nextStep = nextStep || this._storyline.steps[this.getStepPosition(this.currentStep) + 1];
        var self = this;

        this.hideStep(function () {
          if (nextStep) self.showStep(nextStep, function () {
            if (callback) callback();
          });
          else {
            if (currentStep && currentStep.listeners && currentStep.listeners.afterStep) currentStep.listeners.afterStep();

            var completedWizard = currentWizard;
            currentWizard = null;
            var listeners = self.listeners;
            if (listeners && listeners.afterWizardEnds) listeners.afterWizardEnds();

            if (!SS.showRelatedWizardsList(completedWizard)) SS.close();
          }
        });
      }
    });

    /**
     Hides the step
     
     @method hideStep
     @param {Function} callback                            A callback function to be called in the ending of the hiding process
     **/
    Wizard.method("hideStep", function (callback) {
      StepDescription.singleInstance.fadeOut(function () {
        DetailsPanel.singleInstance.hide();
      });
      Arrows.fadeOut();
      Mask.SubjectMask.singleInstance.update(Subject.position, Subject.dimension, Subject.borderRadius);
      Mask.SubjectMask.singleInstance.fadeIn(callback);
    });

    /**
     Returns the position of the step passed as argument or (by default) the current step
     
     @method getStepPosition
     @param {Object} step                                  The step object to get position
     **/
    Wizard.method("getStepPosition", function (step) {
      return this._storyline.steps.indexOf(step || this.currentStep);
    });

    /**
     Checks if a wizard should be shown in the current context (running each evaluator defined for this wizard)
     
     @method isEligible
     @return {boolean}                                     A boolean indicating if this wizard should be available in the current context
     **/
    Wizard.method("isEligible", function () {
      var l = global.location;

      function isEqual(a, b, caseSensitive) {
        return (caseSensitive) ? a === b : a.toLowerCase() === b.toLowerCase();
      }

      for (var c = 0; c < this.affects.length; c++) {
        var condition = this.affects[c];
        if (condition instanceof Function) {
          if (condition()) return true;
        } else if (condition instanceof Object) {
          if ("route" in condition) {
            var route = l.pathname + l.search + l.hash;
            if (isEqual(route, condition.route, condition.caseSensitive)) return true;
          }

          if ("hash" in condition) {
            if (isEqual(location.hash, condition.hash, condition.caseSensitive)) return true;
          }

          if ("url" in condition) {
            if (isEqual(location.href, condition.url, condition.caseSensitive)) return true;
          }
        }
      }
      return false;
    });

    /**
     Checks if the current user already watched this wizard
     
     @method isAlreadyWatched
     @return {boolean}                                     A boolean indicating if the user watched this wizard
     @@todo Implement this method...
     **/
    Wizard.method("isAlreadyWatched", function () {
      //ToDo
      return false;
    });

    /**
     A Polling function to check if the current step is completed
     
     @method pollForCheckCompletedStep
     **/
    Wizard.method("pollForCheckCompletedStep", function () {
      var conditions = this.currentStep.completingConditions;
      if (conditions && conditions.length > 0 && !flags.skippingStep) {
        var completed = true;
        for (var fn = 0; fn < conditions.length; fn++) {
          var completingCondition = conditions[fn];
          if (!completingCondition()) completed = false;
        }

        if (completed) {
          if (this.currentStep.autoContinue === false) StepDescription.singleInstance.nextButton.enable();
          else currentWizard.next();
        }
      }
    });


    Wizard.method("prepareAndPlay", function () {
      currentWizard = this;

      if (!this.isEligible()) {
        if (this.preparation) this.preparation(function () {
          currentWizard.play();
        });
        else throw new SSException("203", "This wizard is not eligible neither has a preparation function.");
      } else this.play();
    });


    /**
     The panel that holds step description, is positionated over the biggest remaining space among the four parts of a composite mask
     
     @class DetailsPanel
     @@singleton
     @extends FadableItem
     **/
    var DetailsPanel = jazz.Class().extending(FadableItem).singleton;

    /**
     An object holding dimension information for the Details Panel
     
     @@field dimension
     @type Object
     **/
    DetailsPanel.field("dimension", {});

    /**
     An object holding positioning information for the Details Panel
     
     @@field position
     @type Object
     **/
    DetailsPanel.field("position", {});

    /**
     Renders the Details Panel
     
     @method render
     **/
    DetailsPanel.method("render", function () {
      this.$el = $("<div>").addClass("sideshow-details-panel").addClass("sideshow-hidden");
      this.callSuper("render");
    });

    /**
     Positionates the panel automatically, calculating the biggest available area and putting the panel over there
     
     @method positionate
     **/
    DetailsPanel.method("positionate", function () {
      var parts = Mask.CompositeMask.singleInstance.parts;

      //Considering the four parts surrounding the current subject, gets the biggest one
      var sortedSides = [
        [parts.top, "height"],
        [parts.right, "width"],
        [parts.bottom, "height"],
        [parts.left, "width"]
      ].sort(function (a, b) {
        return a[0].dimension[a[1]] - b[0].dimension[b[1]];
      });

      var biggestSide = sortedSides.slice(-1)[0];

      for (var i = 2; i > 0; i--) {
        var side = sortedSides[i];
        var dimension = side[0].dimension;
        if (dimension.width > 250 && dimension.height > 250) {
          if ((dimension.width + dimension.height) > ((biggestSide[0].dimension.width + biggestSide[0].dimension.height) * 2)) biggestSide = side;
        }
      }

      if (biggestSide[1] == "width") {
        this.$el.css("left", biggestSide[0].position.x).css("top", 0).css("height", Screen.dimension.height).css("width", biggestSide[0].dimension.width);
      } else {
        this.$el.css("left", 0).css("top", biggestSide[0].position.y).css("height", biggestSide[0].dimension.height).css("width", Screen.dimension.width);
      }

      this.dimension = {
        width: parsePxValue(this.$el.css("width")),
        height: parsePxValue(this.$el.css("height"))
      };

      this.position = {
        x: parsePxValue(this.$el.css("left")),
        y: parsePxValue(this.$el.css("top"))
      };
    });



    /**
     Class representing all the current shown arrows
     
     @class Arrows
     @static
     **/
    var Arrows = {};

    Arrows.arrows = [];

    /**
     Clear the currently defined arrows
     
     @method clear
     @static
     **/
    Arrows.clear = function () {
      this.arrows = [];
    };

    /**
     Sets the targets for arrows to point
     
     @method setTargets
     @static
     **/
    Arrows.setTargets = function (targets, targetsChanged) {
      if (targets.constructor === String) targets = $(targets);

      if (targets instanceof $ && targets.length > 0) {
        targets.each(function () {
          var arrow = Arrow.build();
          arrow.target.$el = $(this);
          if (arrow.target.$el.is(":visible")) {
            Arrows.arrows.push(arrow);
            arrow.onceVisible = true;
          }
        });
      }
      else if (!targetsChanged) throw new SSException("150", "Invalid targets.");
    };

    Arrows.recreateDOMReferences = function () {
      for (var a = 0; a < this.arrows.length; a++) {
        var arrow = this.arrows[a];
        arrow.$el.remove();
      }

      Arrows.clear();
      Arrows.setTargets(currentWizard.currentStep.targets, true);
      Arrows.render();
      Arrows.positionate();
      Arrows.show();
    };

    /**
     Iterates over the arrows collection showing each arrow
     
     @method show
     @static
     **/
    Arrows.show = function () {
      for (var a = 0; a < this.arrows.length; a++) {
        var arrow = this.arrows[a];
        arrow.show();
      }
    };

    /**
     Iterates over the arrows collection hiding each arrow
     
     @method hide
     @static
     **/
    Arrows.hide = function () {
      for (var a = 0; a < this.arrows.length; a++) {
        var arrow = this.arrows[a];
        arrow.hide();
      }
    };

    /**
     Iterates over the arrows collection fading in each arrow
     
     @method fadeIn
     @static
     **/
    Arrows.fadeIn = function () {
      for (var a = 0; a < this.arrows.length; a++) {
        var arrow = this.arrows[a];
        arrow.fadeIn();
      }
    };

    /**
     Iterates over the arrows collection fading out each arrow
     
     @method fadeOut
     @static
     **/
    Arrows.fadeOut = function () {
      for (var a = 0; a < this.arrows.length; a++) {
        var arrow = this.arrows[a];
        registerFadeOut(arrow);
      }

      function registerFadeOut(arrow) {
        arrow.fadeOut(function () {
          arrow.destroy();
        });
      }
    };

    /**
     Iterates over the arrows collection repositionating each arrow
     
     @method positionate
     @static
     **/
    Arrows.positionate = function () {
      for (var a = 0; a < this.arrows.length; a++) {
        var arrow = this.arrows[a];
        arrow.positionate();
      }
    };

    /**
     Iterates over the arrows collection rendering each arrow
     
     @method render
     @static
     **/
    Arrows.render = function (arrowPosition) {
      for (var a = 0; a < this.arrows.length; a++) {
        var arrow = this.arrows[a];
        arrow.position = arrowPosition || "top";
        arrow.render();
      }
    };

    /**
     A Polling function to check if arrows coordinates has changed
     
     @method pollForArrowsChanges
     **/
    Arrows.pollForArrowsChanges = function () {
      var brokenReference = false;
      for (var a = 0; a < this.arrows.length; a++) {
        var arrow = this.arrows[a];
        if (arrow.hasChanged()) arrow.positionate();
        if (arrow.onceVisible && !arrow.target.$el.is(":visible")) brokenReference = true;
      }

      if (brokenReference) this.recreateDOMReferences();
    };


    /**
     A single arrow for pointing individual items in current subject 
     
     @class Arrow
     **/
    var Arrow = jazz.Class().extending(FadableItem);

    /**
     The jQuery wrapped object which will be pointed by this arrow
     
     @@field target
     @type Object
     **/
    Arrow.field("target", {});

    /**
     The position of the arrow. Valid values are "top", "right", "bottom" or "left". Defaults to "top"
     
     @@field position
     @type String
     **/

    Arrow.field("position", "");

    /**
     Flag created to set if the arrow was visible once, this is used for recreating references to the targets DOM objects
     
     @@field onceVisible
     @type Object
     **/
    Arrow.field("onceVisible", false);

    /**
     Renders the Arrow
     
     @method render
     **/
    Arrow.method("render", function () {
      this.$el = $("<div>").addClass("sideshow-subject-arrow").addClass(this.position).addClass("sideshow-hidden").addClass("sideshow-invisible");
      this.callSuper("render");
      //
    });

    /**
     Positionates the Arrow according to its target
     
     @method positionate
     **/
    Arrow.method("positionate", function () {
      var target = this.target,
          position = this.position;

      target.position = {
        x: target.$el.offset().left - $window.scrollLeft(),
        y: target.$el.offset().top - $window.scrollTop()
      };
      target.dimension = {
        width: parsePxValue(target.$el.outerWidth()),
        height: parsePxValue(target.$el.outerHeight())
      };

      var coordinates = { // a dictionary with each of the coordinates used for positioning Arrow
        top: {
          x: target.position.x + target.dimension.width / 2 - 20 + "px",
          y: target.position.y - 30 + "px"
        },
        right: {
          x: target.position.x + target.dimension.width - 12 + "px",
          y: target.position.y + target.dimension.height / 2 - 6 + "px"
        },
        bottom: {
          x: target.position.x + target.dimension.width / 2 - 35 + "px",
          y: target.position.y + target.dimension.height + 2 + "px"
        },
        left: {
          x: target.position.x - 35 + "px",
          y: target.position.y + target.dimension.height / 2 - 22 + "px"
        }
      };

      this.$el.css({
        left: coordinates[position].x,
        top: coordinates[position].y
      });
    });

    /**
     Shows the Arrow 
     
     @method show
     **/
    Arrow.method("show", function () {
      this.callSuper("show");
      this.positionate();
    });

    /**
     Does a fade in transition in the Arrow 
     
     @method fadeIn
     **/
    Arrow.method("fadeIn", function () {
      this.callSuper("fadeIn");
      this.positionate();
    });

    /**
     Checks if the arrow's target position or dimension has changed
     
     @method hasChanged
     @return boolean                                     
     **/
    Arrow.method("hasChanged", function () {
      return (this.target.dimension.width !== this.target.$el.outerWidth() || this.target.dimension.height !== this.target.$el.outerHeight() || this.target.position.y !== (this.target.$el.offset().top - $window.scrollTop()) || this.target.position.x !== (this.target.$el.offset().left - $window.scrollLeft()));
    });


    /**
     Represents a panel holding the step description
     
     @class StepDescription
     @extends FadableItem
     @@initializer
     **/
    var StepDescription = jazz.Class(function () {
      this.nextButton = StepDescriptionNextButton.build();
    }).extending(FadableItem).singleton;

    /**
     The step description text content
     
     @@field text
     @type String
     **/
    StepDescription.field("text", "");

    /**
     The title text for the step description panel
     
     @@field title
     @type String
     **/
    StepDescription.field("title", "");

    /**
     An object holding dimension information for the Step Description panel
     
     @@field dimension
     @type Object
     **/
    StepDescription.field("dimension", {});

    /**
     An object holding positioning information for the Step Description panel
     
     @@field position
     @type Object
     **/
    StepDescription.field("position", {});

    /**
     An object representing the next button for a step description panel 
     
     @@field nextButton
     @type Object
     **/
    StepDescription.field("nextButton");

    /**
     Sets the text for the step description panel
     
     @method setText
     @param {String} text                                  The text for the step description panel
     **/
    StepDescription.method("setText", function (text) {
      this.text = text;
      this.$el.find(".sideshow-step-text").text(text);
    });

    /**
     Sets the HTML content for the step description panel
     
     @method setHTML
     @param {String} text                                  The HTML content for step description panel
     **/
    StepDescription.method("setHTML", function (text) {
      this.text = text;
      this.$el.find(".sideshow-step-text").html(text);
    });

    /**
     Sets the title for the step description panel
     
     @method setTitle
     @param {String} title                                 The text for the step description panel
     **/
    StepDescription.method("setTitle", function (title) {
      this.title = title;
      this.$el.find("h2:first").text(title);
    });

    /**
     Sets the title for the step description panel
     
     @method setStepPosition
     @param {String} title                                 The text for the step description panel
     **/
    StepDescription.method("setStepPosition", function (stepPosition) {
      this.stepPosition = stepPosition;
      this.$el.find(".sideshow-step-position").text(stepPosition);
    });

    /**
     Renders the step description panel
     
     @method render
     **/
    StepDescription.method("render", function () {
      this.$el = $("<div>").addClass("sideshow-step-description").addClass("sideshow-hidden").addClass("sideshow-invisible");

      var stepPosition = $("<span>").addClass("sideshow-step-position");
      this.$el.append(stepPosition);
      if (currentWizard.showStepPosition === false) stepPosition.hide();

      this.$el.append($("<h2>"));
      this.$el.append($("<div>").addClass("sideshow-step-text"));
      this.nextButton.render(this.$el);
      this.nextButton.$el.click(function () {
        currentWizard.next();
      });
      DetailsPanel.singleInstance.$el.append(this.$el);
    });

    /**
     Shows the step description panel
     
     @method show
     **/
    StepDescription.method("show", function (displayButKeepTransparent) {
      this.callSuper("show", displayButKeepTransparent);
      //this.positionate();
    });

    /**
     Positionates the step description panel
     
     @method positionate
     **/
    StepDescription.method("positionate", function () {
      var dp = DetailsPanel.singleInstance;

      if (dp.dimension.width >= 900) this.dimension.width = 900;
      else this.dimension.width = dp.dimension.width * 0.9;

      this.$el.css("width", this.dimension.width);

      var paddingLeftRight = (parsePxValue(this.$el.css("padding-left")) + parsePxValue(this.$el.css("padding-right"))) / 2;
      var paddingTopBottom = (parsePxValue(this.$el.css("padding-top")) + parsePxValue(this.$el.css("padding-bottom"))) / 2;

      this.dimension.height = parsePxValue(this.$el.outerHeight());

      //Checks if the description dimension overflow the available space in the details panel
      if (this.dimension.height > dp.dimension.height || this.dimension.width < 400) {
        this.dimension.width = $window.width() * 0.9;
        this.$el.css("width", this.dimension.width);
        this.dimension.height = parsePxValue(this.$el.outerHeight());

        this.position.x = ($window.width() - this.dimension.width) / 2;
        this.position.y = ($window.height() - this.dimension.height) / 2;
      } else {
        this.position.x = (dp.dimension.width - this.dimension.width) / 2;
        this.position.y = (dp.dimension.height - this.dimension.height) / 2;
      }

      this.$el.css("left", this.position.x - paddingLeftRight);
      this.$el.css("top", this.position.y - paddingTopBottom);
    });


    /**
     Step next button 
     
     @class StepDescriptionNextButton
     @extends HidableItem
     **/
    var StepDescriptionNextButton = jazz.Class().extending(HidableItem);

    /**
     The text for the next button
     
     @@field _text
     @private
     **/
    StepDescriptionNextButton.field("_text");

    /**
     Disables the next button
     
     @method disable
     **/
    StepDescriptionNextButton.method("disable", function () {
      this.$el.attr("disabled", "disabled");
    });

    /**
     Enables the next button
     
     @method enable
     **/
    StepDescriptionNextButton.method("enable", function () {
      this.$el.attr("disabled", null);
    });

    /**
     Sets the text for the next button
     
     @method setText
     @param {String} text                                  The text for the next button
     **/
    StepDescriptionNextButton.method("setText", function (text) {
      this._text = text;
      this.$el.text(text);
    });

    /**
     Renders the Next Button
     
     @method render
     @param {Object} $stepDescriptionEl                    The jQuery wrapped DOM element for the Step Description panel
     **/
    StepDescriptionNextButton.method("render", function ($stepDescriptionEl) {
      this.$el = $("<button>").addClass("sideshow-next-step-button");
      this.callSuper("render", $stepDescriptionEl);
    });

    /**
     Represents the current available area in the browser
     
     @class Screen
     @static
     **/
    var Screen = {};

    /**
     Object holding dimension information for the screen
     
     @@field
     @static
     @type Object
     **/
    Screen.dimension = {};

    /**
     Checks if the screen dimension information has changed
     
     @method hasChanged
     @static
     @return boolean
     **/
    Screen.hasChanged = function () {
      return ($window.width() !== this.dimension.width) || ($window.height() !== this.dimension.height);
    };

    /**
     Updates the dimension information for the screen 
     
     @method updateInfo
     @static
     **/
    Screen.updateInfo = function () {
      this.dimension.width = $window.width();
      this.dimension.height = $window.height();
    };

    /**
     The current subject (the object being shown by the current wizard)
     
     @class Subject
     @static
     **/
    var Subject = {};

    /**
     The current subject jQuery wrapped DOM element 
     
     @@field obj
     @static
     @type Object
     **/
    Subject.obj = null;

    /**
     The current subject dimension information
     
     @@field position
     @static
     @type Object
     **/
    Subject.dimension = {};

    /**
     The current subject positioning information
     
     @@field position
     @static
     @type Object
     **/
    Subject.position = {};

    /**
     The current subject border radius information
     
     @@field borderRadius
     @static
     @type Object
     **/
    Subject.borderRadius = {};

    /**
     Checks if the object has changed since the last checking
     
     @method hasChanged
     @return boolean
     **/
    Subject.hasChanged = function () {
      if (!this.obj) return false;

      return (this.obj.offset().left - $window.scrollLeft() !== this.position.x) || (this.obj.offset().top - $window.scrollTop() !== this.position.y) || (this.obj.outerWidth() !== this.dimension.width) || (this.obj.outerHeight() !== this.dimension.height) || (parsePxValue(this.obj.css("border-top-left-radius")) !== this.borderRadius.leftTop) || (parsePxValue(this.obj.css("border-top-right-radius")) !== this.borderRadius.rightTop) || (parsePxValue(this.obj.css("border-bottom-left-radius")) !== this.borderRadius.leftBottom) || (parsePxValue(this.obj.css("border-bottom-right-radius")) !== this.borderRadius.rightBottom) || Screen.hasChanged();
    };

    /**
     Updates the information about the suject
     
     @method updateInfo
     @param {Object} config                                Dimension, positioning and border radius information
     **/
    Subject.updateInfo = function (config) {
      if (config === undefined) {
        this.position.x = this.obj.offset().left - $window.scrollLeft();
        this.position.y = this.obj.offset().top - $window.scrollTop();
        this.dimension.width = this.obj.outerWidth();
        this.dimension.height = this.obj.outerHeight();
        this.borderRadius.leftTop = parsePxValue(this.obj.css("border-top-left-radius"));
        this.borderRadius.rightTop = parsePxValue(this.obj.css("border-top-right-radius"));
        this.borderRadius.leftBottom = parsePxValue(this.obj.css("border-bottom-left-radius"));
        this.borderRadius.rightBottom = parsePxValue(this.obj.css("border-bottom-right-radius"));
      } else {
        this.position.x = config.position.x;
        this.position.y = config.position.y;
        this.dimension.width = config.dimension.width;
        this.dimension.height = config.dimension.height;
        this.borderRadius.leftTop = config.borderRadius.leftTop;
        this.borderRadius.rightTop = config.borderRadius.rightTop;
        this.borderRadius.leftBottom = config.borderRadius.leftBottom;
        this.borderRadius.rightBottom = config.borderRadius.rightBottom;
      }

      Screen.updateInfo();
    };

    Subject.isSubjectVisible = function (position, dimension) {
      if ((position.y + dimension.height) > $window.height() || position.y < 0) {
        return false;
      }
      return true;
    };

    /**
     Namespace to hold classes for mask control
     
     @namespace Mask
     **/
    var Mask = {};

    /**
     Controls the mask that covers the subject during a step transition
     
     @class SubjectMask
     @@singleton
     **/
    Mask.SubjectMask = jazz.Class().extending(FadableItem).singleton;

    /**
     Renders the subject mask
     
     @method render
     **/
    Mask.SubjectMask.method("render", function () {
      this.$el = $("<div>").addClass("sideshow-subject-mask");
      this.callSuper("render");
    });

    /**
     Updates the dimension, positioning and border radius of the subject mask
     
     @method update
     @param {Object} position                              The positioning information 
     @param {Object} dimension                             The dimension information 
     @param {Object} borderRadius                          The border radius information 
     **/
    Mask.SubjectMask.method("update", function (position, dimension, borderRadius) {
      this.$el.css("left", position.x).css("top", position.y).css("width", dimension.width).css("height", dimension.height).css("border-radius", borderRadius.leftTop + "px " + borderRadius.rightTop + "px " + borderRadius.leftBottom + "px " + borderRadius.rightBottom + "px ");
    });

    /**
     Controls the mask surrounds the subject (the step focussed area)
     
     @class CompositeMask
     @@singleton
     **/
    Mask.CompositeMask = jazz.Class().extending(FadableItem).singleton;

    /**
     Initializes the composite mask
     
     @method init
     **/
    Mask.CompositeMask.method("init", function () {
      var mask = this;
      ["top", "left", "right", "bottom"].forEach(function (d) {
        mask.parts[d] = Mask.CompositeMask.Part.build();
      });
      ["leftTop", "rightTop", "leftBottom", "rightBottom"].forEach(function (d) {
        mask.parts[d] = Mask.CompositeMask.CornerPart.build();
      });
    });

    /**
     The parts composing the mask
     
     @@field parts
     @type Object
     **/
    Mask.CompositeMask.field("parts", {});

    /**
     Renders the composite mask 
     
     @method render
     **/
    Mask.CompositeMask.method("render", function () {
      var mask = this;
      for (var p in this.parts) {
        var part = this.parts[p];
        if (part.render) part.render();
      }
      this.$el = $(".sideshow-mask-part, .sideshow-mask-corner-part");
      // if(!this.$el || this.$el.length === 0) this.$el = $(".sideshow-mask-part, .sideshow-mask-corner-part");
      Mask.SubjectMask.singleInstance.render();
      ["leftTop", "rightTop", "leftBottom", "rightBottom"].forEach(function (d) {
        mask.parts[d].$el.addClass(d);
      });
      this.status = AnimationStatus.NOT_DISPLAYED;
    });

    /**
     Checks if the subject is fully visible, if not, scrolls 'til it became fully visible
     
     @method scrollIfNecessary
     @param {Object} position                              An object representing the positioning info for the mask
     @param {Object} dimension                             An object representing the dimension info for the mask
     **/
    Mask.CompositeMask.method("scrollIfNecessary", function (position, dimension) {
      function doSmoothScroll(scrollTop, callback) {
        $("body,html").animate({
          scrollTop: scrollTop
        }, 300, callback);
      }

      if (!Subject.isSubjectVisible(position, dimension)) {
        var description = StepDescription.singleInstance;
        var y = dimension.height > ($window.height() - 50) ? position.y : position.y - 25;
        y += $window.scrollTop();

        doSmoothScroll(y, function () {
          setTimeout(function () {
            DetailsPanel.singleInstance.positionate();
            description.positionate();
            description.fadeIn();
          }, 300);
        });

        return true;
      }
      return false;
    });

    /**
     Updates the positioning and dimension of each part composing the whole mask, according to the subject coordinates
     
     @method update
     @param {Object} position                              An object representing the positioning info for the mask
     @param {Object} dimension                             An object representing the dimension info for the mask
     @param {Object} borderRadius                          An object representing the borderRadius info for the mask
     **/
    Mask.CompositeMask.method("update", function (position, dimension, borderRadius) {
      Mask.SubjectMask.singleInstance.update(position, dimension, borderRadius);
      //Aliases
      var left = position.x,
          top = position.y,
          width = dimension.width,
          height = dimension.height,
          br = borderRadius;

      //Updates the divs surrounding the subject
      this.parts.top.update({
        x: 0,
        y: 0
      }, {
        width: $window.width(),
        height: top
      });
      this.parts.left.update({
        x: 0,
        y: top
      }, {
        width: left,
        height: height
      });
      this.parts.right.update({
        x: left + width,
        y: top
      }, {
        width: $window.width() - (left + width),
        height: height
      });
      this.parts.bottom.update({
        x: 0,
        y: top + height
      }, {
        width: $window.width(),
        height: $window.height() - (top + height)
      });

      //Updates the Rounded corners
      this.parts.leftTop.update({
        x: left,
        y: top
      }, br.leftTop);
      this.parts.rightTop.update({
        x: left + width - br.rightTop,
        y: top
      }, br.rightTop);
      this.parts.leftBottom.update({
        x: left,
        y: top + height - br.leftBottom
      }, br.leftBottom);
      this.parts.rightBottom.update({
        x: left + width - br.rightBottom,
        y: top + height - br.rightBottom
      }, br.rightBottom);
    });

    /**
     A Polling function to check if subject coordinates has changed
     
     @method pollForSubjectChanges
     **/
    Mask.CompositeMask.method("pollForSubjectChanges", function () {
      if (!flags.lockMaskUpdate) {
        if (currentWizard && currentWizard.currentStep.subject) {
          var subject = $(currentWizard.currentStep.subject);
          if (Subject.obj[0] !== subject[0]) SS.setSubject(subject, true);
        }

        if (Subject.hasChanged()) {
          Subject.updateInfo();
          this.update(Subject.position, Subject.dimension, Subject.borderRadius);
        }
      }
    });

    /**
     A Polling function to check if screen dimension has changed
     
     @method pollForScreenChanges
     **/
    Mask.CompositeMask.method("pollForScreenChanges", function () {
      if (Screen.hasChanged()) {
        Screen.updateInfo();
        this.update(Subject.position, Subject.dimension, Subject.borderRadius);
      }
    });

    /**
     A part composing the mask
     
     @class Part
     @@initializer 
     @param {Object} position                              The positioning information 
     @param {Object} dimension                             The dimension information 
     **/
    Mask.CompositeMask.Part = jazz.Class(function (position, dimension) {
      this.position = position;
      this.dimension = dimension;
    }).extending(VisualItem);



    /**
     @@alias Part
     @@to Mask.CompositeMask.Part
     **/
    var Part = Mask.CompositeMask.Part;

    /**
     An object holding positioning information for the mask part
     
     @@field position
     @type Object
     **/
    Part.field("position", {});

    /**
     An object holding dimension information for the mask part
     
     @@field position
     @type Object
     **/
    Part.field("dimension", {});

    /**
     Renders the mask part
     
     @method render
     **/
    Part.method("render", function () {
      this.$el = $("<div>").addClass("sideshow-mask-part").addClass("sideshow-hidden").addClass("sideshow-invisible");
      this.callSuper("render");
    });

    /**
     Updates the dimension and positioning of the subject mask part
     
     @method update
     @param {Object} position                              The positioning information 
     @param {Object} dimension                             The dimension information 
     **/
    Part.method("update", function (position, dimension) {
      this.position = position;
      this.dimension = dimension;
      this.$el.css("left", position.x).css("top", position.y).css("width", dimension.width).css("height", dimension.height);
    });

    /**
     A corner part composing the mask
     
     @class CornerPart
     @@initializer 
     @param {Object} position                              The positioning information 
     @param {Object} dimension                             The dimension information 
     **/
    Mask.CompositeMask.CornerPart = jazz.Class().extending(VisualItem);

    /**
     @@alias CornerPart
     @@to Mask.CompositeMask.CornerPart
     **/
    var CornerPart = Mask.CompositeMask.CornerPart;

    /**
     An object holding positioning information for the mask corner part
     
     @@field position
     @type Object
     **/
    CornerPart.field("position", {});

    /**
     An object holding dimension information for the mask corner part
     
     @@field position
     @type Object
     **/
    CornerPart.field("dimension", {});

    /**
     An object holding border radius information for the mask corner part
     
     @@field borderRadius
     @type Object
     **/
    CornerPart.field("borderRadius", 0);

    /**
     Formats the SVG path for the corner part
     
     @method SVGPathPointsTemplate
     @param {Number} borderRadius                          The corner part border radius
     @static
     **/
    CornerPart.static.SVGPathPointsTemplate = function (borderRadius) {
      return "m 0,0 0," + borderRadius + " C 0," + borderRadius * 0.46 + " " + borderRadius * 0.46 + ",0 " + borderRadius + ",0";
    };

    /**
     Renders the SVG for the corner part
     
     @method buildSVG
     @param {Number} borderRadius                          The corner part border radius
     @static
     **/
    CornerPart.static.buildSVG = function (borderRadius) {
      function SVG(nodeName) {
        return document.createElementNS("http://www.w3.org/2000/svg", nodeName);
      }

      var bezierPoints = this.SVGPathPointsTemplate(borderRadius);
      var $svg = $(SVG("svg"));
      var $path = $(SVG("path"));

      $path.attr("d", bezierPoints);
      $svg.append($path);

      return $svg[0];
    };

    /**
     Renders the mask corner part
     
     @method render
     @return {Object}                                      The corner part jQuery wrapped DOM element
     **/
    CornerPart.prototype.render = function () {
      this.$el = $("<div>").addClass("sideshow-mask-corner-part").addClass("sideshow-hidden").addClass("sideshow-invisible");
      this.$el.append(CornerPart.buildSVG(this.borderRadius));
      $body.append(this.$el);
      return this.$el;
    };

    /**
     Updates the positioning and border radius of the mask corner part
     
     @method update
     @param {Object} position                              The positioning information 
     @param {Object} borderRadius                          The border radius information 
     **/
    CornerPart.prototype.update = function (position, borderRadius) {
      this.$el.css("left", position.x).css("top", position.y).css("width", borderRadius).css("height", borderRadius);

      $(this.$el).find("path").attr("d", CornerPart.SVGPathPointsTemplate(borderRadius));
    };

    /**
     Controls the polling functions needed by Sideshow
     
     @class Polling
     @static
     **/
    var Polling = {};

    /**
     The polling functions queue
     
     @@field queue
     @type Object
     @static
     **/
    Polling.queue = [];

    /**
     A flag that controls if the polling is locked
     
     @@field lock
     @type boolean
     @static
     **/
    Polling.lock = false;

    /**
     Pushes a polling function in the queue
     
     @method enqueue
     @static
     **/
    Polling.enqueue = function () {
      var firstArg = arguments[0];
      var fn;
      var name = "";

      if (typeof firstArg == "function") fn = firstArg;
      else {
        name = arguments[0];
        fn = arguments[1];
      }

      if (this.getFunctionIndex(fn) < 0 && (name === "" || this.getFunctionIndex(name) < 0)) {
        this.queue.push({
          name: name,
          fn: fn,
          enabled: true
        });
      } else throw new SSException("301", "The function is already in the polling queue.");
    };

    /**
     Removes a polling function from the queue
     
     @method dequeue
     @static
     **/
    Polling.dequeue = function () {
      this.queue.splice(this.getFunctionIndex(arguments[0]), 1);
    };

    /**
     Enables an specific polling function
     
     @method enable
     @static
     **/
    Polling.enable = function () {
      this.queue[this.getFunctionIndex(arguments[0])].enabled = true;
    }

    /**
     Disables an specific polling function, but preserving it in the polling queue 
     
     @method disable
     @static
     **/
    Polling.disable = function () {
      this.queue[this.getFunctionIndex(arguments[0])].enabled = false;
    }

    /**
     Gets the position of a polling function in the queue based on its name or the function itself
     
     @method getFunctionIndex
     @static
     **/
    Polling.getFunctionIndex = function () {
      var firstArg = arguments[0];

      if (typeof firstArg == "function") return this.queue.map(function (p) {
        return p.fn;
      }).indexOf(firstArg);
      else if (typeof firstArg == "string") return this.queue.map(function (p) {
        return p.name;
      }).indexOf(firstArg);

      throw new SSException("302", "Invalid argument for getFunctionIndex method. Expected a string (the polling function name) or a function (the polling function itself).");
    }

    /**
     Unlocks the polling and starts the checking process
     
     @method start
     @static
     **/
    Polling.start = function () {
      this.lock = false;
      this.doPolling();
    };

    /**
     Stops the polling process
     
     @method stop
     @static
     **/
    Polling.stop = function () {
      this.lock = true;
    };

    /**
     Clear the polling queue
     
     @method clear
     @static
     **/
    Polling.clear = function () {
      var lock = this.lock;

      this.lock = true;
      this.queue = [];
      this.lock = lock;
    };

    /**
     Starts the polling process  
     
     @method doPolling
     @static
     **/
    Polling.doPolling = function () {
      if (!this.lock) {
        //Using timeout to avoid the queue to not complete in a cycle
        setTimeout(function () {
          for (var fn = 0; fn < Polling.queue.length; fn++) {
            var pollingFunction = Polling.queue[fn];
            pollingFunction.enabled && pollingFunction.fn();
          }
          Polling.doPolling();
        }, pollingDuration);
      }
    };

    /**
     The main menu, where the available wizards are listed
     
     @class WizardMenu
     @static
     **/
    var WizardMenu = {};

    /**
     Renders the wizard menu
     
     @method render
     @param {Array} wizards                                The wizards list
     @static
     **/
    WizardMenu.render = function (wizards) {
      var $menu = $("<div>").addClass("sideshow-wizard-menu");
      this.$el = $menu;
      var $title = $("<h1>").addClass("sideshow-wizard-menu-title");
      $menu.append($title);

      if (wizards.length > 0) {
        var $wizardsList = $("<ul>");

        //Extracting this function to avoid the JSHint warning W083


        function setClick($wiz, wizard) {
          $wiz.click(function () {
            WizardMenu.hide(function () {
              wizard.prepareAndPlay();
            });
          });
        }

        for (var w = 0; w < wizards.length; w++) {
          var wiz = wizards[w];
          var $wiz = $("<li>");
          var $wizTitle = $("<h2>").text(wiz.title);

          if (wiz.title || wiz.description) {
            var description = wiz.description;
            description.length > 100 && (description = description.substr(0, 100) + "...");

            var $wizDescription = $("<span>").addClass("sideshow-wizard-menu-item-description").text(description);
            var $wizEstimatedTime = $("<span>").addClass("sideshow-wizard-menu-item-estimated-time").text(wiz.estimatedTime);
            $wiz.append($wizEstimatedTime, $wizTitle, $wizDescription);
            $wizardsList.append($wiz);
          }
          setClick($wiz, wiz);
        }
        $menu.append($wizardsList);
      } else {
        $("<div>").addClass("sideshow-no-wizards-available").text(getString(strings.noAvailableWizards)).appendTo($menu);
      }

      $body.append($menu);
    };

    /**
     Shows the wizard menu
     
     @method show
     @param {Array} wizards                                The wizards list
     @static
     **/
    WizardMenu.show = function (wizards, title) {
      if (wizards.length == 1 && SS.config.autoSkipIntro) wizards[0].prepareAndPlay();
      else {
        SS.setEmptySubject();
        Mask.CompositeMask.singleInstance.update(Subject.position, Subject.dimension, Subject.borderRadius);
        Mask.CompositeMask.singleInstance.fadeIn();

        WizardMenu.render(wizards);

        if (title) this.setTitle(title);
        else this.setTitle(getString(strings.availableWizards));
      }
    };

    /**
     Hides the wizard menu
     
     @method hide
     @param {Function} callback                            The callback to be called after hiding the menu
     @static
     **/
    WizardMenu.hide = function (callback) {
      var menu = this,
          $el = menu.$el;

      $el && $el.addClass("sideshow-menu-closed");
      setTimeout(function () {
        $el && $el.hide();
        if (callback) callback();
      }, longAnimationDuration);
    };

    WizardMenu.setTitle = function (title) {
      this.$el.find(".sideshow-wizard-menu-title").text(title);
    };


    /**
     Initializes Sideshow
     
     @method init
     @static
     **/
    SS.init = function () {
      $window = $(global);
      $document = $(global.document);
      $body = $("body", global.document);
      registerGlobalHotkeys();
      Polling.start();
      Mask.CompositeMask.singleInstance.init();
      flags.lockMaskUpdate = true;
      Mask.CompositeMask.singleInstance.render();
    };

    /**
     Receives a function with just a multiline comment as body and converts to a here-document string
     
     @method heredoc
     @param {Function}                                     A function without body but a multiline comment
     @return {String}                                      A multiline string
     @static
     **/
    SS.heredoc = function (fn) {
      return fn.toString().match(/[^]*\/\*([^]*)\*\/\}$/)[1];
    }

    /**
     Stops and Closes Sideshow
     
     @method closes
     @static
     **/
    SS.close = function () {
      if (!currentWizard) WizardMenu.hide();

      DetailsPanel.singleInstance.fadeOut();

      this.CloseButton.singleInstance.fadeOut();
      Arrows.fadeOut();

      setTimeout(function () {
        if (Mask.CompositeMask.singleInstance.status === AnimationStatus.VISIBLE || Mask.CompositeMask.singleInstance.status === AnimationStatus.FADING_IN) Mask.CompositeMask.singleInstance.fadeOut();

        Mask.SubjectMask.singleInstance.fadeOut();

      }, longAnimationDuration);

      removeDOMGarbage();
      Polling.clear();
      SS.ControlVariables.clear();
      unregisterInnerHotkeys();
      currentWizard = null;
      flags.running = false;
    };

    /**
     @deprecated
     @method runWizard
     @static
     **/
    SS.runWizard = function (name) {
      showDeprecationWarning("This method is deprecated and will be removed until the next major version of Sideshow.");

      var wiz = wizards.filter(function (w) {
        return w.name === name
      })[0];
      currentWizard = wiz;
      if (wiz) {
        if (wiz.isEligible()) wiz.play();
        else if (wiz.preparation) wiz.preparation(function () {
          setTimeout(function () {
            wiz.play();
          }, 1000);
        });
        else throw new SSException("204", "This wizard hasn't preparation.");
      } else throw new SSException("205", "There's no wizard with name " + name + ".");
    };

    SS.gotoStep = function () {
      var firstArg = arguments[0],
          steps = currentWizard._storyline.steps,
          destination;

      flags.skippingStep = true;

      //First argument is the step position (1-based)
      if (typeof firstArg == "number") {
        if (firstArg <= steps.length) destination = steps[firstArg - 1];
        else throw new SSException("401", "There's no step in the storyline with position " + firstArg + ".");
      } //First argument is the step name
      else if (typeof firstArg == "string") {
        destination = steps.filter(function (i) {
          return i.name === firstArg;
        })[0];

        if (!destination) throw new SSException("401", "There's no step in the storyline with name " + firstArg + ".");
      }
      setTimeout(function () {
        currentWizard.next(null, destination);
      }, 100);
    };

    /**
     A trick to use the composite mask to simulate the behavior of a solid mask, setting an empty subject
     
     @method setEmptySubject
     @static
     **/
    SS.setEmptySubject = function () {
      flags.lockMaskUpdate = true;
      Subject.obj = null;
      Subject.updateInfo({
        dimension: {
          width: 0,
          height: 0
        },
        position: {
          x: 0,
          y: 0
        },
        borderRadius: {
          leftTop: 0,
          rightTop: 0,
          leftBottom: 0,
          rightBottom: 0
        }
      });
    };

    /**
     Sets the current subject
     
     @method setSubject
     @param {Object} subj
     @static
     **/
    SS.setSubject = function (subj, subjectChanged) {
      if (subj.constructor === String) subj = $(subj);

      if (subj instanceof $ && subj.length > 0) {
        if (subj.length === 1) {
          Subject.obj = subj;
          Subject.updateInfo();
          flags.lockMaskUpdate = false;
        } else throw new SSException("101", "A subject must have only one element. Multiple elements by step will be supported in future versions of Sideshow.");
      }
      else if (subjectChanged) SS.setEmptySubject();
      else throw new SSException("100", "Invalid subject.");
    };

    /**
     Registers a wizard
     
     @method registerWizard
     @param {Object} wizardConfig                          
     @return {Object}                                      The wizard instance
     @static
     **/
    SS.registerWizard = function (wizardConfig) {
      var wiz = Wizard.build(wizardConfig);
      wizards.push(wiz);
      return wiz;
    };

    /**
     Registers a wizard
     
     @method registerWizard
     @param {boolean} onlyNew                              Checks only recently added wizards
     @return {Array}                                       The eligible wizards list
     @static
     **/
    SS.getElegibleWizards = function (onlyNew) {
      var eligibleWizards = [];
      var somethingNew = false;
      for (var w = 0; w < wizards.length; w++) {
        var wiz = wizards[w];
        if (wiz.isEligible()) {
          if (!wiz.isAlreadyWatched()) somethingNew = true;
          eligibleWizards.push(wiz);
        }
      }

      return !onlyNew || somethingNew ? eligibleWizards : [];
    };

    /**
     Checks if there are eligible wizards, if exists, shows the wizard menu   
     
     @method showWizardsList
     @param {boolean} onlyNew                              Checks only recently added wizards
     @return {boolean}                                     Returns a boolean indicating whether there is some wizard available
     @static
     **/
    SS.showWizardsList = function () {
      var firstArg = arguments[0];
      var title = arguments[1];
      var onlyNew = typeof firstArg == "boolean" ? false : firstArg;
      var wizards = firstArg instanceof Array ? firstArg : this.getElegibleWizards(onlyNew);

      WizardMenu.show(wizards, title);

      return wizards.length > 0;
    };

    /**
     Shows a list with the related wizards  
     
     @method showRelatedWizardsList
     @param {Object} completedWizard                       The recently completed wizard
     @return {boolean}                                     Returns a boolean indicating whether there is some related wizard available
     @static
     **/
    SS.showRelatedWizardsList = function (completedWizard) {
      var relatedWizardsNames = completedWizard.relatedWizards;
      if (!relatedWizardsNames) return false;

      //Gets only related tutorials which are eligible or have a preparation function
      var relatedWizards = wizards.filter(function (w) {
        return relatedWizardsNames.indexOf(w.name) > -1 && (w.isEligible() || w.preparation);
      });
      if (relatedWizards.length == 0) return false;

      Polling.clear();
      SS.ControlVariables.clear();
      SS.showWizardsList(relatedWizards, getString(strings.relatedWizards));

      return true;
    };

    /**
     The close button for the wizard
     
     @class CloseButton
     @@singleton
     @extends FadableItem
     **/
    SS.CloseButton = jazz.Class().extending(FadableItem).singleton;

    /**
     Renders the close button
     
     @method render
     **/
    SS.CloseButton.method("render", function () {
      this.$el = $("<button>").addClass("sideshow-close-button").text(getString(strings.close));
      this.$el.click(function () {
        SS.close();
      });
      this.callSuper("render");
    });

    /**
     Starts Sideshow
     
     @method start
     @param {Object} config                                The config object for Sideshow
     **/
    SS.start = function (config) {
      config = config || {};

      if (!flags.running) {
        var onlyNew = "onlyNew" in config && !! config.onlyNew;
        var listAll = "listAll" in config && !! config.listAll;
        var wizardName = config.wizardName;

        if (listAll) SS.showWizardsList(wizards.filter(function (w) {
          return w.isEligible() || w.preparation;
        }));
        else if (wizardName) {
          var wizard = wizards.filter(function (w) {
            return w.name === wizardName;
          })[0];

          if (!wizard) throw new SSException("205", "There's no wizard with name '" + wizardName + "'.");

          wizard.prepareAndPlay();
        }
        else SS.showWizardsList(onlyNew);

        this.CloseButton.singleInstance.render();
        this.CloseButton.singleInstance.fadeIn();

        registerInnerHotkeys();
        flags.running = true;

        Polling.enqueue("check_composite_mask_screen_changes", function () {
          Mask.CompositeMask.singleInstance.pollForScreenChanges();
        });
      }
    };




    //Tries to register the Global Access Point
    if (global[globalObjectName] === undefined) {
      global[globalObjectName] = SS;
    } else throw new SSException("1", "The global access point \"Sideshow\" is already being used.");
  });
})(this, jQuery, Jazz, Markdown);