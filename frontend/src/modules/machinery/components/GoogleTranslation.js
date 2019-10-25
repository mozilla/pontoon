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
 * Show the translation source from Google Translate.
 */
export default class GoogleTranslation extends React.Component<Props> {
    render() {
        const {source, index} = this.props;

        return <ul className="sources">
            <li key={ index }>
                <Localized
                    id= "machinery-GoogleTranslation--visit-google"
                    attrs={{ title: true }}
                >
                    <a
                        className="translation-source"
                        href={ source.url }
                        title="Visit Google Translate"
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
                    >
                        <span>Google Translate</span>
                    </a>
                </Localized>
            </li>
        </ul>
    }
}
