import * as React from 'react';
import { Localized } from '@fluent/react';
import useInfiniteScroll from 'react-infinite-scroll-hook';

import './Machinery.css';

import { Translation } from './Translation';
import { SkeletonLoader } from '~/core/loaders';
import { usePrevious } from '~/hooks/usePrevious';

import type { Locale } from '~/core/locale';
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
  const searchInput = React.useRef<HTMLInputElement>(null);
  const prevEntity = usePrevious(machinery.entity);
  const prevPage = usePrevious(page);

  React.useEffect(() => {
    // Restore custom input in search field,
    // e.g. when switching from Locales tab back to Machinery
    if (searchInput.current && machinery.searchString) {
      searchInput.current.value = machinery.searchString;
    }
  }, []);

  React.useEffect(() => {
    // Clear search field after switching to a different entity
    if (
      searchInput.current &&
      !machinery.searchString &&
      machinery.entity !== prevEntity
    ) {
      searchInput.current.value = '';
      setPage(1);
    }
  }, [machinery.entity]);

  React.useEffect(() => {
    // Fetch next page of search results
    if (searchInput.current && prevPage && page !== prevPage) {
      searchMachinery(searchInput.current.value, page);
    }
  }, [page, searchMachinery]);

  const [sentryRef, { rootRef }] = useInfiniteScroll({
    loading: machinery.fetching,
    hasNextPage: machinery.hasMore ?? false,
    onLoadMore: () => setPage((page) => page + 1),
    rootMargin: '0px 0px 400px 0px',
  });

  const resetSearch = () => {
    searchMachinery('');
    if (searchInput.current) searchInput.current.value = '';
    setPage(1);
  };

  const submitForm = (event: React.SyntheticEvent<HTMLFormElement>) => {
    event.preventDefault();
    setPage(1);
    if (searchInput.current) searchMachinery(searchInput.current.value);
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
            <button className='fa fa-times' onClick={resetSearch}></button>
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
      <div className='list-wrapper' ref={rootRef}>
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
        {(machinery.fetching || machinery.hasMore) && (
          <div ref={sentryRef}>
            <SkeletonLoader key={0} items={machinery.searchResults} />
          </div>
        )}
      </div>
    </section>
  );
};
