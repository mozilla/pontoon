import * as React from 'react';

import type { LocationType } from '~/context/location';

import type { Resource } from '../index';
import './ResourceItem.css';
import ResourcePercent from './ResourcePercent';

type Props = {
  parameters: LocationType;
  resource: Resource;
  navigateToPath: (arg0: React.MouseEvent<HTMLAnchorElement>) => void;
};

/**
 * Render a resource menu item.
 */
export default function ResourceItem(props: Props): React.ReactElement<'li'> {
  const { parameters, resource, navigateToPath } = props;
  const className =
    parameters.resource === resource.path ? 'current' : undefined;

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
