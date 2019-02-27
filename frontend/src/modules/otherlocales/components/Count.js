/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';

import { selectors } from '..';

import type { LocalesState } from 'modules/otherlocales';


type Props = {|
    otherlocales: LocalesState,
    preferredCount: number,
|};


export class CountBase extends React.Component<Props> {
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


const mapStateToProps = (state: Object): Props => {
    return {
        otherlocales: state.otherlocales,
        preferredCount: selectors.getPreferredLocalesCount(state),
    };
};

export default connect(mapStateToProps)(CountBase);
