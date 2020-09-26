/* @flow */

import React from 'react';
import { Localized } from '@fluent/react';

import './Machinery.css';

import Translation from './Translation';

import type { Locale } from 'core/locale';
import type { SourceType } from 'core/api';
import type { MachineryState } from '..';

type Props = {|
    isReadOnlyEditor: boolean,
    locale: ?Locale,
    machinery: MachineryState,
    updateEditorTranslation: (string, string) => void,
    updateMachinerySources: (Array<SourceType>, string) => void,
    searchMachinery: (string) => void,
|};

/**
 * Show translations from machines.
 *
 * Shows a sorted list of translations for the same original string, or similar
 * strings, coming from various sources like Translation Memory or
 * third-party Machine Translation.
 */
export default class Machinery extends React.Component<Props> {
    searchInput: { current: any };

    constructor(props: Props) {
        super(props);
        this.searchInput = React.createRef();
    }

    submitForm = (event: SyntheticKeyboardEvent<>) => {
        event.preventDefault();
        this.props.searchMachinery(this.searchInput.current.value);
    };

    render() {
        const {
            isReadOnlyEditor,
            locale,
            machinery,
            updateEditorTranslation,
            updateMachinerySources,
        } = this.props;

        if (!locale) {
            return null;
        }

        return (
            <section className='machinery'>
                <div className='search-wrapper clearfix'>
                    <label htmlFor='machinery-search'>
                        <div className='fa fa-search'></div>
                    </label>
                    <form onSubmit={this.submitForm}>
                        <Localized
                            id='machinery-Machinery--search-placeholder'
                            attrs={{ placeholder: true }}
                        >
                            <input
                                id='machinery-search'
                                type='search'
                                autoComplete='off'
                                placeholder='Search in Machinery'
                                ref={this.searchInput}
                            />
                        </Localized>
                    </form>
                </div>
                <ul>
                    {machinery.translations.map((translation, index) => {
                        return (
                            <Translation
                                sourceString={machinery.sourceString}
                                isReadOnlyEditor={isReadOnlyEditor}
                                locale={locale}
                                translation={translation}
                                updateEditorTranslation={
                                    updateEditorTranslation
                                }
                                updateMachinerySources={updateMachinerySources}
                                key={index}
                            />
                        );
                    })}
                </ul>
            </section>
        );
    }
}
