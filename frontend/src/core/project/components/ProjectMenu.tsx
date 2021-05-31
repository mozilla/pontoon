import * as React from 'react';
import { Localized } from '@fluent/react';

import { useOnDiscard } from 'core/utils';

import './ProjectMenu.css';

import ProjectItem from './ProjectItem';

import type { LocaleState, Localization } from 'core/locale';
import type { NavigationParams } from 'core/navigation';
import type { ProjectState } from 'core/project';

type Props = {
    parameters: NavigationParams;
    locale: LocaleState;
    project: ProjectState;
    navigateToPath: (arg0: string) => void;
};

type State = {
    visible: boolean;
};

type ProjectMenuProps = {
    locale: LocaleState;
    parameters: NavigationParams;
    onDiscard: () => void;
    onNavigate: (e: React.MouseEvent<HTMLAnchorElement>) => void;
};

export function ProjectMenu({
    locale,
    parameters,
    onDiscard,
    onNavigate,
}: ProjectMenuProps): React.ReactElement<'div'> {
    // Searching
    const [search, setSearch] = React.useState('');

    const updateProjectList = (e: React.SyntheticEvent<HTMLInputElement>) => {
        setSearch(e.currentTarget.value);
    };

    const localizationElements = locale.localizations.filter(
        (localization) =>
            localization.project.name
                .toLowerCase()
                .indexOf(search.toLowerCase()) > -1,
    );

    // Sorting
    const [sortActive, setSortActive] = React.useState('project');
    const [sortAsc, setSortAsc] = React.useState(true);

    const sortByProject = () => {
        setSortActive('project');
        setSortAsc(sortActive !== 'project' || !sortAsc);
    };
    const sortByProgress = () => {
        setSortActive('progress');
        setSortAsc(sortActive !== 'progress' || !sortAsc);
    };

    const getProgress = (local: Localization) => {
        const completeStrings =
            local.approvedStrings + local.stringsWithWarnings;
        const percent = Math.floor(
            (completeStrings / local.totalStrings) * 100,
        );
        return percent;
    };

    const getProject = (local: Localization) => {
        return local.project.name;
    };

    const sort = sortAsc ? 'fa fa-caret-up' : 'fa fa-caret-down';
    const projectClass = sortActive === 'project' ? sort : '';
    const progressClass = sortActive === 'progress' ? sort : '';

    // Discarding menu
    const ref = React.useRef(null);
    useOnDiscard(ref, onDiscard);

    return (
        <div ref={ref} className='menu'>
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
                        value={search}
                        onChange={updateProjectList}
                        placeholder='Filter projects'
                    />
                </Localized>
            </div>

            <div className='header'>
                <Localized id='project-ProjectMenu--project'>
                    <span className='project' onClick={sortByProject}>
                        PROJECT
                    </span>
                </Localized>
                <span
                    className={'project icon ' + projectClass}
                    onClick={sortByProject}
                />
                <Localized id='project-ProjectMenu--progress'>
                    <span className='progress' onClick={sortByProgress}>
                        PROGRESS
                    </span>
                </Localized>
                <span
                    className={'progress icon ' + progressClass}
                    onClick={sortByProgress}
                />
            </div>

            <ul>
                {localizationElements.length ? (
                    (sortActive === 'project'
                        ? localizationElements.sort((a, b) => {
                              const projectA = getProject(a);
                              const projectB = getProject(b);

                              let result = 0;

                              if (projectA < projectB) {
                                  result = -1;
                              }
                              if (projectA > projectB) {
                                  result = 1;
                              }

                              return sortAsc ? result : result * -1;
                          })
                        : localizationElements.sort((a, b) => {
                              const percentA = getProgress(a);
                              const percentB = getProgress(b);

                              let result = 0;

                              if (percentA < percentB) {
                                  result = -1;
                              }
                              if (percentA > percentB) {
                                  result = 1;
                              }

                              return sortAsc ? result : result * -1;
                          })
                    ).map((localization, index) => {
                        return (
                            <ProjectItem
                                parameters={parameters}
                                localization={localization}
                                navigateToPath={onNavigate}
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
    );
}

/**
 * Render a project breadcrumb for the main navigation bar in the regular view.
 *
 * In the All projects view, render project menu, which allows switching to the
 * regular view without reloading the Translate app.
 */
export default class ProjectMenuBase extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            visible: false,
        };
    }

    toggleVisibility: () => void = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
    };

    handleDiscard: () => void = () => {
        this.setState({
            visible: false,
        });
    };

    navigateToPath: (event: React.MouseEvent<HTMLAnchorElement>) => void = (
        event: React.MouseEvent<HTMLAnchorElement>,
    ) => {
        event.preventDefault();

        const path = event.currentTarget.pathname;
        this.props.navigateToPath(path);

        this.setState({
            visible: false,
        });
    };

    render(): React.ReactElement<'li'> {
        const { locale, parameters, project } = this.props;

        if (parameters.project !== 'all-projects') {
            return (
                <li>
                    <a href={`/${locale.code}/${project.slug}/`}>
                        {project.name}
                    </a>
                </li>
            );
        }

        let className = 'project-menu';
        if (!this.state.visible) {
            className += ' closed';
        }
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
                {this.state.visible && (
                    <ProjectMenu
                        locale={locale}
                        parameters={parameters}
                        onDiscard={this.handleDiscard}
                        onNavigate={this.navigateToPath}
                    />
                )}
            </li>
        );
    }
}
