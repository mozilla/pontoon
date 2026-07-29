import { Localized } from '@fluent/react';
import React, { useContext } from 'react';

import type { RequestedEntityLocation } from '~/api/entity';
import { emptyParams, Location } from '~/context/Location';
import { useProject } from '~/modules/project';

import './StringNotFound.css';

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
  const { name: viewProjectName } = useProject();

  if (!entityLocation) {
    return null;
  }

  const { push } = location;
  const stringId = String(entityLocation.pk);
  const stringProjectSlug = entityLocation.project;
  const stringProject = entityLocation.project_name;
  const stringResource = entityLocation.resource;

  const viewProjectSlug = location.project;
  const viewProject = viewProjectName;
  const viewResource = location.resource;
  const allProjects = viewProjectSlug === 'all-projects';
  const allResources = !viewResource || viewResource === 'all-resources';
  const sameProject = stringProjectSlug === viewProjectSlug;

  const filteredOut =
    !allProjects &&
    sameProject &&
    (allResources || stringResource === viewResource);

  const goToString = () =>
    push({
      ...emptyParams,
      project: stringProjectSlug,
      resource: stringResource,
      entity: entityLocation.pk,
    });

  const showMatching = () => push({ entity: 0 });

  let descriptionId: string;
  if (filteredOut) {
    descriptionId = 'entities-StringNotFound--description-filtered';
  } else if (allProjects) {
    descriptionId = 'entities-StringNotFound--description-in-all-projects';
  } else if (!sameProject) {
    descriptionId = 'entities-StringNotFound--description-in-project';
  } else {
    descriptionId = 'entities-StringNotFound--description-in-resource';
  }

  return (
    <section id='string-not-found'>
      <div className='inner'>
        <Localized
          id={descriptionId}
          vars={{
            stringId,
            stringProject,
            stringResource,
            viewProject,
            viewResource,
          }}
          elems={{
            id: <span className='id' />,
            project: <span className='project' />,
          }}
        >
          <p className='description' />
        </Localized>
        <div className='actions'>
          <Localized id='entities-StringNotFound--go-to-string'>
            <button onClick={goToString} />
          </Localized>
          <Localized id='entities-StringNotFound--show-matching'>
            <button onClick={showMatching} />
          </Localized>
        </div>
      </div>
    </section>
  );
}
