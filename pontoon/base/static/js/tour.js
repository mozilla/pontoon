//A Sideshow Tutorial Example
//This tutorial introduces the Sideshow basics to the newcomer
var a = false;
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
      title: "Hey there!.",
      text:
        "Pontoon is a web-based, What-You-See-Is-What-You-Get (WYSIWYG), localization (l10n) tool. At Mozilla, we currently use Pontoon to localize various Mozilla project"
    },
    {
      title: "Main toolbar",
      text:
        "The main toolbar allows you to navigate between projects without leaving the translation workspace",
      subject: "div.container.clearfix",
      format: "markdown",
      lockSubject: true,
    },
    {
      title: "Project information",
      text:
        'An overview of the status of the selected resource is located to the right of the main toolbar. Translators can view information regarding the project, its priority level, and testing by clicking the icon.',
      subject: "#progress .menu",
      targets: "#progress",
      format: "markdown",
       listeners: {
        beforeStep: function() {
          $("#progress .menu").css('display', 'block');
      },
    },
  },
     {
      title: "Sidebar",
      text:
        "The sidebar displays the list of strings in the current project resource.<br> Each string is displayed with the string status (i.e. Missing, Translated, etc.) identified by a colored square, the source string, <br> and the approved translation or the most recent suggestion if available",
      subject: "#entitylist",
      format: "markdown",
      lockSubject: true,
    },
     {
      title: "Entity",
      text:
        "Selecting an entity by clicking it opens up the editor.",
      subject: "#entitylist .uneditables li:nth-child(3)",
      format: "markdown",
      autoContinue: true,
      targets: "#entitylist .uneditables li:nth-child(3)",
      completingConditions: [
        function() {
            $("#entitylist .uneditables li:nth-child(3)").click(function(){
              a = true;
            });
            return a;
        }
      ]
    },
     {
      title: "Editor",
      text:
        "The translation workspace is where strings are translated.",
      subject: "#editor #single",
      format: "markdown",
      lockSubject: true,
    },
    {
      title: "That's (NOT) all, folks!",
      text:
        "There's a wide variety of interesting features in this version of Sideshow, some of which we didn't mention in this introductory tutorial. Take this sample, the documentation, open your favorite editor for Javascript and play at will!"
    }
  ]
});

$(document).ready(function() {
  setTimeout(function() {
    Sideshow.start({ listAll: true });
  }, 1000);
});
