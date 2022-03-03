import { push, replace } from 'connected-react-router';

import type { AppDispatch } from '~/store';

/**
 * Update the URL with a set of new parameters.
 *
 * This function removes the `string` parameter from the URL if any, because
 * it is possible that after the results have changed, the currently selected
 * entity won't be available anymore.
 * It keeps all other unaffected parameters in the URL the same.
 *
 * @param {Object} router The router data object from connected-react-router.
 * @param {Object} params A list of parameters to update in the current URL.
 * @param {boolean} replaceHistory Whether or not to push a new URL or replace the current one in the browser history.
 */
export function update(
  router: Record<string, any>,
  params: Record<string, string | null | undefined>,
  replaceHistory?: boolean,
) {
  return (dispatch: AppDispatch) => {
    const queryString = router.location.search;
    const currentParams = new URLSearchParams(queryString);

    Object.keys(params).forEach((param: string) => {
      const prev = currentParams.get(param);
      const value = params[param];

      if (value === prev || (!value && !prev)) {
        return;
      }

      if (!value) {
        currentParams.delete(param);
      } else {
        currentParams.set(param, value);
      }
    });

    // If the URL did not change, don't do anything.
    if (queryString === '?' + currentParams.toString()) {
      return;
    }

    // When we change the URL, we want to remove the `string` parameter
    // because with the new results, that entity might not be available
    // anymore.
    if (!params['string']) {
      currentParams.delete('string');
    }

    let updateMethod = push;
    if (replaceHistory) {
      updateMethod = replace;
    }

    dispatch(updateMethod('?' + currentParams.toString()));
  };
}

/**
 * Update the URL with a new `string` parameter.
 *
 * This function keeps all other parameters in the URL the same.
 */
export function updateEntity(
  router: Record<string, any>,
  entity: string,
  replaceHistory?: boolean,
) {
  return update(router, { string: entity }, replaceHistory);
}

export default {
  update,
  updateEntity,
};
