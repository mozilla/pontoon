import React from 'react';

import './error-list.css';

export function ErrorList({ errors }) {
  const entries = Object.entries(errors);
  return entries.length === 0 ? null : (
    <ul className='errors'>
      {entries.map(([name, error], index) => (
        <li className='error' key={index}>
          {name}: {error}
        </li>
      ))}
    </ul>
  );
}
