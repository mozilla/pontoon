# Docker

The local development of Pontoon using docker is documented at [developer setup](http://mozilla-pontoon.readthedocs.io/en/latest/dev/setup.html).

The portable Docker image for production use is in progress. You can find it in this folder as `Dockerfile.prod`.

It should support all of the same environment variables supported by Heroku, with one caveat:
* `SSH_KEY` is assumed to be an `id_rsa` file that has been base64 encoded. This permits the enviroment variable to live as a string in more contexts
