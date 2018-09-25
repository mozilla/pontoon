/* @flow */

import React from 'react';
import { connect } from 'react-redux';

import './App.css';

import { Lightbox } from 'core/lightbox';
import { selectors as navSelectors } from 'core/navigation';
import { UserAutoUpdater } from 'core/user';
import { EntitiesList } from 'modules/entitieslist';
import { EntityDetails } from 'modules/entitydetails';

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
    render() {
        return <div id="app">
            <UserAutoUpdater />
            <section>
                <EntitiesList />
            </section>
            <EntityDetails />
            <Lightbox />
        </div>;
    }
}

const mapStateToProps = (state: Object): Props => {
    return {
        parameters: navSelectors.getNavigation(state),
    };
};

export default connect(mapStateToProps)(App);
