/* @flow */

import * as React from 'react';

import type { LocalesState } from 'modules/otherlocales';


type Props = {|
    otherlocales: LocalesState,
    preferredLocalesCount: number,
|};


export default class Count extends React.Component<Props> {
    render() {
        const { otherlocales, preferredLocalesCount } = this.props;

        const otherlocalesCount = 3 //otherlocales.translations.other.length;

        const remainingCount = otherlocalesCount - preferredLocalesCount;

        const preferred = (
            !preferredLocalesCount ? null :
            <span className='preferred'>{ preferredLocalesCount }</span>
        );
        const remaining = (
            !remainingCount ? null :
            <span>{ remainingCount }</span>
        );
        const plus = (
            !remainingCount || !preferredLocalesCount ? null :
            <span>{ '+' }</span>
        );

        return <span className='count'>
            { preferred }
            { plus }
            { remaining }
        </span>;
    }
}
