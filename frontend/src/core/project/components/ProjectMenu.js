/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';
import onClickOutside from 'react-onclickoutside';

import type { LocaleState } from 'core/locale';
import type { NavigationParams } from 'core/navigation';
import type { ProjectState } from 'core/project';


type Props = {|
    parameters: NavigationParams,
    locale: LocaleState,
    project: ProjectState,
    navigateToPath: (string) => void,
|};

type State = {|
    search: string,
    visible: boolean,
|};


/**
 * Render a project breadcrumb for the main navigation bar in the regular view.
 *
 * In the All projects view, render project menu, which allows switching to the
 * regular view without reloading the Translate app.
 */
export class ProjectMenuBase extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            search: '',
            visible: false,
        };
    }

    toggleVisibility = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
    }

    // This method is called by the Higher-Order Component `onClickOutside`
    // when a user clicks outside the user menu.
    handleClickOutside = () => {
        this.setState({
            visible: false,
        });
    }

    navigateToPath = (event: SyntheticMouseEvent<HTMLAnchorElement>) => {
        event.preventDefault();

        const path = event.currentTarget.pathname;
        this.props.navigateToPath(path);

        this.setState({
            visible: false,
        });
    }

    updateProjectList = (event: SyntheticInputEvent<HTMLInputElement>) => {
        this.setState({
            search: event.currentTarget.value,
        });
    }

    renderBreadcrumb() {
        const { locale, project } = this.props;

        return <li>
            <a href={ `/${locale.code}/${project.slug}/` }>
                { project.name }
            </a>
        </li>
    }

    renderMenu() {
        const { locale } = this.props;

        return <li>
            <a href={ `/${locale.code}/` }>
                { 'All Projects' }
            </a>
        </li>
    }

    render() {
        const { parameters } = this.props;

        if (parameters.project !== 'all-projects') {
            return this.renderBreadcrumb();
        }

        return this.renderMenu();
    }
}

export default onClickOutside(ProjectMenuBase);
