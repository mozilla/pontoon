/* @flow */

import * as React from 'react';

import type { LocalesState } from 'modules/otherlocales';


type Props = {|
    otherlocales: LocalesState,
|};


export default class Count extends React.Component<Props> {
    render() {
<<<<<<< HEAD
        const { otherlocales } = this.props;

        if (!otherlocales.translations) {
            return null;
        }
=======
        const { /*otherlocales,*/ preferredLocalesCount } = this.props;

        const otherlocalesCount = 2 //otherlocales.translations.other.length;
>>>>>>> Initial progress to refactor frontend

        const otherlocalesCount = otherlocales.translations.other.length;
        const preferredLocalesCount = otherlocales.translations.preferred.length;

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
