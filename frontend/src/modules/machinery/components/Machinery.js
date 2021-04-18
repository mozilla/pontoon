/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './Machinery.css';

import Translation from './Translation';
import { SkeletonLoader } from 'core/loaders';
import * as utils from 'core/utils';

import type { Locale } from 'core/locale';
import type { Entity } from 'core/api';
import type { MachineryState } from '..';

type Props = {|
    locale: ?Locale,
    machinery: MachineryState,
    searchMachinery: (string, ?number) => void,
    entity: Entity,
|};

type State = {|
    page: number,
|};

/**
 * Show translations from machines.
 *
 * Shows a sorted list of translations for the same original string, or similar
 * strings, coming from various sources like Translation Memory or
 * third-party Machine Translation.
 */
export default class Machinery extends React.Component<Props, State> {
    searchInput: { current: any };

    constructor(props: Props) {
        super(props);
        this.searchInput = React.createRef();
        this.state = { page: 1 };
    }

    componentDidMount() {
        const { machinery } = this.props;

        // Restore custom input in search field,
        // e.g. when switching from Locales tab back to Machinery
        if (!machinery.entity && machinery.sourceString) {
            this.searchInput.current.value = machinery.sourceString;
        }
    }

    componentDidUpdate(prevProps: Props) {
        const { machinery } = this.props;

        // Clear search field after switching to a different entity
        if (machinery.entity && !prevProps.machinery.entity) {
            this.searchInput.current.value = '';
            this.setState({ page: 1 });
        }
    }

    handleResetSearch: () => void = () => {
        this.props.searchMachinery('');
        this.setState({ page: 1 });
    };

    submitForm: (event: SyntheticKeyboardEvent<>) => void = (
        event: SyntheticKeyboardEvent<>,
    ) => {
        event.preventDefault();
        this.props.searchMachinery(this.searchInput.current.value);
    };

    getMoreResults: () => void = () => {
        this.setState(
            (state) => ({ page: state.page + 1 }),
            () =>
                this.props.searchMachinery(
                    this.searchInput.current.value,
                    this.state.page,
                ),
        );
    };

    render(): null | React.Element<'section'> {
        const { locale, machinery, entity } = this.props;

        const source = utils.getOptimizedContent(
            entity.machinery_original,
            entity.format,
        );

        if (!locale) {
            return null;
        }

        const showResetButton = !machinery.entity && machinery.sourceString;

        const hasMore = machinery.hasMore;

        return (
            <section className='machinery'>
                <div className='search-wrapper clearfix'>
                    <label htmlFor='machinery-search'>
                        {showResetButton ? (
                            <button
                                className='fa fa-times'
                                onClick={this.handleResetSearch}
                            ></button>
                        ) : (
                            <div className='fa fa-search'></div>
                        )}
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
                                placeholder='Concordance Search'
                                ref={this.searchInput}
                            />
                        </Localized>
                    </form>
                </div>
                <div className='list-wrapper'>
                    <ul>
                        {machinery.translations.map((translation, index) => {
                            return !machinery.entity ||
                                translation.original == source ? (
                                <Translation
                                    index={index}
                                    sourceString={machinery.sourceString}
                                    translation={translation}
                                    key={index}
                                />
                            ) : null;
                        })}
                    </ul>
                    <ul>
                        {machinery.searchResults.map((result, index) => {
                            return (
                                <Translation
                                    index={
                                        index + machinery.translations.length
                                    }
                                    sourceString={machinery.sourceString}
                                    translation={result}
                                    key={index + machinery.translations.length}
                                />
                            );
                        })}
                    </ul>
                    {hasMore && (
                        <div className='load-more-container'>
                            <Localized id='machinery-Machinery--load-more'>
                                <button
                                    className='load-more-button'
                                    onClick={this.getMoreResults}
                                >
                                    LOAD MORE
                                </button>
                            </Localized>
                        </div>
                    )}
                    {machinery.fetching && (
                        <SkeletonLoader
                            key={0}
                            items={machinery.searchResults}
                        />
                    )}
                </div>
            </section>
        );
    }
}
