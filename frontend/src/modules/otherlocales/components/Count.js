/* @flow */

import * as React from 'react';

import type { LocalesState } from 'modules/otherlocales';


type Props = {|
    otherlocales: LocalesState,
|};


export default class Count extends React.Component<Props> {
    render() {
        const { otherlocales } = this.props;

        if (!otherlocales.translations) {
            return null;
        }

        const otherlocalesCount = otherlocales.translations.other.length;
        let preferredLocalesCount = otherlocales.translations.preferred.length;

        otherlocales.translations.preferred[0].locale.code === 'en-US' ?
            preferredLocalesCount -= 1 : preferredLocalesCount;

        const preferred = (
            !preferredLocalesCount ? null :
            <span className='preferred'>{ preferredLocalesCount }</span>
        );
        const other = (
            !otherlocalesCount ? null :
            <span>{ otherlocalesCount }</span>
        )
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
