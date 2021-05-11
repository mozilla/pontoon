/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import { useOnDiscard } from 'core/utils';

import './ResourceMenu.css';

import ResourceItem from './ResourceItem.js';
import ResourcePercent from './ResourcePercent.js';

import type { NavigationParams } from 'core/navigation';
import type { ResourcesState } from '..';
import type { Resource } from '../actions';

type Props = {|
    parameters: NavigationParams,
    resources: ResourcesState,
    navigateToPath: (string) => void,
|};

type State = {|
    visible: boolean,
|};

type ResourceMenuProps = {|
    parameters: NavigationParams,
    resources: ResourcesState,
    onDiscard: () => void,
    onNavigate: (e: SyntheticMouseEvent<HTMLAnchorElement>) => void,
|};

export function ResourceMenu({
    parameters,
    resources,
    onDiscard,
    onNavigate,
}: ResourceMenuProps): React.Element<'div'> {
    // Searching
    const [search, setSearch] = React.useState('');
    const resourceElements = resources.resources.filter(
        (resource) =>
            resource.path.toLowerCase().indexOf(search.toLowerCase()) > -1,
    );

    const updateResourceList = (e: SyntheticInputEvent<HTMLInputElement>) => {
        setSearch(e.currentTarget.value);
    };

    // Sorting
    const [sortActive, setSortActive] = React.useState('resource');
    const [sortAsc, setSortAsc] = React.useState(true);

    const sortByResource = () => {
        setSortActive('resource');
        setSortAsc(sortActive !== 'resource' || !sortAsc);
    };
    const sortByProgress = () => {
        setSortActive('progress');
        setSortAsc(sortActive !== 'progress' || !sortAsc);
    };

    const getProgress = (res: Resource) => {
        const completeStrings = res.approvedStrings + res.stringsWithWarnings;
        const percent = Math.floor((completeStrings / res.totalStrings) * 100);
        return percent;
    };

    const getResource = (res: Resource) => {
        return res.path;
    };

    const sort = sortAsc ? 'fa fa-caret-up' : 'fa fa-caret-down';
    const resourceClass = sortActive === 'resource' ? sort : '';
    const progressClass = sortActive === 'progress' ? sort : '';

    // Discarding menu
    const ref = React.useRef(null);
    useOnDiscard(ref, onDiscard);

    return (
        <div ref={ref} className='menu'>
            <div className='search-wrapper'>
                <div className='icon fa fa-search'></div>
                <Localized
                    id='resource-ResourceMenu--search-placeholder'
                    attrs={{ placeholder: true }}
                >
                    <input
                        type='search'
                        autoComplete='off'
                        autoFocus
                        value={search}
                        onChange={updateResourceList}
                        placeholder='Filter resources'
                    />
                </Localized>
            </div>

            <div className='header'>
                <Localized id='resource-ResourceMenu--resource'>
                    <span className='resource' onClick={sortByResource}>
                        RESOURCE
                    </span>
                </Localized>
                <span
                    className={'resource icon ' + resourceClass}
                    onClick={sortByResource}
                />
                <Localized id='resource-ResourceMenu--progress'>
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
                {resourceElements.length ? (
                    (sortActive === 'resource'
                        ? resourceElements.sort((a, b) => {
                              const resourceA = getResource(a);
                              const resourceB = getResource(b);

                              let result = 0;

                              if (resourceA < resourceB) {
                                  result = -1;
                              }
                              if (resourceA > resourceB) {
                                  result = 1;
                              }

                              return sortAsc ? result : result * -1;
                          })
                        : resourceElements.sort((a, b) => {
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
                    ).map((resource, index) => {
                        return (
                            <ResourceItem
                                parameters={parameters}
                                resource={resource}
                                navigateToPath={onNavigate}
                                key={index}
                            />
                        );
                    })
                ) : (
                    // No resources found
                    <Localized id='resource-ResourceMenu--no-results'>
                        <li className='no-results'>No results</li>
                    </Localized>
                )}
            </ul>

            <ul className='static-links'>
                <li
                    className={
                        parameters.resource === 'all-resources'
                            ? 'current'
                            : null
                    }
                >
                    <a
                        href={`/${parameters.locale}/${parameters.project}/all-resources/`}
                        onClick={onNavigate}
                    >
                        <Localized id='resource-ResourceMenu--all-resources'>
                            <span>All Resources</span>
                        </Localized>
                        <ResourcePercent resource={resources.allResources} />
                    </a>
                </li>
                <li>
                    <a
                        href={`/${parameters.locale}/all-projects/all-resources/`}
                        onClick={onNavigate}
                    >
                        <Localized id='resource-ResourceMenu--all-projects'>
                            <span>All Projects</span>
                        </Localized>
                    </a>
                </li>
            </ul>
        </div>
    );
}

/**
 * Render a resource menu for the main navigation bar.
 *
 * Allows to switch between resources without reloading the Translate app.
 */
export default class ResourceMenuBase extends React.Component<Props, State> {
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

    navigateToPath: (event: SyntheticMouseEvent<HTMLAnchorElement>) => void = (
        event: SyntheticMouseEvent<HTMLAnchorElement>,
    ) => {
        event.preventDefault();

        const path = event.currentTarget.pathname;
        this.props.navigateToPath(path);

        this.setState({
            visible: false,
        });
    };

    render(): null | React.Element<'li'> {
        const { parameters, resources } = this.props;

        if (parameters.project === 'all-projects') {
            return null;
        }

        let className = 'resource-menu';
        if (!this.state.visible) {
            className += ' closed';
        }

        let resourceName = parameters.resource.split('/').slice(-1)[0];
        if (parameters.resource === 'all-resources') {
            resourceName = (
                <Localized id='resource-ResourceMenu--all-resources'>
                    All Resources
                </Localized>
            );
        }

        return (
            <li className={className}>
                <div
                    className='selector unselectable'
                    onClick={this.toggleVisibility}
                    title={parameters.resource}
                >
                    <span>{resourceName}</span>
                    <span className='icon fa fa-caret-down'></span>
                </div>

                {this.state.visible && (
                    <ResourceMenu
                        parameters={parameters}
                        resources={resources}
                        onDiscard={this.handleDiscard}
                        onNavigate={this.navigateToPath}
                    />
                )}
            </li>
        );
    }
}
