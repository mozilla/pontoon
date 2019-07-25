/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';
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

                <ul>
                    { resourceElements.length ?
                        resourceElements.map((resource, index) => {
                            return <ResourceItem
                                parameters={ parameters }
                                resource={ resource }
                                navigateToPath={ this.navigateToPath }
                                key={ index }
                            />;
                        })
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
