/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';
import onClickOutside from 'react-onclickoutside';

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
    search: string,
    visible: boolean,
    sortActive: 'resource' | 'progress',
    sortAsc: boolean,
|};

/**
 * Render a resource menu for the main navigation bar.
 *
 * Allows to switch between resources without reloading the Translate app.
 */
export class ResourceMenuBase extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            search: '',
            visible: false,
            sortActive: 'resource',
            sortAsc: true,
        };
    }

    toggleVisibility = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
    };

    sortByResource = () => {
        this.setState((state) => {
            return {
                sortActive: 'resource',
                sortAsc: state.sortActive !== 'resource' || !state.sortAsc,
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

    updateResourceList = (event: SyntheticInputEvent<HTMLInputElement>) => {
        this.setState({
            search: event.currentTarget.value,
        });
    };

    getProgress(res: Resource) {
        const completeStrings = res.approvedStrings + res.stringsWithWarnings;
        const percent = Math.floor((completeStrings / res.totalStrings) * 100);
        return percent;
    }

    getResource(res: Resource) {
        return res.path;
    }

    render() {
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

        // Search resources
        const search = this.state.search;
        const resourceElements = resources.resources.filter(
            (resource) =>
                resource.path.toLowerCase().indexOf(search.toLowerCase()) > -1,
        );

        const sort = this.state.sortAsc ? 'fa fa-caret-up' : 'fa fa-caret-down';
        const resourceClass = this.state.sortActive === 'resource' ? sort : '';
        const progressClass = this.state.sortActive === 'progress' ? sort : '';

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

                {!this.state.visible ? null : (
                    <div className='menu'>
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
                                    value={this.state.search}
                                    onChange={this.updateResourceList}
                                    placeholder='Filter resources'
                                />
                            </Localized>
                        </div>

                        <div className='header'>
                            <Localized id='resource-ResourceMenu--resource'>
                                <span
                                    className='resource'
                                    onClick={this.sortByResource}
                                >
                                    Resource
                                </span>
                            </Localized>
                            <span
                                className={'resource icon ' + resourceClass}
                                onClick={this.sortByResource}
                            />
                            <Localized id='resource-ResourceMenu--progress'>
                                <span
                                    className='progress'
                                    onClick={this.sortByProgress}
                                >
                                    Progress
                                </span>
                            </Localized>
                            <span
                                className={'progress icon ' + progressClass}
                                onClick={this.sortByProgress}
                            />
                        </div>

                        <ul>
                            {resourceElements.length ? (
                                (this.state.sortActive === 'resource'
                                    ? resourceElements.sort((a, b) => {
                                          const resourceA = this.getResource(a);
                                          const resourceB = this.getResource(b);

                                          let result = 0;

                                          if (resourceA < resourceB) {
                                              result = -1;
                                          }
                                          if (resourceA > resourceB) {
                                              result = 1;
                                          }

                                          return this.state.sortAsc
                                              ? result
                                              : result * -1;
                                      })
                                    : resourceElements.sort((a, b) => {
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
                                ).map((resource, index) => {
                                    return (
                                        <ResourceItem
                                            parameters={parameters}
                                            resource={resource}
                                            navigateToPath={this.navigateToPath}
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
                                    onClick={this.navigateToPath}
                                >
                                    <Localized id='resource-ResourceMenu--all-resources'>
                                        <span>All Resources</span>
                                    </Localized>
                                    <ResourcePercent
                                        resource={resources.allResources}
                                    />
                                </a>
                            </li>
                            <li>
                                <a
                                    href={`/${parameters.locale}/all-projects/all-resources/`}
                                    onClick={this.navigateToPath}
                                >
                                    <Localized id='resource-ResourceMenu--all-projects'>
                                        <span>All Projects</span>
                                    </Localized>
                                </a>
                            </li>
                        </ul>
                    </div>
                )}
            </li>
        );
    }
}

export default onClickOutside(ResourceMenuBase);
