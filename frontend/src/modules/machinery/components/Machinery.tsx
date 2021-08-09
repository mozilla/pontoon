import * as React from 'react';
import { Localized } from '@fluent/react';

import './Machinery.css';

import Translation from './Translation';
import { SkeletonLoader } from 'core/loaders';

import type { Locale } from 'core/locale';
import type { MachineryState } from '..';

type Props = {
    locale: Locale | null | undefined;
    machinery: MachineryState;
    searchMachinery: (query: string, page?: number) => void;
};

type State = {
    page: number;
};

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

    submitForm: (event: React.SyntheticEvent<HTMLFormElement>) => void = (
        event: React.SyntheticEvent<HTMLFormElement>,
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

    render(): null | React.ReactElement<'section'> {
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
                    <ul>
                        {machinery.translations.map((translation, index) => {
                            return (
                                <Translation
                                    index={index}
                                    entity={machinery.entity}
                                    sourceString={machinery.sourceString}
                                    translation={translation}
                                    key={index}
                                />
                            );
                        })}
                    </ul>
                    <ul>
                        {machinery.searchResults.map((result, index) => {
                            return (
                                <Translation
                                    index={
                                        index + machinery.translations.length
                                    }
                                    entity={machinery.entity}
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
