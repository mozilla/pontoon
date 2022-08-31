import React from 'react';

import { getCSRFToken } from '~/api/utils/csrfToken';

/*
 * Render element with CSRF token needed in POST forms.
 */
export function CSRFToken(): React.ReactElement<'input'> {
  return (
    <input name='csrfmiddlewaretoken' type='hidden' value={getCSRFToken()} />
  );
}
