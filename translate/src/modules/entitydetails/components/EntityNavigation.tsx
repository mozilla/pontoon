import { Localized } from '@fluent/react';
import React, { useEffect } from 'react';

import './EntityNavigation.css';

type Props = {
  copyLinkToClipboard: () => void;
  goToNextEntity: () => void;
  goToPreviousEntity: () => void;
};

/**
 * Component showing entity navigation toolbar.
 *
 * Shows copy link and next/previous buttons.
 */
export function EntityNavigation({
  copyLinkToClipboard,
  goToNextEntity,
  goToPreviousEntity,
}: Props): React.ReactElement {
  useEffect(() => {
    const handleShortcuts = (ev: KeyboardEvent) => {
      // On Alt + Up, move to the previous entity.
      if (ev.key === 'ArrowUp' && ev.altKey && !ev.ctrlKey && !ev.shiftKey) {
        ev.preventDefault();
        goToPreviousEntity();
      }

      // On Alt + Down, move to the next entity.
      if (ev.key === 'ArrowDown' && ev.altKey && !ev.ctrlKey && !ev.shiftKey) {
        ev.preventDefault();
        goToNextEntity();
      }
    };
    document.addEventListener('keydown', handleShortcuts);
    return () => document.removeEventListener('keydown', handleShortcuts);
  }, [goToNextEntity, goToPreviousEntity]);

  return (
    <div className='entity-navigation clearfix'>
      <Localized
        id='entitydetails-EntityNavigation--link'
        attrs={{ title: true }}
        elems={{ glyph: <i className='fa fa-link fa-lg' /> }}
      >
        <button
          className='link'
          title='Copy Link to String'
          onClick={copyLinkToClipboard}
        >
          {'<glyph></glyph>COPY LINK'}
        </button>
      </Localized>
      <Localized
        id='entitydetails-EntityNavigation--next'
        attrs={{ title: true }}
        elems={{
          glyph: <i className='fa fa-chevron-down fa-lg' />,
        }}
      >
        <button
          className='next'
          title='Go To Next String (Alt + Down)'
          onClick={goToNextEntity}
        >
          {'<glyph></glyph>NEXT'}
        </button>
      </Localized>
      <Localized
        id='entitydetails-EntityNavigation--previous'
        attrs={{ title: true }}
        elems={{ glyph: <i className='fa fa-chevron-up fa-lg' /> }}
      >
        <button
          className='previous'
          title='Go To Previous String (Alt + Up)'
          onClick={goToPreviousEntity}
        >
          {'<glyph></glyph>PREVIOUS'}
        </button>
      </Localized>
    </div>
  );
}
