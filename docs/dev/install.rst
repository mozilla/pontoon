Developer Setup
===============
1. `Install Docker and Compose`_.

2. Clone this repository or your fork_:

   .. code-block:: bash

      git clone --recursive https://github.com/mozilla/pontoon.git
      cd pontoon

3. **Optional**: If you're running the site via boot2docker_, you'll want to add
   a ``.env`` file to the project's root director with the IP address of the
   boot2docker VM.

   .. code-block:: bash

      echo "SITE_URL=http://$(boot2docker ip):8000" > .env

4. Build the development instance using the build script:

   .. code-block:: bash

      boot2docker up
      eval "$(boot2docker shellinit)"
      ./bin/build-docker.sh


Once you've finished these steps, you should be able to start the site by
running:

.. code-block:: bash

   docker-compose up

If you're running Docker directly (via Linux), the site should be available at
http://localhost:8000. If you're running boot2docker, the site should be
available on port 8000 at the IP output by running:

.. code-block:: bash

   boot2docker ip

For admin_ access, create admin account with:

.. code-block:: bash

   docker-compose run web ./manage.py createsuperuser

.. _Install Docker and Compose: https://docs.docker.com/compose/install/
.. _fork: http://help.github.com/fork-a-repo/
.. _boot2docker: http://boot2docker.io/
.. _admin: http://localhost:8000/admin/

Local settings
--------------
The following settings can be set by creating a `.env` file in root directory of
your pontoon repo and adding their values:

```
MICROSOFT_TRANSLATOR_API_KEY=microsoft-key
GOOGLE_ANALYTICS_KEY=google-key
MOZILLIANS_API_KEY=mozillians-key
```

``MICROSOFT_TRANSLATOR_API_KEY``
   Set your `Microsoft Translator API key`_ to use machine translation.
``GOOGLE_ANALYTICS_KEY``
   Set your `Google Analytics key`_ to use Google Analytics.
``MOZILLIANS_API_KEY``
   Set your `Mozillians API key`_ to grant permission to Mozilla localizers.

.. _Microsoft Translator API key: http://msdn.microsoft.com/en-us/library/hh454950
.. _Google Analytics key: https://www.google.com/analytics/
.. _Mozillians API key: https://wiki.mozilla.org/Mozillians/API-Specification
