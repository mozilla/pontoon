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
 * Show the translation source from Microsoft Translation.
 */
export default class MicrosoftTranslation extends React.Component<Props> {
    render() {
        const {source, index} = this.props;

        return <ul className="sources">
            <li key={ index }>
                <Localized
                    id= "machinery-MicrosoftTranslation--visit-bing"
                    attrs={{ title: true }}
                >
                    <a
                        className="translation-source"
                        href={ source.url }
                        title="Visit Bing Translate"
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
                    >
                        <span>Microsoft Translator</span>
                    </a>
                </Localized>
            </li>
        </ul>
    }
}
