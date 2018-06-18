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


# Development resources

On the integration between Django and React:

- [Making React and Django play well together — Fractal Ideas](https://fractalideas.com/blog/making-react-and-django-play-well-together/)
- [Making React and Django play well together - the “hybrid app” model — Fractal Ideas](https://fractalideas.com/blog/making-react-and-django-play-well-together-hybrid-app-model/)

On front-end code architecture:

- [Three Rules For Structuring (Redux) Applications — Jack Hsu](https://jaysoo.ca/2016/02/28/organizing-redux-application/)
- [The Anatomy Of A React & Redux Module (Applying The Three Rules) — Jack Hsu](https://jaysoo.ca/2016/02/28/applying-code-organization-rules-to-concrete-redux-code/)
- [Additional Guidelines For (Redux) Project Structure — Jack Hsu](https://jaysoo.ca/2016/12/12/additional-guidelines-for-project-structure/)

Tools documentation:

- [Redux](https://redux.js.org/)
- [create-react-app](https://github.com/facebook/create-react-app/blob/master/packages/react-scripts/template/README.md)
