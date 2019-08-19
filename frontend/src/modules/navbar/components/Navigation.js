/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';
import { push } from 'connected-react-router';

import './Navigation.css';

import * as locales from 'core/locales';
import * as navigation from 'core/navigation';
import * as project from 'core/project';
import * as resource from 'core/resource';
import * as unsavedchanges from 'modules/unsavedchanges';


import type { Locale } from 'core/locales';
import type { NavigationParams } from 'core/navigation';
import type { ProjectState } from 'core/project';
import type { ResourcesState } from 'core/resource';
import type { UnsavedChangesState } from 'modules/unsavedchanges';


type Props = {|
    locale: Locale,
    parameters: NavigationParams,
    project: ProjectState,
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
    componentDidMount() {
        this.updateTitle();
    }

    componentDidUpdate(prevProps: InternalProps) {
        this.updateTitle();
    }

    updateTitle = () => {
        const { locale, project } = this.props;

        if (!locale || !project) {
            return null;
        }

        const projectName = project.name || 'All Projects';
        document.title = `${locale.name} (${locale.code}) · ${projectName}`;
    }

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
        const { locale, parameters, project, resources } = this.props;

        if (!locale) {
            return null;
        }

        const localeDashboardURL = `/${locale.code}/`;
        let projectDashboardURL = `/${locale.code}/${parameters.project}/`;
        let projectName = project.name;

        // For all-projects, we have some special cases.
        if (parameters.project === 'all-projects') {
            projectDashboardURL = localeDashboardURL;
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
                    <a href={ localeDashboardURL }>
                        { locale.name }
                        <span className="locale-code">{ locale.code }</span>
                    </a>
                </li>
                <li>
                    <a href={ projectDashboardURL }>
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
        locale: locales.selectors.getCurrentLocaleData(state),
        parameters: navigation.selectors.getNavigationParams(state),
        project: state[project.NAME],
        resources: state[resource.NAME],
        unsavedchanges: state[unsavedchanges.NAME],
    };
};

export default connect(mapStateToProps)(NavigationBase);
