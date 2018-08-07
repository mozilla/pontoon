/* @flow */

import React from 'react';
import { connect } from 'react-redux';

import './App.css';

import { selectors as navSelectors } from 'core/navigation';
import { actions, EntitiesList } from 'modules/entitieslist';
import { Editor } from 'modules/editor';

import type { Navigation } from 'core/navigation';


type Props = {|
    parameters: Navigation,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};

/**
 * Main entry point to the application. Will render the structure of the page.
 */
class App extends React.Component<InternalProps> {
    componentDidMount() {
        const { locale, project, resource } = this.props.parameters;
        this.props.dispatch(actions.get(locale, project, resource));
    }

    render() {
        return (<div id="app">
            <section>
                <EntitiesList />
            </section>
            <section>
                <Editor />
            </section>
        </div>);
    }
}

const mapStateToProps = (state: Object): Props => {
    return {
        parameters: navSelectors.getNavigation(state),
    };
};

export default connect(mapStateToProps)(App);
