import { Localized, useLocalization } from '@fluent/react';
import React, { useContext } from 'react';

import type { RequestedEntityLocation } from '~/api/entity';
import { Locale } from '~/context/Locale';
import { emptyParams, Location } from '~/context/Location';
import { useProject } from '~/modules/project';

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

  if (!entityLocation) {
    return null;
  }

  const { push } = location;
  const allProjects = location.project === 'all-projects';
  const allResources =
    !location.resource || location.resource === 'all-resources';
  const sameProject = entityLocation.project === location.project;

  const goToString = () =>
    push({
      ...emptyParams,
      project: entityLocation.project,
      resource: entityLocation.resource,
      entity: entityLocation.pk,
    });

  const showMatching = () => push({ entity: 0 });

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

  const filters = (
    ['status', 'extra', 'tag', 'author', 'time'] as const
  ).flatMap((key) => location[key]?.split(',') ?? []);
  const [uiBundle] = l10n.bundles;
  const filterList = new Intl.ListFormat(
    uiBundle?.locales[0] ?? 'en-US',
  ).format(filters);

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
            <button className='primary' onClick={goToString} />
          </Localized>
          <Localized id='entities-StringNotFound--show-matching'>
            <button className='secondary' onClick={showMatching} />
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
            <Localized id='entities-StringNotFound--string-details'>
              <h3 />
            </Localized>
            <div className='fields'>
              {!sameProject && (
                <Detail labelId='entities-StringNotFound--label-project'>
                  {entityLocation.project_name}
                </Detail>
              )}
              <Detail labelId='entities-StringNotFound--label-resource'>
                {entityLocation.resource}
              </Detail>
            </div>
          </section>
        </div>
      </div>
    </section>
  );
}
