import { Localized } from '@fluent/react';
import classNames from 'classnames';
import React, { useCallback, useContext, useRef, useState } from 'react';

import { Location } from '~/context/Location';
import { useOnDiscard } from '~/utils';

import type { Resource } from '../actions';
import { useResource } from '../hooks';
import { ResourceItem } from './ResourceItem';
import './ResourceMenu.css';
import { ResourcePercent } from './ResourcePercent';

type Props = {
  navigateToPath: (path: string) => void;
};

type DialogProps = {
  onDiscard: () => void;
  onNavigate: (e: React.MouseEvent<HTMLAnchorElement>) => void;
};

function ResourceMenuDialog({
  onDiscard,
  onNavigate,
}: DialogProps): React.ReactElement<'div'> {
  // Searching
  const [search, setSearch] = useState('');
  const { allResources, resources } = useResource();
  const resourceElements = resources.filter(
    (resource) =>
      resource.path.toLowerCase().indexOf(search.toLowerCase()) > -1,
  );
  const location = useContext(Location);

  const updateResourceList = (e: React.SyntheticEvent<HTMLInputElement>) => {
    setSearch(e.currentTarget.value);
  };

  // Sorting
  const [sortActive, setSortActive] = useState('resource');
  const [sortAsc, setSortAsc] = useState(true);

  const sortByResource = () => {
    setSortActive('resource');
    setSortAsc(sortActive !== 'resource' || !sortAsc);
  };
  const sortByProgress = () => {
    setSortActive('progress');
    setSortAsc(sortActive !== 'progress' || !sortAsc);
  };

  const getProgress = (res: Resource) => {
    const completeStrings =
      res.approvedStrings + res.pretranslatedStrings + res.stringsWithWarnings;
    const percent = Math.floor((completeStrings / res.totalStrings) * 100);
    return percent;
  };

  const getResource = (res: Resource) => {
    return res.path;
  };

  const sort = sortAsc ? 'fa fa-caret-up' : 'fa fa-caret-down';
  const resourceClass = sortActive === 'resource' ? sort : '';
  const progressClass = sortActive === 'progress' ? sort : '';

  // Discarding menu
  const ref = useRef(null);
  useOnDiscard(ref, onDiscard);

  return (
    <div ref={ref} className='menu'>
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
            value={search}
            onChange={updateResourceList}
            placeholder='Filter resources'
          />
        </Localized>
      </div>

      <div className='header'>
        <Localized id='resource-ResourceMenu--resource'>
          <span className='resource' onClick={sortByResource}>
            RESOURCE
          </span>
        </Localized>
        <span
          className={'resource icon ' + resourceClass}
          onClick={sortByResource}
        />
        <Localized id='resource-ResourceMenu--progress'>
          <span className='progress' onClick={sortByProgress}>
            PROGRESS
          </span>
        </Localized>
        <span
          className={'progress icon ' + progressClass}
          onClick={sortByProgress}
        />
      </div>

      <ul>
        {resourceElements.length ? (
          (sortActive === 'resource'
            ? resourceElements.sort((a, b) => {
                const resourceA = getResource(a);
                const resourceB = getResource(b);

                let result = 0;

                if (resourceA < resourceB) {
                  result = -1;
                }
                if (resourceA > resourceB) {
                  result = 1;
                }

                return sortAsc ? result : result * -1;
              })
            : resourceElements.sort((a, b) => {
                const percentA = getProgress(a);
                const percentB = getProgress(b);

                let result = 0;

                if (percentA < percentB) {
                  result = -1;
                }
                if (percentA > percentB) {
                  result = 1;
                }

                return sortAsc ? result : result * -1;
              })
          ).map((resource, index) => {
            return (
              <ResourceItem
                location={location}
                resource={resource}
                navigateToPath={onNavigate}
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
            location.resource === 'all-resources' ? 'current' : undefined
          }
        >
          <a
            href={`/${location.locale}/${location.project}/all-resources/`}
            onClick={onNavigate}
          >
            <Localized id='resource-ResourceMenu--all-resources'>
              <span>All Resources</span>
            </Localized>
            <ResourcePercent resource={allResources} />
          </a>
        </li>
        <li>
          <a
            href={`/${location.locale}/all-projects/all-resources/`}
            onClick={onNavigate}
          >
            <Localized id='resource-ResourceMenu--all-projects'>
              <span>All Projects</span>
            </Localized>
          </a>
        </li>
      </ul>
    </div>
  );
}

/**
 * Render a resource menu for the main navigation bar.
 *
 * Allows to switch between resources without reloading the Translate app.
 */
export function ResourceMenu({
  navigateToPath,
}: Props): React.ReactElement<'li'> | null {
  const [visible, setVisible] = useState(false);
  const toggleVisible = useCallback(() => setVisible((prev) => !prev), []);
  const handleDiscard = useCallback(() => setVisible(false), []);
  const { project, resource } = useContext(Location);

  const handleNavigate = useCallback(
    (ev: React.MouseEvent<HTMLAnchorElement>) => {
      ev.preventDefault();
      navigateToPath(ev.currentTarget.pathname);
      setVisible(false);
    },
    [navigateToPath],
  );

  if (project === 'all-projects') {
    return null;
  }

  const className = classNames('resource-menu', visible ? null : 'closed');

  const resourceName =
    resource === 'all-resources' ? (
      <Localized id='resource-ResourceMenu--all-resources'>
        All Resources
      </Localized>
    ) : (
      resource.split('/').slice(-1)[0]
    );

  return (
    <li className={className}>
      <div
        className='selector unselectable'
        onClick={toggleVisible}
        title={resource}
      >
        <span>{resourceName}</span>
        <span className='icon fa fa-caret-down'></span>
      </div>

      {visible && (
        <ResourceMenuDialog
          onDiscard={handleDiscard}
          onNavigate={handleNavigate}
        />
      )}
    </li>
  );
}
