import api, { Entities, EntityTranslation, EntitySiblings } from '~/core/api';
import { update as updateStats } from '~/core/stats/actions';
import type { AppDispatch } from '~/store';

export const RECEIVE_ENTITIES = 'entities/RECEIVE';
export const REQUEST_ENTITIES = 'entities/REQUEST';
export const RESET_ENTITIES = 'entities/RESET';
export const UPDATE_ENTITIES = 'entities/UPDATE';
export const RECEIVE_ENTITY_SIBLINGS = 'entities/RECEIVE_SIBLINGS';

/** Indicate that entities are currently being fetched.  */
type RequestAction = {
  type: typeof REQUEST_ENTITIES;
};

/** Update entities to a new set.  */
type ReceiveAction = {
  type: typeof RECEIVE_ENTITIES;
  entities: Entities;
  hasMore: boolean;
};

/** Update the siblings of an entity.  */
type ReceiveSiblingsAction = {
  type: typeof RECEIVE_ENTITY_SIBLINGS;
  siblings: EntitySiblings;
  entity: number;
};

type ResetAction = {
  type: typeof RESET_ENTITIES;
};

/** Update the active translation of an entity.  */
type UpdateAction = {
  type: typeof UPDATE_ENTITIES;
  entity: number;
  pluralForm: number;
  translation: EntityTranslation;
};

export type Action =
  | ReceiveAction
  | ReceiveSiblingsAction
  | RequestAction
  | ResetAction
  | UpdateAction;

export const resetEntities = (): ResetAction => ({ type: RESET_ENTITIES });

export const updateEntityTranslation = (
  entity: number,
  pluralForm: number,
  translation: EntityTranslation,
): UpdateAction => ({ type: UPDATE_ENTITIES, entity, pluralForm, translation });

/** Fetch entities and their translation.  */
export const fetchEntities =
  (
    locale: string,
    project: string,
    resource: string,
    entityIds: Array<number> | null | undefined,
    exclude: Array<number>,
    entity: string | null | undefined,
    search: string | null | undefined,
    status: string | null | undefined,
    extra: string | null | undefined,
    tag: string | null | undefined,
    author: string | null | undefined,
    time: string | null | undefined,
  ) =>
  async (dispatch: AppDispatch) => {
    dispatch({ type: REQUEST_ENTITIES });

    const content = await api.entity.getEntities(
      locale,
      project,
      resource,
      entityIds,
      exclude,
      entity,
      search,
      status,
      extra,
      tag,
      author,
      time,
      false,
    );

    if (content.entities) {
      dispatch({
        type: RECEIVE_ENTITIES,
        entities: content.entities,
        hasMore: content.has_next,
      });
      dispatch(updateStats(content.stats));
    }
  };

export const fetchSiblingEntities =
  (entity: number, locale: string) => async (dispatch: AppDispatch) => {
    const siblings = await api.entity.getSiblingEntities(entity, locale);
    if (siblings) {
      dispatch({ type: RECEIVE_ENTITY_SIBLINGS, siblings, entity });
    }
  };
