import * as React from 'react';
import { useStore } from 'react-redux';
import { push } from 'connected-react-router';

import './Navigation.css';

import { useAppDispatch, useAppSelector } from 'hooks';
import * as locale from 'core/locale';
import * as navigation from 'core/navigation';
import * as project from 'core/project';
import * as resource from 'core/resource';
import * as unsavedchanges from 'modules/unsavedchanges';

import type { LocaleState } from 'core/locale';
import type { NavigationParams } from 'core/navigation';
import type { ProjectState } from 'core/project';
import type { ResourcesState } from 'core/resource';

type Props = {
    locale: LocaleState;
    parameters: NavigationParams;
    project: ProjectState;
    resources: ResourcesState;
};

type InternalProps = Props & {
    dispatch: (...args: Array<any>) => any;
    store: Record<string, any>;
};

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
        const { parameters } = this.props;

        // Update project and resource data if project changes
        if (parameters.project !== prevProps.parameters.project) {
            this.props.dispatch(project.actions.get(parameters.project));

            // Load resources, unless we're in the All Projects view
            if (parameters.project !== 'all-projects') {
                this.props.dispatch(
                    resource.actions.get(parameters.locale, parameters.project),
                );
            }
        }

        if (this.props.project !== prevProps.project) {
            this.updateTitle();
        }
    }

    updateTitle: () => null | void = () => {
        const { locale, project } = this.props;

        if (!locale || !locale.name) {
            return null;
        }

        if (!project || !project.name) {
            return null;
        }

        const projectName = project.name || 'All Projects';
        document.title = `${locale.name} (${locale.code}) · ${projectName}`;
    };

    navigateToPath: (path: string) => void = (path: string) => {
        const { dispatch } = this.props;

        const state = this.props.store.getState();
        const unsavedChangesExist = state[unsavedchanges.NAME].exist;
        const unsavedChangesIgnored = state[unsavedchanges.NAME].ignored;

        dispatch(
            unsavedchanges.actions.check(
                unsavedChangesExist,
                unsavedChangesIgnored,
                () => {
                    dispatch(push(path));
                },
            ),
        );
    };

    render(): null | React.ReactElement<'nav'> {
        const { locale, parameters, resources } = this.props;

        if (!locale) {
            return null;
        }

        return (
            <nav className='navigation'>
                <ul>
                    <li>
                        <a href='/'>
                            <img
                                src='/static/img/logo.svg'
                                width='32'
                                height='32'
                                alt='Pontoon logo'
                            />
                        </a>
                    </li>
                    <li>
                        <a href={`/${locale.code}/`}>
                            {locale.name}
                            <span className='locale-code'>{locale.code}</span>
                        </a>
                    </li>
                    <project.ProjectMenu
                        locale={locale}
                        parameters={parameters}
                        project={this.props.project}
                        navigateToPath={this.navigateToPath}
                    />
                    <resource.ResourceMenu
                        parameters={parameters}
                        resources={resources}
                        navigateToPath={this.navigateToPath}
                    />
                </ul>
            </nav>
        );
    }
}

export default function Navigation(): React.ReactElement<
    typeof NavigationBase
> {
    const state = {
        locale: useAppSelector((state) => state[locale.NAME]),
        parameters: useAppSelector((state) =>
            navigation.selectors.getNavigationParams(state),
        ),
        project: useAppSelector((state) => state[project.NAME]),
        resources: useAppSelector((state) => state[resource.NAME]),
    };

    return (
        <NavigationBase
            {...state}
            dispatch={useAppDispatch()}
            store={useStore()}
        />
    );
}
