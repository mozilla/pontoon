/* @flow */

import React from 'react';
import { Localized } from 'fluent-react';

import './Machinery.css';

import Translation from './Translation';

import type { Locale } from 'core/locales';
import type { MachineryState } from '..';


type Props = {|
    locale: ?Locale,
    machinery: MachineryState,
    updateEditorTranslation: (string) => void,
|};


/**
 * Show translations from machines.
 *
 * Shows a sorted list of translations for the same original string, or similar
 * strings, coming from various sources like Translation Memory or
 * third-party Machine Translation.
 */
export default class Machinery extends React.Component<Props> {
    render() {
        const { locale, machinery, updateEditorTranslation } = this.props;

        if (!locale) {
            return null;
        }

        return <section className="machinery">
            <div className="search-wrapper clearfix">
                <div className="icon fa fa-search"></div>
                <Localized id="machinery-machinery-search-placeholder" attrs={{ placeholder: true }}>
                    <input type="search" autoComplete="off" placeholder="Type to search machinery" />
                </Localized>
            </div>
            <ul>
                { machinery.translations.map((item, i) => {
                    return <Translation
                        translation={ item }
                        locale={ locale }
                        updateEditorTranslation={ updateEditorTranslation }
                        key={ i }
                    />;
                }) }
            </ul>
        </section>;
    }
}
