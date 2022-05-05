import { LocationType } from '~/context/location';
import api, { EntityTranslation } from '~/core/api';

import { updateEntityTranslation } from '~/core/entities/actions';
import { updateResource } from '~/core/resource/actions';
import { updateStats } from '~/core/stats/actions';
import { actions as historyActions } from '~/modules/history';

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
  (
    { locale, project, resource }: LocationType,
    selectedEntity: number,
    entityIds: number[],
  ) =>
  async (dispatch: AppDispatch) => {
    const entitiesData = await api.entity.getEntities(
      { locale, project, resource },
      { entityIds },
    );

    if (entitiesData.stats) {
      // Update stats in progress chart and filter panel.
      dispatch(updateStats(entitiesData.stats));

      /*
       * Update stats in the resource menu.
       *
       * TODO: Update stats for all affected resources. ATM that's not possbile,
       * since the backend only returns stats for the passed resource.
       */
      if (resource !== 'all-resources') {
        dispatch(
          updateResource(
            resource,
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
          dispatch(historyActions.request(entity.pk, pluralForm));
          dispatch(historyActions.get(entity.pk, locale, pluralForm));
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

    const data = await api.entity.batchEdit(
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

    const content = await api.entity.getEntities(location, { pkOnly: true });

    const entityIds = content.entity_pks;

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
