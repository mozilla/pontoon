/* @flow */

import * as React from 'react';

import './ResourcePercent.css';

import type { Resource } from '..';

type Props = {|
    resource: Resource,
|};

/**
 * Render a resource item percentage.
 */
export default function ResourcePercent(props: Props) {
    const {
        approvedStrings,
        stringsWithWarnings,
        totalStrings,
    } = props.resource;
    const completeStrings = approvedStrings + stringsWithWarnings;

    const percent = Math.floor((completeStrings / totalStrings) * 100) + '%';

    return <span className='percent'>{percent}</span>;
}
