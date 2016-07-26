Integration
===========

The following is a list of mechanism that can help you to integrate your website/app
with pontoon.

Event-driven integration
------------------------
Pontoon exposes various events that can be handled jQuery callbacks.
Following code will call an alert window when your page is called inside Pontoon Editor:

.. code-block:: javascript

   $(function() {
     $(document).on('pontoonInit', function() {
       alert('Hello world!');
     });
   });

Supported jQuery Events
---------------------------
Pontoon exposes following events:
* `pontoonInit` is called when the Pontoon is fully initialized and the Pontoon object is accessible for the javascript Api.
* `pontoonSave` is executed after user saves new translation and Pontoon updates it on your site.
