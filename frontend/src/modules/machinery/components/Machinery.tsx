import * as React from 'react';
import { Localized } from '@fluent/react';

import './Machinery.css';

import { Translation } from './Translation';
import { SkeletonLoader } from 'core/loaders';
import { usePrevious } from 'hooks/usePrevious';

import type { Locale } from 'core/locale';
import type { MachineryState } from '..';

interface Props {
    locale: Locale | null | undefined;
    machinery: MachineryState;
    searchMachinery: (query: string, page?: number) => void;
}

/**
 * Show translations from machines.
 *
 * Shows a sorted list of translations for the same original string, or similar
 * strings, coming from various sources like Translation Memory or
 * third-party Machine Translation.
 */
export const Machinery = ({
    locale,
    machinery,
    searchMachinery,
}: Props): null | React.ReactElement<'section'> => {
    const [page, setPage] = React.useState(1);
    const searchInput = React.useRef<HTMLInputElement>();
    const prevEntity = usePrevious(machinery.entity);
    const prevPage = usePrevious(page);

    React.useEffect(() => {
        // Restore custom input in search field,
        // e.g. when switching from Locales tab back to Machinery
        if (machinery.searchString) {
            searchInput.current.value = machinery.searchString;
        }
    }, []);

    React.useEffect(() => {
        // Clear search field after switching to a different entity
        if (!machinery.searchString && machinery.entity !== prevEntity) {
            searchInput.current.value = '';
            setPage(1);
        }
    }, [machinery.entity]);

    React.useEffect(() => {
        // Fetch next page of search results
        if (prevPage && page !== prevPage) {
            searchMachinery(searchInput.current.value, page);
        }
    }, [page]);

    const handleResetSearch = () => {
        searchMachinery('');
        setPage(1);
    };

    const submitForm = (event: React.SyntheticEvent<HTMLFormElement>) => {
        event.preventDefault();
        searchMachinery(searchInput.current.value);
    };

    const getMoreResults = () => {
       setPage(page + 1);
    };

    if (!locale) {
        return null;
    }

    const entity = machinery.searchString ? null : machinery.entity;
    const sourceString = machinery.searchString || machinery.sourceString;

    return (
        <section className='machinery'>
            <div className='search-wrapper clearfix'>
                <label htmlFor='machinery-search'>
                    {machinery.searchString ? (
                        <button
                            className='fa fa-times'
                            onClick={handleResetSearch}
                        ></button>
                    ) : (
                        <div className='fa fa-search'></div>
                    )}
                </label>
                <form onSubmit={submitForm}>
                    <Localized
                        id='machinery-Machinery--search-placeholder'
                        attrs={{ placeholder: true }}
                    >
                        <input
                            id='machinery-search'
                            type='search'
                            autoComplete='off'
                            placeholder='Concordance Search'
                            ref={searchInput}
                        />
                    </Localized>
                </form>
            </div>
            <div className='list-wrapper'>
                <ul>
                    {machinery.translations.map((translation, index) => (
                        <Translation
                            index={index}
                            entity={entity}
                            sourceString={sourceString}
                            translation={translation}
                            key={index}
                        />
                    ))}
                </ul>
                <ul>
                    {machinery.searchResults.map((result, index) => (
                        <Translation
                            index={index + machinery.translations.length}
                            entity={entity}
                            sourceString={sourceString}
                            translation={result}
                            key={index + machinery.translations.length}
                        />
                    ))}
                </ul>
                {machinery.hasMore && (
                    <div className='load-more-container'>
                        <Localized id='machinery-Machinery--load-more'>
                            <button
                                className='load-more-button'
                                onClick={getMoreResults}
                            >
                                LOAD MORE
                            </button>
                        </Localized>
                    </div>
                )}
                {machinery.fetching && (
                    <SkeletonLoader key={0} items={machinery.searchResults} />
                )}
            </div>
        </section>
    );
};
