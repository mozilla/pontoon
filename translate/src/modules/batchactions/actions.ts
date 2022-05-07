import { batchEditEntities, fetchEntities, fetchEntityIds } from '~/api/entity';
import type { EntityTranslation } from '~/api/translation';
import type { LocationType } from '~/context/location';
import { updateEntityTranslation } from '~/core/entities/actions';
import { updateResource } from '~/core/resource/actions';
import { updateStats } from '~/core/stats/actions';
import {
  get as getHistory,
  request as requestHistory,
} from '~/modules/history/actions';
import type { AppDispatch } from '~/store';

export const CHECK_BATCHACTIONS = 'batchactions/CHECK';
export const RECEIVE_BATCHACTIONS = 'batchactions/RECEIVE';
export const REQUEST_BATCHACTIONS = 'batchactions/REQUEST';
export const RESET_BATCHACTIONS = 'batchactions/RESET';
export const RESET_BATCHACTIONS_RESPONSE = 'batchactions/RESET_RESPONSE';
export const TOGGLE_BATCHACTIONS = 'batchactions/TOGGLE';
export const UNCHECK_BATCHACTIONS = 'batchactions/UNCHECK';

export type ResponseType = {
  action: string;
  changedCount: number | null | undefined;
  invalidCount: number | null | undefined;
  error: boolean | null | undefined;
};

export type Action =
  | CheckAction
  | ReceiveAction
  | RequestAction
  | ResetAction
  | ResetResponseAction
  | ToggleAction
  | UncheckAction;

type CheckAction = {
  type: typeof CHECK_BATCHACTIONS;
  entities: Array<number>;
  lastCheckedEntity: number;
};

type ReceiveAction = {
  type: typeof RECEIVE_BATCHACTIONS;
  response: ResponseType | null | undefined;
};

type RequestAction = {
  type: typeof REQUEST_BATCHACTIONS;
  source: string;
};

type ResetAction = {
  type: typeof RESET_BATCHACTIONS;
};

type ResetResponseAction = {
  type: typeof RESET_BATCHACTIONS_RESPONSE;
};

type ToggleAction = {
  type: typeof TOGGLE_BATCHACTIONS;
  entity: number;
};

type UncheckAction = {
  type: typeof UNCHECK_BATCHACTIONS;
  entities: Array<number>;
  lastCheckedEntity: number;
};

export const checkSelection = (
  entities: Array<number>,
  lastCheckedEntity: number,
): CheckAction => ({
  type: CHECK_BATCHACTIONS,
  entities,
  lastCheckedEntity,
});

const updateUI =
  (location: LocationType, selectedEntity: number, entityIds: number[]) =>
  async (dispatch: AppDispatch) => {
    const entitiesData = await fetchEntities({ ...location, list: entityIds });

    if (entitiesData.stats) {
      // Update stats in progress chart and filter panel.
      dispatch(updateStats(entitiesData.stats));

      /*
       * Update stats in the resource menu.
       *
       * TODO: Update stats for all affected resources. ATM that's not possbile,
       * since the backend only returns stats for the passed resource.
       */
      if (location.resource !== 'all-resources') {
        dispatch(
          updateResource(
            location.resource,
            entitiesData.stats.approved,
            entitiesData.stats.warnings,
          ),
        );
      }
    }

    // Update entity translation data now that it has changed on the server.
    for (let entity of entitiesData.entities) {
      entity.translation.forEach(function (
        translation: EntityTranslation,
        pluralForm: number,
      ) {
        dispatch(updateEntityTranslation(entity.pk, pluralForm, translation));

        if (entity.pk === selectedEntity) {
          dispatch(requestHistory(entity.pk, pluralForm));
          dispatch(getHistory(entity.pk, location.locale, pluralForm));
        }
      });
    }
  };

export const performAction =
  (
    location: LocationType,
    action: string,
    selectedEntity: number,
    entityIds: number[],
    find?: string,
    replace?: string,
  ) =>
  async (dispatch: AppDispatch) => {
    dispatch({ type: REQUEST_BATCHACTIONS, source: action });

    const data = await batchEditEntities(
      action,
      location.locale,
      entityIds,
      find,
      replace,
    );

    const response: ResponseType = {
      changedCount: 0,
      invalidCount: 0,
      error: false,
      action,
    };

    if ('count' in data) {
      response.changedCount = data.count;
      response.invalidCount = data.invalid_translation_count;

      if (data.count > 0) {
        dispatch(updateUI(location, selectedEntity, entityIds));
      }
    } else {
      response.error = true;
    }

    dispatch({ type: RECEIVE_BATCHACTIONS, response });

    setTimeout(() => {
      dispatch({ type: RESET_BATCHACTIONS_RESPONSE });
    }, 3000);
  };

export const resetSelection = (): ResetAction => ({ type: RESET_BATCHACTIONS });

export const selectAll =
  (location: LocationType) => async (dispatch: AppDispatch) => {
    dispatch({ type: REQUEST_BATCHACTIONS, source: 'select-all' });

    const entityIds = await fetchEntityIds(location);
    dispatch({ type: RECEIVE_BATCHACTIONS, response: undefined });
    dispatch(checkSelection(entityIds, entityIds[0]));
  };

export const toggleSelection = (entity: number): ToggleAction => ({
  type: TOGGLE_BATCHACTIONS,
  entity,
});

export const uncheckSelection = (
  entities: Array<number>,
  lastCheckedEntity: number,
): UncheckAction => ({
  type: UNCHECK_BATCHACTIONS,
  entities,
  lastCheckedEntity,
});
