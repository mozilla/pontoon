import React from 'react';

import type { Localization } from '~/context/locale';
import type { LocationType } from '~/context/location';

import './ProjectItem.css';
import ProjectPercent from './ProjectPercent';

type Props = {
  parameters: LocationType;
  localization: Localization;
  navigateToPath: (arg0: React.MouseEvent<HTMLAnchorElement>) => void;
};

/**
 * Render a project menu item.
 */
export default function ProjectItem(props: Props): React.ReactElement<'li'> {
  const { parameters, localization, navigateToPath } = props;
  const project = localization.project;
  const className = parameters.project === project.slug ? 'current' : undefined;

  return (
    <li className={className}>
      <a
        href={`/${parameters.locale}/${project.slug}/all-resources/`}
        onClick={navigateToPath}
      >
        <span className='project' title={project.name}>
          {project.name}
        </span>
        <ProjectPercent localization={localization} />
      </a>
    </li>
  );
}
