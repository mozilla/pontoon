# Translate.Next — a better Translate app for Pontoon


## Tools

<table>
    <tr>
        <td>Bootstrapper</td>
        <td>create-react-app — https://github.com/facebook/create-react-app</td>
    </tr>
    <tr>
        <td>Package manager</td>
        <td>Yarn — https://yarnpkg.com/</td>
    </tr>
    <tr>
        <td>Views</td>
        <td>React — https://reactjs.org/</td>
    </tr>
    <tr>
        <td>Data</td>
        <td>Redux — https://redux.js.org/</td>
    </tr>
    <tr>
        <td>Tests</td>
        <td>Jest — http://jestjs.io/</td>
    </tr>
    <tr>
        <td>Type checking</td>
        <td>Flow — https://flow.org/</td>
    </tr>
    <tr>
        <td>Localization</td>
        <td>Fluent — https://projectfluent.org/</td>
    </tr>
    <tr>
        <td>Style</td>
        <td>CSS</td>
    </tr>
</table>


## Code architecture

### Where code goes

`src/core/` contains features that are shared in the application, in the form of modules. There should be as little code as possible in this folder.

`src/modules/` contains the self-contained features of the application, separated in modules.

`src/rootReducer.js` creates the main reducer to be used with Redux. When adding a new module with a reducer, make sure to include that reducer to `rootReducer`.

### Modules

Each module should be in a folder and have an `index.js` file that serves as the module's public interface. Outside of the module, always import from the module's index, and never from specific files. This allows us to easily evolve modules and keep things decoupled, which reduces code complexity.

Here are the files commonly found in a module:

- `index.js` — public interface of the module
- `actions.js` — actions that can be used to fetch data from an API, trigger changes, etc.
- `reducer.js` — a single Redux reducer (if you need to have more than one reducer, you probably actually need to make several modules)
- `constants.js` — a list of constants required by the module or other modules. It is recommended to expose a `NAME` constant here, that will contain the key to use to expose the reducer in the global store.
- `components/` — a folder containing components, with file names in CamelCase

Of course, more can be added if needed. For example, modules with a high number of action types might want to have an `actionTypes.js` file to separate them from actions.


## Running and deploying

### This feature is behind a Switch

While this is under development, the feature is hidden behing a feature switch, and thus is not accessible by default. In order to turn it on, you have to run `./manage.py waffle_switch translate_next on --create`, then restart your web server. To turn it off, run `./manage.py waffle_switch translate_next off`.

### Production

The only required step for the front-end is to build static files with `yarn build`. Django is configured to collect the `index.html` and static files from the `build` folder and put them with other static files. All of that is automated for deployement to Heroku.

### Development

If you're using docker, `make run` automatically starts both a webpack server (on port 3000) and a Django server (on port 8000). Django is the server you want to hit, and it will then proxy appropriate requests to the webpack server.

A common case during development is to have 3 terminals open: one for the dev servers, one for the tests and one for Flow:

    # terminal 1
    $ make run

    # terminal 2
    $ make test-frontend

    # terminal 3
    $ make flow

#### Enabling websocket and warm-reloading for dev

Currently websocket requests are redirected by Django to the webpack server. Sadly, by default major browsers do not support websocket redirection. To enable it in Firefox, go to `about:config` and turn `network.websocket.auto-follow-http-redirect` to `true`. Note that there is a bug filed to get rid of that option entirely: https://bugzilla.mozilla.org/show_bug.cgi?id=1052909

As far as we know, it is not possible to make that work in Chrome or Edge. This only impacts development, as there's no hot reloading in production.

If you can't turn on websockets, you will see errors in the console (that's not very impacting) and you'll have to reload your Django server regularly, because polling requests don't close, and after so many web page reloads, the Django process won't be able to accept new requests.


## Type checking

Our code uses Flow to enforce type checking. This is a good way to significantly improve resilience to bugs, and it removes some burden from unit tests (because Flow ensures that we use functions and components correctly).

To check for Flow issues during development while you edit files, run:

    yarn flow:dev

To learn more, you can read [Why use static types in JavaScript?](https://medium.freecodecamp.org/why-use-static-types-in-javascript-part-1-8382da1e0adb) or the official [Flow documentation](https://flow.org/en/docs/). Additionally, you can read through the [web-ext guide](https://github.com/mozilla/web-ext/blob/master/CONTRIBUTING.md#check-for-flow-errors) for hints on how to solve common Flow errors.

Until we define our set of rules, please refer to the [addons team's Flow manifesto](https://github.com/mozilla/addons-frontend/#flow) regarding specific usage and edge cases.


## Testing

Tests are run using [`jest`](https://facebook.github.io/jest/). We use [`enzyme`](http://airbnb.io/enzyme/docs/api/) for mounting React components and [`sinon`](http://sinonjs.org/) for mocking.

To run the test suite, use:

    $ yarn test

It will start an auto-reloading test runner, that will refresh every time you make a change to the code or tests.

Tests are put in files called `fileToTest.test.js` in the same directory as the file to test. Inside test files, test suites are created. There should be one test suite per component, using this notation:

```javascript
describe('<Component>', () => {
    // test suite here
});
```

Individual tests follow `mocha`'s syntax:

```javascript
it('does something', () => {
    // unit test here
});
```

We use `jest`'s [`expect`](https://facebook.github.io/jest/docs/en/expect.html) assertion tool.


## Development resources

### Integration between Django and React

- [Making React and Django play well together — Fractal Ideas](https://fractalideas.com/blog/making-react-and-django-play-well-together/)
- [Making React and Django play well together - the “hybrid app” model — Fractal Ideas](https://fractalideas.com/blog/making-react-and-django-play-well-together-hybrid-app-model/)

### Code architecture

- [Three Rules For Structuring (Redux) Applications — Jack Hsu](https://jaysoo.ca/2016/02/28/organizing-redux-application/)
- [The Anatomy Of A React & Redux Module (Applying The Three Rules) — Jack Hsu](https://jaysoo.ca/2016/02/28/applying-code-organization-rules-to-concrete-redux-code/)
- [Additional Guidelines For (Redux) Project Structure — Jack Hsu](https://jaysoo.ca/2016/12/12/additional-guidelines-for-project-structure/)

### Tools documentation

- [React](https://reactjs.org/docs/getting-started.html)
- [Redux](https://redux.js.org/)
- [create-react-app](https://github.com/facebook/create-react-app/blob/master/packages/react-scripts/template/README.md)
- [Flow](https://flow.org/en/docs/)
- [Jest](http://jestjs.io/docs/en/getting-started)
