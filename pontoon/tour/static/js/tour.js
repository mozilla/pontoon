$(function () {
  // Run the tour only on project with slug 'tutorial'
  if (Pontoon.state.project !== "tutorial") {
    return;
  }

  var isSubmitClicked = false;

  var tourStatus = Number($('#server').data('tour-status') || 0);

  var submitTarget = "#editor #single button#save";
  var submitText = "A user needs to be logged in to be able to submit " +
  "translations. Non-authenticated users will see a link to Sign in " +
  "instead of the translation toolbar with a button to save translations.";

  // Translators
  if (Pontoon.user.canTranslate()) {
    submitText = "If a translator has permission to add translations " +
    "directly, the green SAVE button will appear in the translation " +
    "toolbar. To submit a translation, type it in the translation input and " +
    "click SAVE.";
  }
  // Contributors
  else if (Pontoon.user.id) {
    submitText = "When a translator is in Suggest Mode, or doesn’t have " +
    "permission to submit translations directly, a blue SUGGEST button " +
    "will appear in the translation toolbar. To make a suggestion, type it " +
    "in the translation input and click SUGGEST.";
  }
  // Non-authenticated users
  else {
    submitTarget = null;
  }

  var updateTourStatus = function (step) {
    if (Pontoon.user.id) {
      $.ajax({
        url: "/update-tour-status/",
        type: "POST",
        data: {
          csrfmiddlewaretoken: $("#server").data("csrf"),
          tour_status: step
        },
        success: function(data) {
          return data;
        }
      });
    }
  };


  Sideshow.registerWizard({
    name: "introducing_pontoon",
    title: "Introducing Pontoon",
    description: "Introducing the translate page of Pontoon.",
    affects: [
      function() {
        return true;
      }
    ],
    listeners: {
        beforeWizardStarts: function(){
          // unbind all keydown handelers.
          $('html').off('keydown');
          $('#editor').off('keydown');
        },
        afterWizardEnds: function(){
          // rebind all keydown handelers back.
          $('html').unbind("keydown.pontoon").bind("keydown.pontoon", generalKeys);
          $('html').on('keydown', traversalKeys);
          translateAreaKeys();
        }
    }
  }).storyLine({
    showStepPosition: true,
    steps: [
      {
        title: "Hey there!",
        text:
          "Pontoon is a localization platform by Mozilla, used to localize " +
          "Firefox and various other projects at Mozilla.<br />" +
          "Follow this guide to learn how to use it.",
        format: "markdown",
        listeners: {
          beforeStep: function() {
            // Take the user directly to next step of where he left.
            if (tourStatus !== 0) {
              Sideshow.gotoStep(tourStatus+1);
            }
          },
          afterStep: function() {
            if (tourStatus === 0) {
              updateTourStatus(++tourStatus);
            }
          }
        },
      },
      {
        title: "Main toolbar",
        text:
          "The main toolbar located on top of the screen allows you to " +
          "navigate among languages, projects and resources. You can also " +
          "see the progress of your current localization and additional " +
          "project information." +
          "<br /><br />" +
          "On the right hand side, logged in users can access notifications " +
          "and settings.",
        subject: "div.container.clearfix",
        format: "markdown",
        lockSubject: true,
        listeners: {
          afterStep: function() {
            updateTourStatus(++tourStatus);
          }
        },
      },
      {
        title: "String List",
        text:
          "The sidebar displays a list of strings in the current " +
          "localization. Status of each string (e.g. Translated or Missing) " +
          "is indicated by a different color of the square on the left. The " +
          "square also acts as a checkbox for selecting strings to perform " +
          "mass actions on." +
          "<br /><br />" +
          "On top of the list is a search box, which allows you to search " +
          "source strings, translations, comments and string IDs.",
        subject: "#entitylist",
        format: "markdown",
        lockSubject: true,
        listeners: {
          beforeStep: function() {
            // rebind string list events back.
            $('html').unbind("keydown.pontoon").bind("keydown.pontoon", generalKeys);
            $('html').on('keydown', traversalKeys);
          },
          afterStep: function() {
            $('html').off('keydown');
            updateTourStatus(++tourStatus);
          }
        },
      },
      {
        title: "Filters",
        text:
          "Strings can also be filtered by their status, translation time, " +
          "translation authors and other criteria. Note that filter icons " +
          "act as checkboxes, which allows you to filter by multiple " +
          "criteria.",
        subject: "#filter .menu",
        targets: "#filter .menu",
        format: "markdown",
        lockSubject: true,
        listeners: {
          beforeStep: function() {
            $("#filter div.button").click();
            $("#filter .menu").addClass("permanent");
          },
          afterStep: function() {
            $("#filter .menu").removeClass("permanent");
            $("#filter .menu").css("display", "none");
            updateTourStatus(++tourStatus);
          }
        }
      },
      {
        title: "Editor",
        text:
          "Clicking a string in the list opens it in the editor. On top of " +
          "it, you can see the source string with its context. Right under " +
          "that is the translation input to type translation in, followed " +
          "by the translation toolbar.",
        subject: "#editor #single",
        format: "markdown",
        lockSubject: true,
        listeners: {
          beforeStep: function() {
            // rebind editor keydowns back
            translateAreaKeys();
          },
          afterStep: function() {
            $('#editor').off('keydown');
            updateTourStatus(++tourStatus);
          }
        },
      },
      {
        title: "Submit a Translation",
        text: submitText,
        subject: "#editor #single",
        format: "markdown",
        autoContinue: true,
        showNextButton: true,
        targets: submitTarget,
        completingConditions: [
          function() {
            $("#editor #single button#save").click(function() {
              isSubmitClicked = true;
            });
            return isSubmitClicked;
          }
        ],
        listeners: {
          beforeStep: function() {
            // Bind editor keydowns back
            translateAreaKeys();
          },
          afterStep: function() {
            $('#editor').off('keydown');
            updateTourStatus(++tourStatus);
          }
        },
      },
      {
        title: "History",
        text:
          "All suggestions and translations submitted for the current " +
          "string can be found in the History Tab. Icons to the right of " +
          "each entry indicate its review status (Approved, Rejected or " +
          "Unreviewed).",
        subject: "#helpers",
        format: "markdown",
        targets: "#helpers.tabs nav li:nth-child(1)",
        listeners: {
          beforeStep: function() {
            $("#entitylist .uneditables li:nth-child(3)").click();
          },
          afterStep: function() {
            updateTourStatus(++tourStatus);
          }
        },
      },
      {
        title: "Machinery",
        text:
          "The Machinery tab shows automated translation suggestions from " +
          "Machine Translation, Translation Memory and Terminology " +
          "services. Clicking on an entry copies it to the translation " +
          "input.",
        subject: "#helpers",
        format: "markdown",
        targets: "#helpers.tabs nav li:nth-child(2)",
        listeners: {
          beforeStep: function() {
            $("#helpers.tabs nav li")[1].firstElementChild.click();
          },
          afterStep: function() {
            updateTourStatus(++tourStatus);
          }
        },
      },
      {
        title: "Inspiration from other languages",
        text:
          "Sometimes it's useful to see general style choices by other " +
          "localization communities. Approved translations of the current " +
          "string to other languages are available in the Locales tab.",
        subject: "#helpers",
        format: "markdown",
        targets: "#helpers.tabs nav li:nth-child(3)",
        listeners: {
          beforeStep: function() {
            $("#helpers.tabs nav li")[2].firstElementChild.click();
          },
          afterStep: function() {
            updateTourStatus(++tourStatus);
          }
        },
      },
      {
        title: "That's (not) all, folks!",
        text:
          "There's a wide variety of tools to help you with translations, " +
          "some of which we didn't mention in this tutorial. For more " +
          "topics of interest for localizers at Mozilla, please have a look " +
          "at the [Localizer Documentation]" +
          "(https://mozilla-l10n.github.io/localizer-documentation/)." +
          "<br /><br />" +
          "Next, feel free to explore this tutorial project or move straight to " +
          "translating live projects!",
        format: "markdown",
        listeners: {
          afterStep: function() {
            updateTourStatus(-1);
          }
        },
      }
    ]
  });

  // Run the tour only if not completed by user
  if (tourStatus !== -1) {
    Sideshow.start({ listAll: true });

    // If a user closes the tour at the "Filter" step,
    // run the corresponding afterStep function.
    $('.sideshow-close-button').click(function() {

      // bind all keydown handelers back.
      $('html').unbind("keydown.pontoon").bind("keydown.pontoon", generalKeys);
      $('html').on('keydown', traversalKeys);
      translateAreaKeys();

      setTimeout(function() {
        $("#filter .menu").fadeOut(function() {
          $("#filter .menu").removeClass("permanent");
        });
      }, 100);
    });
  }
});
