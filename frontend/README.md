# Translate front-end app

## Tools

<table>
    <tr>
        <td>Bootstrapper</td>
        <td>create-react-app</td>
        <td>https://github.com/facebook/create-react-app</td>
    </tr>
    <tr>
        <td>Package manager</td>
        <td>Yarn</td>
        <td>https://yarnpkg.com/</td>
    </tr>
    <tr>
        <td>Views</td>
        <td>React</td>
        <td>https://reactjs.org/</td>
    </tr>
    <tr>
        <td>Data</td>
        <td>Redux</td>
        <td>https://redux.js.org/</td>
    </tr>
    <tr>
        <td>Tests</td>
        <td>Jest</td>
        <td>http://jestjs.io/</td>
    </tr>
    <tr>
        <td>Type checking</td>
        <td>TypeScript</td>
        <td>https://www.typescriptlang.org/</td>
    </tr>
    <tr>
        <td>Localization</td>
        <td>Fluent</td>
        <td>https://projectfluent.org/</td>
    </tr>
    <tr>
        <td>Style</td>
        <td>CSS</td>
        <td></td>
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

- `index.js` — public interface of the module. It is recommended to define a NAME constant here which should be a unique identifier of the module. This name will be used in `combineReducers` and in all `mapStateToProps` to identify the subtree of the global state relevant to this module.
- `actions.js` — actions that can be used to fetch data from an API, trigger changes, etc.
- `reducer.js` — a single Redux reducer (if you need to have more than one reducer, you probably actually need to make several modules)
- `components/` — a folder containing components, with file names in CamelCase

Of course, more can be added if needed. For example, modules with a high number of action types might want to have an `actionTypes.js` file to separate them from actions.


## Running and deploying

### Production

The only required step for the front-end is to build static files with `yarn build`. Django is configured to collect the `index.html` and static files from the `build` folder and put them with other static files. All of that is automated for deployement to Heroku.

### Development

If you're using docker, `make run` automatically starts both a webpack server (on port 3000) and a Django server (on port 8000). Django is the server you want to hit, and it will then proxy appropriate requests to the webpack server.

A common case during development is to have 2 terminals open: one for the dev servers and one for the tests:

```shell
    # terminal 1
    $ make run

    # terminal 2
    $ make test-frontend
```

#### Enabling websocket and warm-reloading for dev

Currently websocket requests are redirected by Django to the webpack server. Sadly, by default major browsers do not support websocket redirection. To enable it in Firefox, go to `about:config` and turn `network.websocket.auto-follow-http-redirect` to `true`. Note that there is a bug filed to get rid of that option entirely: https://bugzilla.mozilla.org/show_bug.cgi?id=1052909

As far as we know, it is not possible to make that work in Chrome or Edge. This only impacts development, as there's no hot reloading in production.

If you can't turn on websockets, you will see errors in the console (that's not very impacting) and you'll have to reload your Django server regularly, because polling requests don't close, and after so many web page reloads, the Django process won't be able to accept new requests.


## Dependencies

We manage our JavaScript dependencies with `yarn`. Dependencies and their versions are listed in the `package.json` file, under `dependencies` for production and `devDependencies` for development.

To add a new dependency, run the following commands:

```shell
    # Add the dependency. Make sure to use an exact version.
    yarn add my-package@version

    # Go back to the root folder.
    cd ..

    # Rebuild the Pontoon image so that it has the new dependencies.
    make build
```

To upgrade dependency to a specific version, run the following commands:

```shell
    # Upgrade dependency to the specified version.
    yarn upgrade my-package@version

    # Go back to the root folder.
    cd ..

    # Rebuild the Pontoon image so that it has the upgraded dependencies.
    make build
```

Note that, in order to add new dependencies, you need to have `yarn` installed and perform the actions locally (outside docker). You might want to remove the `node_modules` folder after you've run the install or update command (and the `package.json` and `yarn.lock` files have been updated) and before rebuilding the image, to reduce the size of the docker context.


## Type checking

Our code uses TypeScript for type-checking the production code. Tests are not type-checked in general, which allows for smaller test fixtures. Visit the [TypeScript documentation](https://www.typescriptlang.org/docs) to learn more about TypeScript.

To check for TypeScript errors locally, run:

    $ make types


## Testing

Tests are run using [`jest`](https://facebook.github.io/jest/). We use [`enzyme`](http://airbnb.io/enzyme/docs/api/) for mounting React components and [`sinon`](http://sinonjs.org/) for mocking.

To run the test suite, use:

    $ make test-frontend

It will start an auto-reloading test runner, that will refresh every time you make a change to the code or tests.

Tests are put in files called `fileToTest.test.js` in the same directory as the file to test. Inside test files, test suites are created. There should be one test suite per component, using this notation:

```javascript
describe('<Component>', () => {
    // test suite here
});
```

Individual tests follow `mocha`'s descriptive syntax. Try to be as explicit as possible in your test description. If you cannot, that probably means the test you want to write is not focused enough. Each test should be as small as possible, testing one single thing. It's better to have many small tests than one single, humongous test. Code repetition is tolerated in unit tests.

```javascript
it('does something specific', () => {
    // unit test here
});
```

We use `jest`'s [`expect`](https://facebook.github.io/jest/docs/en/expect.html) assertion tool.


## Localization

The user interface is localized using [Fluent](https://projectfluent.org/) and the library `fluent-react`. Fluent allows to move the complexity of handling translated content from the developer to the translator. Thus, when using it, you should care only about the English version, and trust that the localizers will know what to do with your string in their language.

### Adding localized content

Every time you add a piece of UI that contains some content, there are 2 things you need to do. First, make sure you put it inside a `<Localized>` element, and give it an id. String identifiers should follow this form: `${module}-${ComponentName}--${string-description}`. For example, if you were to add a new button (`<button>Update</button>`) to the `Editor` component in the `entitydetails` module, the id for that button might be `entitydetails-Editor--button-update`.

That would give:

```js
class Editor extends React.Component {
    render() {
        return <div>
            <Localized id="entitydetails-Editor--button-update">
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

### Pseudo-localization

In order to easily verify that a string is effectively localized, you can turn on pseudo-localization. To do that, add `pseudolocalization=accented` or `pseudolocalization=bidi` to the URL, then refresh the page.

Pseudo-localization turns every supported string into a different version of itself. We support two modes: "accented" (transforms "Accented English" into "Ȧȧƈƈḗḗƞŧḗḗḓ Ḗḗƞɠŀīīşħ") and "bidi" (transforms "Reversed English" into "‮ᴚǝʌǝɹsǝp Ǝuƃʅısɥ‬"). Because only strings that are actually localized (they exist in our reference en-US FTL file and they are properly set in a `<Localized>` component) get that transformation, it is easy to spot which strings are *not* properly localized in the interface.

You can read [more about pseudo-localization on Wikipedia](https://en.wikipedia.org/wiki/Pseudolocalization).


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
- [Jest](http://jestjs.io/docs/en/getting-started)
- [sinon](https://sinonjs.org/releases/v6.0.0/)
- [connected-react-router](https://github.com/supasate/connected-react-router)
- [Infinite Scroller](https://cassetterocks.github.io/react-infinite-scroller/)
- [Linkify](https://tasti.github.io/react-linkify/)
- [reselect](https://github.com/reduxjs/reselect)
- [ReactTimeAgo](https://github.com/catamphetamine/react-time-ago)
- [react-tabs](https://github.com/reactjs/react-tabs)
- [Slate](https://docs.slatejs.org/)
- [TypeScript](https://www.typescriptlang.org/docs/)
