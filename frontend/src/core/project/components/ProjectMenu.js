/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';
import onClickOutside from 'react-onclickoutside';

import './ProjectMenu.css';

import ProjectItem from './ProjectItem.js';

import type { LocaleState, Localization } from 'core/locale';
import type { NavigationParams } from 'core/navigation';
import type { ProjectState } from 'core/project';

type Props = {|
    parameters: NavigationParams,
    locale: LocaleState,
    project: ProjectState,
    navigateToPath: (string) => void,
    sortActive: 'project' | 'progress',
    sortAsc: boolean,
|};

type State = {|
    search: string,
    visible: boolean,
    sortActive: string,
    sortAsc: boolean,
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
            sortActive: 'project',
            sortAsc: true,
        };
    }

    toggleVisibility = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
    };

    sortByProject = () => {
        this.setState((state) => {
            return {
                sortActive: 'project',
                sortAsc: state.sortActive !== 'project' || !state.sortAsc,
            };
        });
    };

    sortByProgress = () => {
        this.setState((state) => {
            return {
                sortActive: 'progress',
                sortAsc: state.sortActive !== 'progress' || !state.sortAsc,
            };
        });
    };

    getProgress(local: Localization) {
        const completeStrings =
            local.approvedStrings + local.stringsWithWarnings;
        const percent = Math.floor(
            (completeStrings / local.totalStrings) * 100,
        );
        return percent;
    }

    getProject(local: Localization) {
        return local.project.name;
    }

    // This method is called by the Higher-Order Component `onClickOutside`
    // when a user clicks outside the user menu.
    handleClickOutside = () => {
        this.setState({
            visible: false,
        });
    };

    navigateToPath = (event: SyntheticMouseEvent<HTMLAnchorElement>) => {
        event.preventDefault();

        const path = event.currentTarget.pathname;
        this.props.navigateToPath(path);

        this.setState({
            visible: false,
        });
    };

    updateProjectList = (event: SyntheticInputEvent<HTMLInputElement>) => {
        this.setState({
            search: event.currentTarget.value,
        });
    };

    renderBreadcrumb() {
        const { locale, project } = this.props;

        return (
            <li>
                <a href={`/${locale.code}/${project.slug}/`}>{project.name}</a>
            </li>
        );
    }

    renderMenu() {
        const { locale, parameters } = this.props;

        let className = 'project-menu';
        if (!this.state.visible) {
            className += ' closed';
        }

        // Search projects
        const search = this.state.search;
        const localizationElements = locale.localizations.filter(
            (localization) =>
                localization.project.name
                    .toLowerCase()
                    .indexOf(search.toLowerCase()) > -1,
        );

        const sort = this.state.sortAsc ? 'fa fa-caret-up' : 'fa fa-caret-down';
        const projectClass = this.state.sortActive === 'project' ? sort : '';
        const progressClass = this.state.sortActive === 'progress' ? sort : '';

        return (
            <li className={className}>
                <div
                    className='selector unselectable'
                    onClick={this.toggleVisibility}
                >
                    <Localized id='project-ProjectMenu--all-projects'>
                        <span>All Projects</span>
                    </Localized>
                    <span className='icon fa fa-caret-down'></span>
                </div>

                {!this.state.visible ? null : (
                    <div className='menu'>
                        <div className='search-wrapper'>
                            <div className='icon fa fa-search'></div>
                            <Localized
                                id='project-ProjectMenu--search-placeholder'
                                attrs={{ placeholder: true }}
                            >
                                <input
                                    type='search'
                                    autoComplete='off'
                                    autoFocus
                                    value={this.state.search}
                                    onChange={this.updateProjectList}
                                    placeholder='Filter projects'
                                />
                            </Localized>
                        </div>

                        <div className='header'>
                            <Localized id='project-ProjectMenu--project'>
                                <span
                                    className='project'
                                    onClick={this.sortByProject}
                                >
                                    PROJECT
                                </span>
                            </Localized>
                            <span
                                className={'project icon ' + projectClass}
                                onClick={this.sortByProject}
                            />
                            <Localized id='project-ProjectMenu--progress'>
                                <span
                                    className='progress'
                                    onClick={this.sortByProgress}
                                >
                                    PROGRESS
                                </span>
                            </Localized>
                            <span
                                className={'progress icon ' + progressClass}
                                onClick={this.sortByProgress}
                            />
                        </div>

                        <ul>
                            {localizationElements.length ? (
                                (this.state.sortActive === 'project'
                                    ? localizationElements.sort((a, b) => {
                                          const projectA = this.getProject(a);
                                          const projectB = this.getProject(b);

                                          let result = 0;

                                          if (projectA < projectB) {
                                              result = -1;
                                          }
                                          if (projectA > projectB) {
                                              result = 1;
                                          }

                                          return this.state.sortAsc
                                              ? result
                                              : result * -1;
                                      })
                                    : localizationElements.sort((a, b) => {
                                          const percentA = this.getProgress(a);
                                          const percentB = this.getProgress(b);

                                          let result = 0;

                                          if (percentA < percentB) {
                                              result = -1;
                                          }
                                          if (percentA > percentB) {
                                              result = 1;
                                          }

                                          return this.state.sortAsc
                                              ? result
                                              : result * -1;
                                      })
                                ).map((localization, index) => {
                                    return (
                                        <ProjectItem
                                            parameters={parameters}
                                            localization={localization}
                                            navigateToPath={this.navigateToPath}
                                            key={index}
                                        />
                                    );
                                })
                            ) : (
                                // No projects found
                                <Localized id='project-ProjectMenu--no-results'>
                                    <li className='no-results'>No results</li>
                                </Localized>
                            )}
                        </ul>
                    </div>
                )}
            </li>
        );
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
