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
 * Show the translation source from Microsoft Terminology.
 */
export default class MicrosoftTerminology extends React.Component<Props> {
    render() {
        const {source, index} = this.props;

        return <ul className="sources">
            <li key={ index }>
                <Localized
                    id= "machinery-MicrosoftTerminology--visit-microsoft"
                    attrs={{ title: true }}
                >
                    <a
                        className="translation-source"
                        href={ source.url }
                        title="'Visit Microsoft Terminology Service API.\n'+
                        '© 2018 Microsoft Corporation. All rights reserved.'"
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
                    >
                        <span>Microsoft</span>
                    </a>
                </Localized>
            </li>
        </ul>
    }
}
