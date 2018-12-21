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
- `constants.js` — a list of constants required by the module or other modules. It is recommended to define a NAME constant here which should be a unique identifier of the module. This name will be used in `combineReducers` and in all `mapStateToProps` to identify the subtree of the global state relevant to this module.
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

Note that Flow is good at extrapolating types from the standard library and common tools like React. Only put explicit types where needed. For example, it is not necessary to express that the `render` method of a component return a `React.Node`, as Flow will extrapolate that and check it even if you don't.


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


## Localization

The user interface is localized using [Fluent](https://projectfluent.org/) and the library `fluent-react`. Fluent allows to move the complexity of handling translated content from the developer to the translator. Thus, when using it, you should care only about the English version, and trust that the localizers will know what to do with your string in their language.

### Adding localized content

Every time you add a piece of UI that contains some content, there are 2 things you need to do. First, make sure you put it inside a `<Localized>` element, and give it an id. String identifiers should follow this form: `${module}-${component}-${contentDescription}`. For example, if you were to add a new button (`<button>Update</button>`) to the `Editor` component in the `entitydetails` module, the id for that button might be `entitydetails-editor-button-update`.

That would give:

```js
class Editor extends React.Component {
    render() {
        return <div>
            <Localized id="entitydetails-editor-button-update">
                <button>Update</button>
            </Localized>
        </div>;
    }
}
```

The second thing you need to do is to add that new string into our main translation files. Translations available to localizers are based on those files, so if you forget to put the new content there, no one will be able to translate that content.

The source language for our application is `en-US` (that is what you should use by default when writing content in the code, and in the language files). You can find them in `frontend/public/static/locale/en-US/`. We currently have only one file, named `translate.ftl`, and that is where all content should be added.

Those files use the FTL format. In its simplest form, a string in such a file (called a `message` in Fluent vocabulary) looks like this: `message-id = Content`. There are, however, lots of tools that you can use in that syntax, and you are encouraged to read [Fluent's Syntax Guide](https://projectfluent.org/fluent/guide/) to familiarize yourself with them. Make sure you also take a look at the [Good Practices for Developers](https://github.com/projectfluent/fluent/wiki/Good-Practices-for-Developers#prefer-separate-messages-over-variants-for-ui-logic) guide.

### Semantic identifiers

Fluent uses the concept of a *social contract* between developer and localizers. This contract is established by the selection of a unique identifier, called `l10n-id`, which carries a promise of being used in a particular place to carry a particular meaning.

You should consider the `l10n-id` as a variable name. If the meaning of the content changes, then you should also change the ID. This will notify localizers that the content is different from before and that a new translation is needed. However, if you make minor changes (fix a typo, make a change that keeps the same meaning) you should instead keep the same ID.

An important part of the contract is that the developer commits to treat the localization output as opaque. That means that no concatenations, replacements or splitting should happen after the translation is completed to generate the desired output.

In return, localizers enter the social contract by promising to provide an accurate and clean translation of the messages that match the request.

In Fluent, the developer is not to be bothered with inner logic and complexity that the localization will use to construct the response. Whether declensions or other variant selection techniques are used is up to a localizer and their particular translation. From the developer perspective, Fluent returns a final string to be presented to the user, with no l10n logic required in the running code.


## Development resources

### Integration between Django and React

- [Making React and Django play well together — Fractal Ideas](https://fractalideas.com/blog/making-react-and-django-play-well-together/)
- [Making React and Django play well together - the “hybrid app” model — Fractal Ideas](https://fractalideas.com/blog/making-react-and-django-play-well-together-hybrid-app-model/)

### Code architecture

- [Three Rules For Structuring (Redux) Applications — Jack Hsu](https://jaysoo.ca/2016/02/28/organizing-redux-application/)
- [The Anatomy Of A React & Redux Module (Applying The Three Rules) — Jack Hsu](https://jaysoo.ca/2016/02/28/applying-code-organization-rules-to-concrete-redux-code/)
- [Additional Guidelines For (Redux) Project Structure — Jack Hsu](https://jaysoo.ca/2016/12/12/additional-guidelines-for-project-structure/)

### Localization tools

- [Fluent Syntax Guide](https://projectfluent.org/fluent/guide/)
- [fluent-react's Localized](https://github.com/projectfluent/fluent.js/wiki/Localized)
- [Fluent's playground](https://projectfluent.org/play/)

### Tools documentation

- [React](https://reactjs.org/docs/getting-started.html)
- [Redux](https://redux.js.org/)
- [create-react-app](https://github.com/facebook/create-react-app/blob/master/packages/react-scripts/template/README.md)
- [Flow](https://flow.org/en/docs/)
- [Jest](http://jestjs.io/docs/en/getting-started)
- [sinon](https://sinonjs.org/releases/v6.0.0/)
- [connected-react-router](https://github.com/supasate/connected-react-router)
- [Infinite Scroller](https://cassetterocks.github.io/react-infinite-scroller/)
- [Linkify](https://tasti.github.io/react-linkify/)
- [reselect](https://github.com/reduxjs/reselect)
- [TimeAgo](https://github.com/nmn/react-timeago)
- [react-tabs](https://github.com/reactjs/react-tabs)
