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
    const { resource } = props;
    const percent = Math.floor(resource.approved_strings / resource.total_strings * 100) + '%';

    return <span className="percent">{ percent }</span>;
}
