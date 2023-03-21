import { Localized } from '@fluent/react';
import classNames from 'classnames';
import React, { useCallback, useContext, useRef, useState } from 'react';

import { Locale, Localization } from '~/context/Locale';
import type { Location } from '~/context/Location';
import type { ProjectState } from '~/modules/project';
import { useOnDiscard } from '~/utils';

import { ProjectItem } from './ProjectItem';

import './ProjectMenu.css';

type Props = {
  parameters: Location;
  project: ProjectState;
  navigateToPath: (arg0: string) => void;
};

type ProjectMenuProps = {
  parameters: Location;
  onDiscard: () => void;
  onNavigate: (e: React.MouseEvent<HTMLAnchorElement>) => void;
};

export function ProjectMenuDialog({
  parameters,
  onDiscard,
  onNavigate,
}: ProjectMenuProps): React.ReactElement<'div'> {
  // Searching
  const { localizations } = useContext(Locale);
  const [search, setSearch] = useState('');

  const updateProjectList = (e: React.SyntheticEvent<HTMLInputElement>) => {
    setSearch(e.currentTarget.value);
  };

  // Sorting
  const [sortActive, setSortActive] = React.useState<'project' | 'progress'>(
    'project',
  );
  const [sortAsc, setSortAsc] = React.useState(true);

  const sortByProject = () => {
    setSortActive('project');
    setSortAsc(sortActive !== 'project' || !sortAsc);
  };
  const sortByProgress = () => {
    setSortActive('progress');
    setSortAsc(sortActive !== 'progress' || !sortAsc);
  };

  const sort = sortAsc ? 'fa fa-caret-up' : 'fa fa-caret-down';
  const projectClass = sortActive === 'project' ? sort : '';
  const progressClass = sortActive === 'progress' ? sort : '';

  // Discarding menu
  const ref = useRef(null);
  useOnDiscard(ref, onDiscard);

  const search_ = search.toLowerCase();
  const localizationElements = localizations
    .filter((lc) => !search_ || lc.project.name.toLowerCase().includes(search_))
    .sort(sortBy(sortActive, sortAsc));

  return (
    <div ref={ref} className='menu'>
      <div className='search-wrapper'>
        <div className='icon fa fa-search'></div>
        <Localized
          id='project-ProjectMenu--search-placeholder'
          attrs={{ placeholder: true }}
        >
          <input
            type='search'
            autoComplete='off'
            autoFocus
            value={search}
            onChange={updateProjectList}
            placeholder='Filter projects'
          />
        </Localized>
      </div>

      <div className='header'>
        <Localized id='project-ProjectMenu--project'>
          <span className='project' onClick={sortByProject}>
            PROJECT
          </span>
        </Localized>
        <span
          className={'project icon ' + projectClass}
          onClick={sortByProject}
        />
        <Localized id='project-ProjectMenu--progress'>
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
        {localizationElements.length ? (
          localizationElements.map((localization, index) => (
            <ProjectItem
              location={parameters}
              localization={localization}
              navigateToPath={onNavigate}
              key={index}
            />
          ))
        ) : (
          // No projects found
          <Localized id='project-ProjectMenu--no-results'>
            <li className='no-results'>No results</li>
          </Localized>
        )}
      </ul>
    </div>
  );
}

/**
 * Render a project breadcrumb for the main navigation bar in the regular view.
 *
 * In the All projects view, render project menu, which allows switching to the
 * regular view without reloading the Translate app.
 */
export function ProjectMenu({
  navigateToPath,
  parameters,
  project,
}: Props): React.ReactElement<'li'> {
  const { code } = useContext(Locale);
  const [visible, setVisible] = useState(false);

  const toggleVisibility = useCallback(() => setVisible((prev) => !prev), []);
  const handleDiscard = useCallback(() => setVisible(false), []);

  const handleNavigate = useCallback(
    (ev: React.MouseEvent<HTMLAnchorElement>) => {
      ev.preventDefault();
      navigateToPath(ev.currentTarget.pathname);
      setVisible(false);
    },
    [navigateToPath],
  );

  if (parameters.project !== 'all-projects') {
    return (
      <li>
        <a href={`/${code}/${project.slug}/`}>{project.name}</a>
      </li>
    );
  }

  const className = classNames('project-menu', visible ? null : 'closed');
  return (
    <li className={className}>
      <div className='selector unselectable' onClick={toggleVisibility}>
        <Localized id='project-ProjectMenu--all-projects'>
          <span>All Projects</span>
        </Localized>
        <span className='icon fa fa-caret-down'></span>
      </div>
      {visible && (
        <ProjectMenuDialog
          parameters={parameters}
          onDiscard={handleDiscard}
          onNavigate={handleNavigate}
        />
      )}
    </li>
  );
}

function sortBy(sortActive: 'project' | 'progress', sortAsc: boolean) {
  const get =
    sortActive === 'project'
      ? (lc: Localization) => lc.project.name
      : (lc: Localization) =>
          (lc.approvedStrings + lc.stringsWithWarnings) / lc.totalStrings;

  return function (a: Localization, b: Localization) {
    const aa = get(a);
    const bb = get(b);
    if (aa < bb) {
      return sortAsc ? -1 : 1;
    }
    if (aa > bb) {
      return sortAsc ? 1 : -1;
    }
    return 0;
  };
}
