import React from 'react';

import './MachinerySkeletonLoader.css';

export function MachinerySkeletonLoader({
  sentryRef,
  items,
}: {
  sentryRef?: React.Ref<HTMLUListElement>;
  items: unknown[];
}) {
  const firstLoad = items.length === 0;
  const itemCount = firstLoad ? 30 : 2;
  const list = Array.from(Array(itemCount).keys());

  return (
    <ul
      className={`machinery-skeleton-loader ${firstLoad ? null : 'scroll'}`}
      data-testid='machinery-skeleton-loader'
      ref={sentryRef}
    >
      {list.map((i) => (
        <li className='machinery-item-skeleton' key={i}>
          <header>
            <span className='skeleton-bar' />
          </header>
          <p className='original' />
          <p className='suggestion' />
        </li>
      ))}
    </ul>
  );
}
