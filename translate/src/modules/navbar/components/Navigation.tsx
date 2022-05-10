import React, { useCallback, useContext, useEffect } from 'react';
import { Locale } from '~/context/locale';
import { Location } from '~/context/location';
import { useCheckUnsavedChanges } from '~/context/unsavedChanges';

import { useProject } from '~/core/project';
import { ProjectMenu } from '~/core/project/components/ProjectMenu';
import { ResourceMenu } from '~/core/resource/components/ResourceMenu';

import './Navigation.css';

/**
 * Render a breadcrumb-like navigation bar.
 *
 * Allows to exit the Translate app to go back to team or project dashboards.
 */
export function Navigation(): React.ReactElement<'nav'> {
  const location = useContext(Location);
  const { code, name } = useContext(Locale);
  const projectState = useProject();
  const checkUnsavedChanges = useCheckUnsavedChanges();

  useEffect(() => {
    if (name && projectState?.name) {
      document.title = `${name} (${code}) · ${projectState.name}`;
    }
  }, [code, name, projectState]);

  const navigateToPath = useCallback(
    (path: string) => checkUnsavedChanges(() => location.push(path)),
    [],
  );

  return (
    <nav className='navigation'>
      <ul>
        <li>
          <a href='/'>
            <img
              src='/static/img/logo.svg'
              width='32'
              height='32'
              alt='Pontoon logo'
            />
          </a>
        </li>
        <li>
          <a href={`/${code}/`}>
            {name}
            <span className='locale-code'>{code}</span>
          </a>
        </li>
        <ProjectMenu
          parameters={location}
          project={projectState}
          navigateToPath={navigateToPath}
        />
        <ResourceMenu navigateToPath={navigateToPath} />
      </ul>
    </nav>
  );
}
