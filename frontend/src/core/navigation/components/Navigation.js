/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';
import isEmpty from 'lodash.isempty';
import { push } from 'connected-react-router';

import './Navigation.css';

import { NAME as LOCALES_NAME } from 'core/locales';
import * as resource from 'core/resource';
import * as unsavedchanges from 'modules/unsavedchanges';

import { selectors } from '..';

import type { LocalesState } from 'core/locales';
import type { NavigationParams } from '..';
import type { ResourcesState } from 'core/resource';
import type { UnsavedChangesState } from 'modules/unsavedchanges';


type Props = {|
    locales: LocalesState,
    parameters: NavigationParams,
    resources: ResourcesState,
    unsavedchanges: UnsavedChangesState,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};


/**
 * Render a breadcrumb-like navigation bar.
 *
 * Allows to exit the Translate app to go back to team or project dashboards.
 */
export class NavigationBase extends React.Component<InternalProps> {
    navigateToPath = (path: string) => {
        const { dispatch } = this.props;

        dispatch(
            unsavedchanges.actions.check(
                this.props.unsavedchanges,
                () => { dispatch(push(path)); }
            )
        );
    }

    render() {
        const { locales, parameters, resources } = this.props;

        if (isEmpty(locales.locales)) {
            return null;
        }

        const locale = locales.locales[parameters.locale];

        let projectName = parameters.project;
        if (projectName === 'all-projects') {
            projectName = 'All Projects';
        }

        return <nav className="navigation">
            <ul>
                <li>
                    <a href="/">
                        <img
                            src="/static/img/logo.svg"
                            width="32"
                            height="32"
                            alt="Pontoon logo"
                        />
                    </a>
                </li>
                <li>
                    <a href={ `/${locale.code}/` }>
                        { locale.name }
                        <span className="locale-code">{ locale.code }</span>
                    </a>
                </li>
                <li>
                    <a href={ `/${locale.code}/${parameters.project}/` }>
                        { projectName }
                    </a>
                </li>
                <resource.ResourceMenu
                    navigateToPath={ this.navigateToPath }
                    parameters={ parameters }
                    resources={ resources }
                />
            </ul>
        </nav>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        locales: state[LOCALES_NAME],
        parameters: selectors.getNavigationParams(state),
        resources: state[resource.NAME],
        unsavedchanges: state[unsavedchanges.NAME],
    };
};

export default connect(mapStateToProps)(NavigationBase);
