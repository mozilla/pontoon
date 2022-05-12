import {
  Action,
  ResponseType,
  CHECK_BATCHACTIONS,
  RECEIVE_BATCHACTIONS,
  REQUEST_BATCHACTIONS,
  RESET_BATCHACTIONS,
  RESET_BATCHACTIONS_RESPONSE,
  TOGGLE_BATCHACTIONS,
  UNCHECK_BATCHACTIONS,
} from './actions';

// Name of this module.
// Used as the key to store this module's reducer.
export const BATCHACTIONS = 'batchactions';

export type BatchActionsState = {
  readonly entities: Array<number>;
  readonly lastCheckedEntity: number | null | undefined;
  readonly requestInProgress: string | null | undefined;
  readonly response: ResponseType | null | undefined;
};

const initial: BatchActionsState = {
  entities: [],
  lastCheckedEntity: null,
  requestInProgress: null,
  response: null,
};

const checkEntities = (
  stateEntities: Array<number>,
  actionEntities: Array<number>,
) =>
  // Union with duplicates removed
  stateEntities.concat(
    actionEntities.filter((e) => !stateEntities.includes(e)),
  );

const toggleEntity = (entities: Array<number>, entity: number) =>
  entities.includes(entity)
    ? // Remove entity if present
      entities.filter((e) => e !== entity)
    : // Add entity if not present
      entities.concat([entity]);

const uncheckEntities = (
  stateEntities: Array<number>,
  actionEntities: Array<number>,
) => stateEntities.filter((e) => actionEntities.indexOf(e) < 0);

export function reducer(
  state: BatchActionsState = initial,
  action: Action,
): BatchActionsState {
  switch (action.type) {
    case CHECK_BATCHACTIONS:
      return {
        ...state,
        entities: checkEntities(state.entities, action.entities),
        lastCheckedEntity: action.lastCheckedEntity,
      };
    case RECEIVE_BATCHACTIONS:
      return {
        ...state,
        requestInProgress: null,
        response: action.response,
      };
    case REQUEST_BATCHACTIONS:
      return {
        ...state,
        requestInProgress: action.source,
      };
    case RESET_BATCHACTIONS:
      return {
        ...initial,
      };
    case RESET_BATCHACTIONS_RESPONSE:
      return {
        ...state,
        response: initial.response,
      };
    case TOGGLE_BATCHACTIONS:
      return {
        ...state,
        entities: toggleEntity(state.entities, action.entity),
        lastCheckedEntity: action.entity,
      };
    case UNCHECK_BATCHACTIONS:
      return {
        ...state,
        entities: uncheckEntities(state.entities, action.entities),
        lastCheckedEntity: action.lastCheckedEntity,
      };
    default:
      return state;
  }
}
