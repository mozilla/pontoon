import { Localized, useLocalization } from '@fluent/react';
import React, { useContext, useEffect } from 'react';

import type { RequestedEntityLocation } from '~/api/entity';
import { logUXAction } from '~/api/uxaction';
import { Locale } from '~/context/Locale';
import { emptyParams, Location } from '~/context/Location';
import { useAppSelector } from '~/hooks';
import { useProject } from '~/modules/project';
import { USER } from '~/modules/user';

import './StringNotFound.css';

function Detail({
  labelId,
  children,
}: {
  labelId: string;
  children: React.ReactNode;
}): React.ReactElement<'div'> {
  return (
    <div className='detail'>
      <Localized id={labelId}>
        <span className='label' />
      </Localized>
      <span className='value'>{children}</span>
    </div>
  );
}

/**
 * Shown in the editor panel when the `string` URL parameter points at a valid,
 * viewable string that doesn't match the rest of the query (#2921).
 */
export function StringNotFound({
  entityLocation,
}: {
  entityLocation: RequestedEntityLocation | null;
}): React.ReactElement<'section'> | null {
  const location = useContext(Location);
  const locale = useContext(Locale);
  const { name: viewProjectName } = useProject();
  const { l10n } = useLocalization();
  const isAuthUser = useAppSelector((state) => state[USER].isAuthenticated);

  const allProjects = location.project === 'all-projects';
  const allResources =
    !location.resource || location.resource === 'all-resources';
  const sameProject = entityLocation?.project === location.project;
  const sameResource =
    allResources || entityLocation?.resource === location.resource;
  const stringFilters = entityLocation?.filters ?? [];
  const filteredOut =
    (allProjects || (sameProject && sameResource)) && stringFilters.length > 0;

  const panel = filteredOut ? 'filters' : !sameProject ? 'project' : 'resource';

  const logAction = (action: string) => {
    if (isAuthUser) {
      logUXAction(action, 'String Not Found 1.0', { panel });
    }
  };

  useEffect(() => {
    if (entityLocation) {
      logAction('Render: String not found');
    }
  }, [isAuthUser, entityLocation?.pk]);

  if (!entityLocation) {
    return null;
  }

  const { push } = location;

  const goToString = (ev: React.MouseEvent) => {
    ev.preventDefault();
    logAction('Click: String not found, go to string');
    push({
      ...emptyParams,
      project: entityLocation.project,
      resource: entityLocation.resource,
      entity: entityLocation.pk,
    });
  };

  const showMatching = (ev: React.MouseEvent) => {
    ev.preventDefault();
    logAction('Click: String not found, show matching');
    push({ entity: 0 });
  };

  const goToStringHref = `/${location.locale}/${entityLocation.project}/${entityLocation.resource}/?string=${entityLocation.pk}`;
  const showMatchingUrl = new URL(window.location.href);
  showMatchingUrl.searchParams.delete('string');
  const showMatchingHref = showMatchingUrl.pathname + showMatchingUrl.search;

  const requestProject = allProjects
    ? l10n.getString(
        'entities-StringNotFound--all-projects',
        null,
        'All Projects',
      )
    : viewProjectName || location.project;
  const requestResource = allResources
    ? l10n.getString(
        'entities-StringNotFound--all-resources',
        null,
        'All Resources',
      )
    : location.resource;

  const [uiBundle] = l10n.bundles;
  const formatFilters = (slugs: readonly string[]) =>
    new Intl.ListFormat(uiBundle?.locales[0] ?? 'en-US').format(slugs);

  const filters = (
    ['status', 'extra', 'tag', 'author', 'time'] as const
  ).flatMap((key) => location[key]?.split(',') ?? []);
  const filterList = formatFilters(filters);

  const stringFilterList = formatFilters(stringFilters);

  return (
    <section id='string-not-found'>
      <div className='inner'>
        <Localized id='entities-StringNotFound--title'>
          <h2 className='title' />
        </Localized>
        <Localized id='entities-StringNotFound--description'>
          <p className='description' />
        </Localized>

        <div className='actions'>
          <Localized id='entities-StringNotFound--go-to-string'>
            <a
              className='primary'
              href={goToStringHref}
              title={goToStringHref}
              onClick={goToString}
            />
          </Localized>
          <Localized id='entities-StringNotFound--show-matching'>
            <a
              className='secondary'
              href={showMatchingHref}
              title={showMatchingHref}
              onClick={showMatching}
            />
          </Localized>
        </div>

        <div className='details'>
          <section className='group'>
            <Localized id='entities-StringNotFound--request-details'>
              <h3 />
            </Localized>
            <div className='fields'>
              <Detail labelId='entities-StringNotFound--label-locale'>
                {locale.name} <span className='accent'>{locale.code}</span>
              </Detail>
              <Detail labelId='entities-StringNotFound--label-project'>
                {requestProject}
              </Detail>
              <Detail labelId='entities-StringNotFound--label-resource'>
                {requestResource}
              </Detail>
              {filters.length > 0 && (
                <Detail labelId='entities-StringNotFound--label-filters'>
                  {filterList}
                </Detail>
              )}
              <Detail labelId='entities-StringNotFound--label-string'>
                {entityLocation.pk}
              </Detail>
            </div>
          </section>

          <section className='group'>
            <Localized
              id='entities-StringNotFound--string-details'
              vars={{ stringId: String(entityLocation.pk) }}
            >
              <h3 />
            </Localized>
            <div className='fields'>
              {panel === 'filters' ? (
                <Detail labelId='entities-StringNotFound--label-filters'>
                  {stringFilterList}
                </Detail>
              ) : (
                <>
                  {panel === 'project' && (
                    <Detail labelId='entities-StringNotFound--label-project'>
                      {entityLocation.project_name}
                    </Detail>
                  )}
                  <Detail labelId='entities-StringNotFound--label-resource'>
                    {entityLocation.resource}
                  </Detail>
                </>
              )}
            </div>
          </section>
        </div>
      </div>
    </section>
  );
}
