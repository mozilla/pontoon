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
    const { approved_strings, strings_with_warnings, total_strings }  = props.resource;
    const complete_strings = approved_strings + strings_with_warnings;

    const percent = Math.floor(complete_strings / total_strings * 100) + '%';

    return <span className="percent">{ percent }</span>;
}
