/* @flow */

import React from 'react';
import { Localized } from '@fluent/react';


type Props = {|
    source: {
        type: string,
        url: string,
    },
    index: number
|};


/**
 * Show the translation source from Transvision.
 */
export default class TransvisionMemory extends React.Component<Props> {
    render() {
        const {source, index} = this.props;

        return <ul className="sources">
            <li key={ index }>
                <Localized
                    id= "machinery-TransvisionMemory--visit-transvision"
                    attrs={{ title: true }}
                >
                    <a
                        className="translation-source"
                        href={ source.url }
                        title="Visit Transvision"
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
                    >
                        <span>Mozilla</span>
                    </a>
                </Localized>
            </li>
        </ul>
    }
}
