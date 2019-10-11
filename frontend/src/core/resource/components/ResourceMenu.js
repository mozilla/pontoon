/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';
import onClickOutside from 'react-onclickoutside';

import './ResourceMenu.css';

import ResourceItem from './ResourceItem.js';
import ResourcePercent from './ResourcePercent.js';

import type { NavigationParams } from 'core/navigation';
import type { ResourcesState } from '..';


type Props = {|
    parameters: NavigationParams,
    resources: ResourcesState,
    navigateToPath: (string) => void,
|};

type State = {|
    search: string,
    visible: boolean,
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
            sortActive: false,
            sortAsc: false,
        };
    }

    toggleVisibility = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
    }

    toggleSort = () => {
        this.setState(() => {
            return {
                sortActive: false,
            };
        });
    }

    handleSort = () => {
        this.setState((state) => {
            return {
                sortActive: true,
                sortAsc: !state.sortAsc
            };
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

    updateResourceList = (event: SyntheticInputEvent<HTMLInputElement>) => {
        this.setState({
            search: event.currentTarget.value,
        });
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
            resourceName = 'All Resources';
        }

        // Search resources
        const search = this.state.search;
        const resourceElements = resources.resources.filter(resource =>
            resource.path.toLowerCase().indexOf(search.toLowerCase()) > -1
        );

        function getPercentCompletion(el){
            let approvedStrings = el.approvedStrings,
                stringsWithWarnings = el.stringsWithWarnings,
                totalStrings = el.totalStrings;

            const completeStrings = approvedStrings + stringsWithWarnings;

            const percent = Math.floor(completeStrings / totalStrings * 100);
            return percent;
        }

        return <li className={ className }>
            <div
                className="selector unselectable"
                onClick={ this.toggleVisibility }
                title={ parameters.resource }
            >
                <span>{ resourceName }</span>
                <span className="icon fa fa-caret-down"></span>
            </div>

            { !this.state.visible ? null :
            <div className="menu">
                <div className="search-wrapper">
                    <div className="icon fa fa-search"></div>
                    <input
                        type="search"
                        autoComplete="off"
                        autoFocus
                        value={ this.state.search }
                        onChange={ this.updateResourceList }
                    />
                </div>

                <div className="resources-list-header">
                    <span className="resource" onClick={ this.toggleSort }> RESOURCE </span>
                    <span className="completion" onClick={ this.handleSort } >% COMPLETION </span>
                    <span className={"completion icon " + (this.state.sortActive ? (this.state.sortAsc ? "fa fa-caret-up" : "fa fa-caret-down") : "")}
                          onClick={ this.handleSort }
                    />
                </div>

                <ul>
                    { resourceElements.length ? (
                            (this.state.sortActive
                                ? resourceElements.sort( (a,b) => {
                                    let percentA = getPercentCompletion(a),
                                        percentB = getPercentCompletion(b);

                                    let result = 0;

                                    if (percentA < percentB ) {
                                        result = -1;
                                    }
                                    if (percentA > percentB) {
                                        result = 1;
                                    }
                                    return this.state.sortAsc ? result :  result * -1;

                                })
                                : resourceElements)
                                .map((resource, index) => {
                            return <ResourceItem
                                parameters={ parameters }
                                resource={ resource }
                                navigateToPath={ this.navigateToPath }
                                key={ index }
                            />;
                        }))
                        :
                        // No resources found
                        <Localized id='resource-ResourceMenu--no-results'>
                            <li className="no-results">No results</li>
                        </Localized>
                    }
                </ul>

                <ul className="static-links">
                    <li className={ parameters.resource === 'all-resources' ? 'current' : null }>
                        <a
                            href={ `/${parameters.locale}/${parameters.project}/all-resources/` }
                            onClick={ this.navigateToPath }
                        >
                            <Localized id='resource-ResourceMenu--all-resources'>
                                <span>All Resources</span>
                            </Localized>
                            <ResourcePercent resource={ resources.allResources } />
                        </a>
                    </li>
                    <li>
                        <a
                            href={ `/${parameters.locale}/all-projects/all-resources/` }
                            onClick={ this.navigateToPath }
                        >
                            <Localized id='resource-ResourceMenu--all-projects'>
                                <span>All Projects</span>
                            </Localized>
                        </a>
                    </li>
                </ul>
            </div>
            }
        </li>;
    }
}

export default onClickOutside(ResourceMenuBase);
