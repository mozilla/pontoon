import React from 'react';

import './SkeletonLoader.css';

export function SkeletonLoader({
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
      className={`skeleton-loader entities ${firstLoad ? null : 'scroll'}`}
      ref={sentryRef}
    >
      {list.map((i) => {
        const classes = `entity missing ${
          i === 0 && firstLoad ? 'selected' : null
        }`;
        return (
          <li className={classes} key={i}>
            <span className='status fa' />
            <div>
              <p className='source-string'></p>
              <p className='text-2'></p>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
