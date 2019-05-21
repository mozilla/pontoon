/* @flow */

import * as React from 'react';

import './ResourceItem.css';

import { ResourcePercent } from '..';

import type { NavigationParams } from 'core/navigation';
import type { Resource } from '..';


type Props = {|
    index: number,
    parameters: NavigationParams,
    resource: Resource,
    navigateToPath: (SyntheticMouseEvent<>) => void,
|};


/**
 * Render a resource menu item.
 */
export default function ResourceItem(props: Props) {
    const { index, parameters, resource, navigateToPath } = props;
    const className = parameters.resource === resource.path ? 'current' : null;

    return <li className={ className } key={ index }>
        <a
            href={ `/${parameters.locale}/${parameters.project}/${resource.path}/` }
            onClick={ navigateToPath }
        >
            <span>{ resource.path }</span>
            <ResourcePercent resource={ resource } />
        </a>
    </li>;
}
