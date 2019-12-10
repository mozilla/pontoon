/* @flow */

import * as React from 'react';

import type { MachineryState } from 'modules/machinery';


type Props = {|
    machinery: MachineryState,
|};


export default class Count extends React.Component<Props> {
    render() {
        const { machinery } = this.props;

        const machineryCount = machinery.translations.length;

        const preferredCount = machinery.translations.reduce((count, item) => {
            if (item.sources.find(source => source === 'translation-memory')) {
                return count + 1;
            }
            return count;
        }, 0);

        const remainingCount = machineryCount - preferredCount;

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
