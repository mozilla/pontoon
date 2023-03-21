import {
  Action,
  Resource,
  RECEIVE_RESOURCES,
  UPDATE_RESOURCE,
} from './actions';

// Name of this module.
// Used as the key to store this module's reducer.
export const RESOURCE = 'resource';

type ResourcesState = {
  readonly resources: Resource[];
  readonly allResources: Resource;
};

const updateResource = (
  { resources }: ResourcesState,
  resourcePath: string,
  approvedStrings: number,
  stringsWithWarnings: number,
): Resource[] =>
  resources.map((item) =>
    item.path === resourcePath
      ? { ...item, approvedStrings, stringsWithWarnings }
      : item,
  );

function updateAllResources(
  { allResources, resources }: ResourcesState,
  resourcePath: string,
  approvedStrings: number,
  stringsWithWarnings: number,
): Resource {
  const updatedResource = resources.find((item) => item.path === resourcePath);

  // That can happen in All Projects view
  if (!updatedResource) {
    return allResources;
  }

  const diffApproved = approvedStrings - updatedResource.approvedStrings;
  const diffWarnings =
    stringsWithWarnings - updatedResource.stringsWithWarnings;

  return {
    ...allResources,
    approvedStrings: allResources.approvedStrings + diffApproved,
    stringsWithWarnings: allResources.stringsWithWarnings + diffWarnings,
  };
}

const initial: ResourcesState = {
  resources: [],
  allResources: {
    path: 'all-resources',
    approvedStrings: 0,
    pretranslatedStrings: 0,
    stringsWithWarnings: 0,
    totalStrings: 0,
  },
};

export function reducer(
  state: ResourcesState = initial,
  action: Action,
): ResourcesState {
  switch (action.type) {
    case RECEIVE_RESOURCES:
      return {
        ...state,
        resources: action.resources,
        allResources: action.allResources,
      };
    case UPDATE_RESOURCE:
      return {
        ...state,
        resources: updateResource(
          state,
          action.resourcePath,
          action.approvedStrings,
          action.stringsWithWarnings,
        ),
        allResources: updateAllResources(
          state,
          action.resourcePath,
          action.approvedStrings,
          action.stringsWithWarnings,
        ),
      };
    default:
      return state;
  }
}
