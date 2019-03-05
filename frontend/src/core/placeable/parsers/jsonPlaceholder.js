/* @flow */

import * as React from 'react';


/**
 * Marks JSON format placeholders as user by the WebExtension API.
 *
 * Terms must start and end with a dollar sign "$" and contain only capital
 * letters or underscores.
 *
 * Example matches:
 *
 *   $USER$
 *   $FIRST_NAME$
 */
const jsonPlaceholder = {
    rule: /(\$[A-Z0-9_]+\$)/,
    tag: (x: string) => <mark className='placeable' title='JSON placeholder'>
        { x }
    </mark>,
};

export default jsonPlaceholder;
