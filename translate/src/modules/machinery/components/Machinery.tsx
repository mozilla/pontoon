import { useLocalization } from '@fluent/react';
import React, { useContext } from 'react';
import useInfiniteScroll from 'react-infinite-scroll-hook';
import { Entity } from '~/api/entity';
import { MachineryTranslations } from '~/context/MachineryTranslations';
import { SearchData } from '~/context/SearchData';

import { SkeletonLoader } from '~/core/loaders';

import './Machinery.css';
import { Translation } from './Translation';

type Props = {
  entity: Entity;
};

/**
 * Show translations from machines.
 *
 * Shows a sorted list of translations for the same original string, or similar
 * strings, coming from various sources like Translation Memory or
 * third-party Machine Translation.
 */
export function Machinery({ entity }: Props): React.ReactElement<'section'> {
  const { l10n } = useLocalization();
  const { source, translations } = useContext(MachineryTranslations);
  const { fetching, hasMore, input, query, results, setInput, getResults } =
    useContext(SearchData);

  const [sentryRef, { rootRef }] = useInfiniteScroll({
    loading: fetching,
    hasNextPage: hasMore,
    onLoadMore: getResults,
    rootMargin: '0px 0px 400px 0px',
  });

  const placeholder =
    query ||
    l10n.getString(
      'machinery-Machinery--search-placeholder',
      null,
      'Concordance Search',
    );

  return (
    <section className='machinery'>
      <div className='search-wrapper clearfix'>
        <label htmlFor='machinery-search'>
          {input && input !== query ? (
            <button className='fa fa-search' onClick={getResults}></button>
          ) : query ? (
            <button
              className='fa fa-times'
              onClick={() => {
                setInput('');
                getResults();
              }}
            ></button>
          ) : (
            <div className='fa fa-search'></div>
          )}
        </label>
        <form
          onSubmit={(ev) => {
            ev.preventDefault();
            getResults();
          }}
        >
          <input
            autoComplete='off'
            id='machinery-search'
            onChange={(ev) => setInput(ev.target.value)}
            placeholder={placeholder}
            type='search'
            value={input}
          />
        </form>
      </div>
      <div className='list-wrapper' ref={rootRef}>
        <ul>
          {translations.map((translation, index) => (
            <Translation
              index={index}
              entity={entity.pk}
              sourceString={source}
              translation={translation}
              key={index}
            />
          ))}
        </ul>
        <ul>
          {results.map((result, index) => (
            <Translation
              index={index + translations.length}
              entity={entity.pk}
              sourceString={query}
              translation={result}
              key={index + translations.length}
            />
          ))}
        </ul>
        {(fetching || hasMore) && (
          <SkeletonLoader items={results} sentryRef={sentryRef} />
        )}
      </div>
    </section>
  );
}
