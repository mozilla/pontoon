//A Sideshow Tutorial Example
//This tutorial introduces the Sideshow basics to the newcomer
var is_entity_clicked = false;
var is_submit_clicked = false;
Sideshow.registerWizard({
  name: "introducing_pontoon",
  title: "Introducing Pontoon",
  description: "Introducing the main features of translate page of Pontoon. ",
  affects: [
    function() {
      //Here we could do any checking to infer if this tutorial is eligible the current screen/context.
      //After this checking, just return a boolean indicating if this tutorial will be available.
      //As a simple example we're returning a true, so this tutorial would be available in any context
      return true;
    }
  ]
}).storyLine({
  showStepPosition: true,
  steps: [
    {
      title: "Hey there!",
      text: "Pontoon is a web-based, What-You-See-Is-What-You-Get (WYSIWYG), " +
            "localization (l10n) tool. At Mozilla, we currently use Pontoon " +
            "to localize various Mozilla project."
    },
    {
      title: "Main toolbar",
      text: "The main toolbar allows you to navigate between projects without " +
            "leaving the translation workspace",
      subject: "div.container.clearfix",
      format: "markdown",
      lockSubject: true
    },
    {
      title: "Project information",
      text: "An overview of the status of the selected resource is located to " +
            "the right of the main toolbar. Translators can view information " +
            "regarding the project, its priority level, and testing by clicking the icon.",
      subject: "#progress .menu",
      targets: "#progress",
      format: "markdown",
      listeners: {
        beforeStep: function() {
          $("#progress .menu").css("display", "block");
        }
      }
    },
    {
      title: "Sidebar",
      text: "The sidebar displays the list of strings in the current project " +
            "resource. Each string is displayed with the string status "+
            "(i.e. Missing, Translated, etc.) identified by a colored square.",
      subject: "#entitylist",
      format: "markdown",
      lockSubject: true
    },
    {
      title: "Entity",
      text: "Selecting an entity by clicking it opens up the editor.",
      subject: "#entitylist .uneditables li:nth-child(3)",
      format: "markdown",
      autoContinue: false,
      targets: "#entitylist .uneditables li:nth-child(3)",
      completingConditions: [
        function() {
          $("#entitylist .uneditables li:nth-child(3)").click(function() {
            is_entity_clicked = true;
          });
          $(".sideshow-next-step-button").attr("disabled", null);
          return is_entity_clicked;
        }
      ]
    },
    {
      title: "Editor",
      text: "The translation workspace is where strings are translated.",
      subject: "#editor #single",
      format: "markdown",
      lockSubject: true
    },
    {
      title: "Submit a suggestion",
      text: "When a translator is in Suggest Mode, or doesn’t have permissions" +
            " to submit translations directly, a blue SUGGEST button will " +
            "be visible in the lower-right side of the editing space. To " +
            "suggest a translation, simply input the translation to the " +
            "editing space and click SUGGEST",
      subject: "#editor #single",
      format: "markdown",
      autoContinue: false,
      targets: "#editor #single button#save",
      completingConditions: [
        function() {
          $("#editor #single button#save").click(function() {
            is_submit_clicked = true;
          });
          $(".sideshow-next-step-button").attr("disabled", null);
          return is_submit_clicked;
        }
      ]
    },
    {
      title: "Entity",
      text: "Once the translator has suggested the translation, the " +
            "suggestion will appear in the sidebar. In case of multiple " +
            "suggestions, sidebar will show the most recent one.",
      subject: "#helpers",
      format: "markdown",
      targets: "#helpers section.history",
      listeners: {
        beforeStep: function() {
          $("#entitylist .uneditables li:nth-child(3)").click();
        }
      }
    },
    {
      title: "That's (NOT) all, folks!",
      text: "There's a wide variety of tools to help you with translations, " +
            "some of which we didn't mention in this introductory tutorial. " +
            "<br> Feel free to explore this demo project to know about these  " +
            "or move forward to translate some live projects.",
      format: "markdown"
    }
  ]
});

if(Pontoon.state.project=='demo'){
  Sideshow.start({ listAll: true });
}
