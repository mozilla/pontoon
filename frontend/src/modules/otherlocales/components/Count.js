/* @flow */

import * as React from 'react';

import type { LocalesState } from 'modules/otherlocales';


type Props = {|
    otherlocales: LocalesState,
    preferredCount: number,
|};


export default class Count extends React.Component<Props> {
    render() {
        const { otherlocales, preferredCount } = this.props;

        const otherlocalesCount = otherlocales.translations.length;

        const remainingCount = otherlocalesCount - preferredCount;

        const preferred = (
            !preferredCount ? null :
            <span className='preferred'>{ preferredCount }</span>
        );
        const remaining = (
            !remainingCount ? null :
            <span>{ remainingCount }</span>
        );
        const plus = (
            !remainingCount || !preferredCount ? null :
            <span>{ '+' }</span>
        );

        return <span className='count'>
            { preferred }
            { plus }
            { remaining }
        </span>;
    }
}
