This project is based on create-react-app. See the documentation.

# Integration with django

The setup we use is based on this blog post:
https://fractalideas.com/blog/making-react-and-django-play-well-together-hybrid-app-model/

## Production

Build static files with `yarn build`. django is configured to collect the
`index.html` and static files from the `build` folder.

## Development

If you're using docker, `make run` automatically starts both a webpack server
(on port 3000) and a django server (on port 8000). django is the server you want
to hit, and it will then proxy appropriate requests to the webpack server.

### Enable websocket and warm-reloading

Currently websocket requests are redirect by django to the webpack server.
Sadly, by default major browsers do not support websocket redirection. To
enable it in Firefox, go to `about:config` and turn
`network.websocket.auto-follow-http-redirect` to `true`. Note that there is
a bug filed to get rid of that option entirely:
https://bugzilla.mozilla.org/show_bug.cgi?id=1052909
