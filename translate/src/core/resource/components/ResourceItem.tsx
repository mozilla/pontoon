import React from 'react';

import type { Location } from '~/context/Location';

import type { Resource } from '../actions';
import './ResourceItem.css';
import { ResourcePercent } from './ResourcePercent';

type Props = {
  location: Location;
  resource: Resource;
  navigateToPath: (arg0: React.MouseEvent<HTMLAnchorElement>) => void;
};

/**
 * Render a resource menu item.
 */
export const ResourceItem = ({
  location,
  resource,
  navigateToPath,
}: Props): React.ReactElement<'li'> => (
  <li className={location.resource === resource.path ? 'current' : undefined}>
    <a
      href={`/${location.locale}/${location.project}/${resource.path}/`}
      onClick={navigateToPath}
    >
      <span className='path' title={resource.path}>
        {resource.path}
      </span>
      <ResourcePercent resource={resource} />
    </a>
  </li>
);
