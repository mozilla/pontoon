/* @flow */

import api from 'core/api';

import { actions as entitiesActions } from 'core/entities';
import { actions as resourceActions } from 'core/resource';
import { actions as statsActions } from 'core/stats';
import { actions as historyActions } from 'modules/history';

export const CHECK: 'batchactions/CHECK' = 'batchactions/CHECK';
export const RECEIVE: 'batchactions/RECEIVE' = 'batchactions/RECEIVE';
export const REQUEST: 'batchactions/REQUEST' = 'batchactions/REQUEST';
export const RESET: 'batchactions/RESET' = 'batchactions/RESET';
export const RESET_RESPONSE: 'batchactions/RESET_RESPONSE' =
    'batchactions/RESET_RESPONSE';
export const TOGGLE: 'batchactions/TOGGLE' = 'batchactions/TOGGLE';
export const UNCHECK: 'batchactions/UNCHECK' = 'batchactions/UNCHECK';

export type CheckAction = {|
    type: typeof CHECK,
    entities: Array<number>,
    lastCheckedEntity: number,
|};
export function checkSelection(
    entities: Array<number>,
    lastCheckedEntity: number,
): CheckAction {
    return {
        type: CHECK,
        entities,
        lastCheckedEntity,
    };
}

function updateUI(
    locale: string,
    project: string,
    resource: string,
    selectedEntity: number,
    entities: Array<number>,
): Function {
    return async (dispatch) => {
        const entitiesData = await api.entity.getEntities(
            locale,
            project,
            resource,
            entities,
            [],
        );

        if (entitiesData.stats) {
            // Update stats in progress chart and filter panel.
            dispatch(statsActions.update(entitiesData.stats));

            /*
             * Update stats in the resource menu.
             *
             * TODO: Update stats for all affected resources. ATM that's not possbile,
             * since the backend only returns stats for the passed resource.
             */
            if (resource !== 'all-resources') {
                dispatch(
                    resourceActions.update(
                        resource,
                        entitiesData.stats.approved,
                        entitiesData.stats.warnings,
                    ),
                );
            }
        }

        // Update entity translation data now that it has changed on the server.
        for (let entity of entitiesData.entities) {
            entity.translation.forEach(function (translation, pluralForm) {
                dispatch(
                    entitiesActions.updateEntityTranslation(
                        entity.pk,
                        pluralForm,
                        translation,
                    ),
                );

                if (entity.pk === selectedEntity) {
                    dispatch(historyActions.request(entity.pk, pluralForm));
                    dispatch(historyActions.get(entity.pk, locale, pluralForm));
                }
            });
        }
    };
}

export function performAction(
    action: string,
    locale: string,
    project: string,
    resource: string,
    selectedEntity: number,
    entities: Array<number>,
    find?: ?string,
    replace?: ?string,
): Function {
    return async (dispatch) => {
        dispatch(request(action));

        const data = await api.entity.batchEdit(
            action,
            locale,
            entities,
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
                dispatch(
                    updateUI(
                        locale,
                        project,
                        resource,
                        selectedEntity,
                        entities,
                    ),
                );
            }
        } else {
            response.error = true;
        }

        dispatch(receive(response));

        setTimeout(() => {
            dispatch(reset_response());
        }, 3000);
    };
}

export type ResponseType = {
    action: string,
    changedCount: ?number,
    invalidCount: ?number,
    error: ?boolean,
};

export type ReceiveAction = {|
    type: typeof RECEIVE,
    response: ?ResponseType,
|};
export function receive(response?: ?ResponseType): ReceiveAction {
    return {
        type: RECEIVE,
        response,
    };
}

export type RequestAction = {|
    type: typeof REQUEST,
    source: string,
|};
export function request(source: string): RequestAction {
    return {
        type: REQUEST,
        source,
    };
}

export type ResetResponseAction = {|
    type: typeof RESET_RESPONSE,
|};
export function reset_response(): ResetResponseAction {
    return {
        type: RESET_RESPONSE,
    };
}

export type ResetAction = {|
    type: typeof RESET,
|};
export function resetSelection(): ResetAction {
    return {
        type: RESET,
    };
}

export function selectAll(
    locale: string,
    project: string,
    resource: string,
    search: ?string,
    status: ?string,
    extra: ?string,
    tag: ?string,
    author: ?string,
    time: ?string,
): Function {
    return async (dispatch) => {
        dispatch(request('select-all'));

        const content = await api.entity.getEntities(
            locale,
            project,
            resource,
            null,
            [],
            null,
            search,
            status,
            extra,
            tag,
            author,
            time,
            true,
        );

        const entities = content.entity_pks;

        dispatch(receive());
        dispatch(checkSelection(entities, entities[0]));
    };
}

export type ToggleAction = {|
    type: typeof TOGGLE,
    entity: number,
|};
export function toggleSelection(entity: number): ToggleAction {
    return {
        type: TOGGLE,
        entity,
    };
}

export type UncheckAction = {|
    type: typeof UNCHECK,
    entities: Array<number>,
    lastCheckedEntity: number,
|};
export function uncheckSelection(
    entities: Array<number>,
    lastCheckedEntity: number,
): UncheckAction {
    return {
        type: UNCHECK,
        entities,
        lastCheckedEntity,
    };
}

export default {
    checkSelection,
    performAction,
    resetSelection,
    selectAll,
    toggleSelection,
    uncheckSelection,
};
