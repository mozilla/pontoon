import { fetchAllResources } from '~/api/resource';
import type { AppDispatch } from '~/store';

export const RECEIVE_RESOURCES = 'resource/RECEIVE';
export const UPDATE_RESOURCE = 'resource/UPDATE';

export type Resource = {
  readonly path: string;
  readonly approvedStrings: number;
  readonly pretranslatedStrings: number;
  readonly stringsWithWarnings: number;
  readonly totalStrings: number;
};

type UpdateAction = {
  type: typeof UPDATE_RESOURCE;
  resourcePath: string;
  approvedStrings: number;
  pretranslatedStrings: number;
  stringsWithWarnings: number;
};

type ReceiveAction = {
  type: typeof RECEIVE_RESOURCES;
  resources: Array<Resource>;
  allResources: Resource;
};

export type Action = ReceiveAction | UpdateAction;

export const getResource =
  (locale: string, project: string) => async (dispatch: AppDispatch) => {
    const results = await fetchAllResources(locale, project);

    const resources = results.map((resource) => ({
      path: resource.title,
      approvedStrings: resource.approved_strings,
      pretranslatedStrings: resource.pretranslated_strings,
      stringsWithWarnings: resource.strings_with_warnings,
      totalStrings: resource.resource__total_strings,
    }));

    const allResources = resources.pop();
    dispatch({ type: RECEIVE_RESOURCES, resources, allResources });
  };

export const updateResource = (
  resourcePath: string,
  approvedStrings: number,
  pretranslatedStrings: number,
  stringsWithWarnings: number,
): UpdateAction => ({
  type: UPDATE_RESOURCE,
  resourcePath,
  approvedStrings,
  pretranslatedStrings,
  stringsWithWarnings,
});
