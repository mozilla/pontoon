/* @flow */

import React from 'react';
import InfiniteScroll from 'react-infinite-scroller';
import { Localized } from '@fluent/react';

import './Machinery.css';

import Translation from './Translation';
import { SkeletonLoader } from 'core/loaders';

import type { Locale } from 'core/locale';
import type { MachineryState } from '..';

type Props = {|
    locale: ?Locale,
    machinery: MachineryState,
    searchMachinery: (string, ?number) => void,
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
        }
    }

    handleResetSearch = () => {
        this.props.searchMachinery('');
    };

    submitForm = (event: SyntheticKeyboardEvent<>) => {
        event.preventDefault();
        this.props.searchMachinery(this.searchInput.current.value);
    };

    getMoreResults = (page: number) => {
        const { machinery } = this.props;

        // Temporary fix for the infinite number of requests from InfiniteScroller
        // More info at:
        // * https://github.com/CassetteRocks/react-infinite-scroller/issues/149
        // * https://github.com/CassetteRocks/react-infinite-scroller/issues/163
        if (machinery.fetching) {
            return;
        }

        this.props.searchMachinery(this.searchInput.current.value, page);
    };

    render() {
        const { locale, machinery } = this.props;

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
                    <InfiniteScroll
                        pageStart={1}
                        loadMore={this.getMoreResults}
                        hasMore={hasMore}
                        loader={
                            <SkeletonLoader
                                key={0}
                                items={machinery.translations}
                            />
                        }
                        useWindow={false}
                        threshold={300}
                    >
                        <ul>
                            {machinery.translations.map(
                                (translation, index) => {
                                    return (
                                        <Translation
                                            index={index}
                                            sourceString={
                                                machinery.sourceString
                                            }
                                            translation={translation}
                                            key={index}
                                        />
                                    );
                                },
                            )}
                        </ul>
                    </InfiniteScroll>
                </div>
            </section>
        );
    }
}
