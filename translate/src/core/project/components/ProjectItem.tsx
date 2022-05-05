import React from 'react';

import type { Localization } from '~/context/locale';
import type { LocationType } from '~/context/location';

import './ProjectItem.css';

type Props = {
  location: LocationType;
  localization: Localization;
  navigateToPath: (arg0: React.MouseEvent<HTMLAnchorElement>) => void;
};

/**
 * Render a project menu item.
 */
export function ProjectItem({
  location: { locale, project },
  localization,
  navigateToPath,
}: Props): React.ReactElement<'li'> {
  const { name, slug } = localization.project;
  const className = project === slug ? 'current' : undefined;

  const { approvedStrings, stringsWithWarnings, totalStrings } = localization;
  const percent =
    Math.floor(((approvedStrings + stringsWithWarnings) / totalStrings) * 100) +
    '%';

  return (
    <li className={className}>
      <a href={`/${locale}/${slug}/all-resources/`} onClick={navigateToPath}>
        <span className='project' title={name}>
          {name}
        </span>
        <span className='percent'>{percent}</span>
      </a>
    </li>
  );
}
