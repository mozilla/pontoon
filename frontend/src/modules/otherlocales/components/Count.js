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

<<<<<<< HEAD
        const otherlocalesCount = otherlocales.translations.other.length;
        const preferredLocalesCount = otherlocales.translations.preferred.length;
=======
        const preferredLocalesCount = otherlocales.translations.preferred.length
        const otherlocalesCount = otherlocales.translations.other.length;
>>>>>>> Refactored for user authenticated and refactored count

        const preferred = (
            !preferredLocalesCount ? null :
            <span className='preferred'>{ preferredLocalesCount }</span>
        );
<<<<<<< HEAD
        const other = (
            !otherlocalesCount ? null :
            <span>{ otherlocalesCount }</span>
        );
=======
>>>>>>> Refactored for user authenticated and refactored count
        const plus = (
            !otherlocalesCount || !preferredLocalesCount ? null :
            <span>{ '+' }</span>
        );

        return <span className='count'>
            { preferred }
            { plus }
<<<<<<< HEAD
            { other }
=======
            { otherlocalesCount }
>>>>>>> Refactored for user authenticated and refactored count
        </span>;
    }
}
