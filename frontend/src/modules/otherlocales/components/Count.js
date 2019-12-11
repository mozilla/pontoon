/* @flow */

import * as React from 'react';

import type { LocalesState } from 'modules/otherlocales';


type Props = {|
    otherlocales: LocalesState,
|};


export default class Count extends React.Component<Props> {
    render() {
        const { otherlocales } = this.props;

        if (otherlocales.fetching) {
            return null;
        }

        if (!otherlocales.translations) {
            return null;
        }

        const otherlocalesCount = otherlocales.translations.other.length;
        const preferredLocalesCount = otherlocales.translations.preferred.length;

        if (!otherlocalesCount && !preferredLocalesCount) {
            return null;
        }

        const preferred = (
            !preferredLocalesCount ? null :
            <span className='preferred'>{ preferredLocalesCount }</span>
        );
        const other = (
            !otherlocalesCount ? null :
            <span>{ otherlocalesCount }</span>
        );
        const plus = (
            !otherlocalesCount || !preferredLocalesCount ? null :
            <span>{ '+' }</span>
        );

        return <span className='count'>
            { preferred }
            { plus }
            { other }
        </span>;
    }
}
