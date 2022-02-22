import { createSelector } from 'reselect';

import * as navigation from '~/core/navigation';
import * as user from '~/core/user';

import { NAME } from '.';

import type { Entities, Entity } from '~/core/api';
import type { NavigationParams } from '~/core/navigation';
import type { UserState } from '~/core/user';
import type { RootState } from '../../store';

const entitiesSelector = (state: RootState) => state[NAME].entities;
const userSelector = (state: RootState) => state[user.NAME];

export function _getSelectedEntity(
  entities: ReturnType<typeof entitiesSelector>,
  params: NavigationParams,
): Entity | undefined {
  return entities.find((element) => element.pk === params.entity);
}

/**
 * Return the currently selected Entity object.
 */
export const getSelectedEntity = createSelector(
  entitiesSelector,
  navigation.selectors.getNavigationParams,
  _getSelectedEntity,
);

export function _getNextEntity(
  entities: Entities,
  params: NavigationParams,
): Entity | undefined {
  const currentIndex = entities.findIndex(
    (element) => element.pk === params.entity,
  );

  if (currentIndex === -1) {
    return undefined;
  }

  const next = currentIndex + 1 >= entities.length ? 0 : currentIndex + 1;
  return entities[next];
}

/**
 * Return the Entity that follows the current one in the list.
 */
export const getNextEntity = createSelector(
  entitiesSelector,
  navigation.selectors.getNavigationParams,
  _getNextEntity,
);

export function _getPreviousEntity(
  entities: Entities,
  params: NavigationParams,
): Entity | undefined {
  const currentIndex = entities.findIndex(
    (element) => element.pk === params.entity,
  );

  if (currentIndex === -1) {
    return undefined;
  }

  const previous = currentIndex === 0 ? entities.length - 1 : currentIndex - 1;
  return entities[previous];
}

/**
 * Return the Entity that preceeds the current one in the list.
 */
export const getPreviousEntity = createSelector(
  entitiesSelector,
  navigation.selectors.getNavigationParams,
  _getPreviousEntity,
);

export function _isReadOnlyEditor(entity: Entity, user: UserState): boolean {
  return (entity && entity.readonly) || !user.isAuthenticated;
}

/**
 * Return true if editor must be read-only, which happens when:
 *   - the entity is read-only OR
 *   - the user is not authenticated
 */
export const isReadOnlyEditor = createSelector(
  getSelectedEntity,
  userSelector,
  _isReadOnlyEditor,
);

export default {
  getNextEntity,
  getPreviousEntity,
  getSelectedEntity,
  isReadOnlyEditor,
};
