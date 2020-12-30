/* @flow */

import * as React from 'react';

import './ResourceItem.css';

import ResourcePercent from './ResourcePercent.js';

import type { NavigationParams } from 'core/navigation';
import type { Resource } from '..';

type Props = {|
    parameters: NavigationParams,
    resource: Resource,
    navigateToPath: (SyntheticMouseEvent<HTMLAnchorElement>) => void,
|};

/**
 * Render a resource menu item.
 */
export default function ResourceItem(props: Props) {
    const { parameters, resource, navigateToPath } = props;
    const className = parameters.resource === resource.path ? 'current' : null;

    return (
        <li className={className}>
            <a
                href={`/${parameters.locale}/${parameters.project}/${resource.path}/`}
                onClick={navigateToPath}
            >
                <span className='path' title={resource.path}>
                    {resource.path}
                </span>
                <ResourcePercent resource={resource} />
            </a>
        </li>
    );
}
