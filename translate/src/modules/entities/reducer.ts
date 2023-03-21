import type { Entity, EntitySiblings } from '~/api/entity';
import type { EntityTranslation } from '~/api/translation';

import {
  Action,
  RECEIVE_ENTITIES,
  REQUEST_ENTITIES,
  RESET_ENTITIES,
  UPDATE_ENTITIES,
  RECEIVE_ENTITY_SIBLINGS,
} from './actions';

// Name of this module.
// Used as the key to store this module's reducer.
export const ENTITIES = 'entities';

type EntitiesState = {
  readonly entities: Entity[];
  readonly fetching: boolean;
  readonly fetchCount: number;
  readonly hasMore: boolean;
};

function updateEntityTranslation(
  state: EntitiesState,
  entity: number,
  pluralForm: number,
  translation: EntityTranslation,
): Entity[] {
  return state.entities.map((item) => {
    if (item.pk !== entity) {
      return item;
    }

    const translations = [...item.translation];

    // If the plural form is -1, then there's no plural and we should
    // simply update the first translation.
    const plural = pluralForm === -1 ? 0 : pluralForm;
    translations[plural] = translation;

    return {
      ...item,
      translation: translations,
    };
  });
}

function injectSiblingEntities(
  entities: Entity[],
  siblings: EntitySiblings,
  entity: number,
): Entity[] {
  const index = entities.findIndex((item) => item.pk === entity);
  let parentEntity = entities[index];
  const currentPKs = entities.map((e) => e.pk);
  let newEntitiesState = entities.slice();

  // filtering out parent entities already present in the list
  const precedingSiblings = siblings.preceding.filter(
    (sibling) => !currentPKs.includes(sibling.pk),
  );

  const succeedingSiblings = siblings.succeeding.filter(
    (sibling) => !currentPKs.includes(sibling.pk),
  );

  let list = [...precedingSiblings, parentEntity, ...succeedingSiblings];

  newEntitiesState.splice(index, 1, ...list);

  // This block removes duplicated siblings
  newEntitiesState = newEntitiesState.filter(
    (currentValue, index, array) =>
      array.findIndex((e) => e.pk === currentValue.pk) === index,
  );
  return newEntitiesState;
}

const initial: EntitiesState = {
  entities: [],
  fetching: false,
  fetchCount: 0,
  hasMore: true,
};

export function reducer(
  state: EntitiesState = initial,
  action: Action,
): EntitiesState {
  switch (action.type) {
    case RECEIVE_ENTITIES:
      return {
        ...state,
        entities: [...state.entities, ...action.entities],
        fetching: false,
        fetchCount: state.fetchCount + 1,
        hasMore: action.hasMore,
      };
    case REQUEST_ENTITIES:
      return {
        ...state,
        fetching: true,
        hasMore: false,
      };
    case RESET_ENTITIES:
      return {
        ...state,
        entities: [],
        fetching: false,
        hasMore: true,
      };
    case UPDATE_ENTITIES:
      return {
        ...state,
        entities: updateEntityTranslation(
          state,
          action.entity,
          action.pluralForm,
          action.translation,
        ),
      };
    case RECEIVE_ENTITY_SIBLINGS:
      return {
        ...state,
        entities: injectSiblingEntities(
          state.entities,
          action.siblings,
          action.entity,
        ),
      };
    default:
      return state;
  }
}
