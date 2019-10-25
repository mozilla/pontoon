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
 * Show the translation source from Caighdean Machine Translation.
 */
export default class CaighdeanTranslation extends React.Component<Props> {
    render() {
        const {source, index} = this.props;

        return <ul className="sources">
            <li key={ index }>
                <Localized
                    id= "machinery-CaighdeanTranslation--visit-caighdean"
                    attrs={{ title: true }}
                >
                    <a
                        className="translation-source"
                        href={ source.url }
                        title="Visit Caighdean Machine Translation"
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
                    >
                        <span>Caighdean</span>
                    </a>
                </Localized>
            </li>
        </ul>
    }
}
