import { Localized } from '@fluent/react';
import React, { useCallback, useContext, useEffect } from 'react';

import { Location } from '~/context/Location';
import { ShowNotification } from '~/context/Notification';
import { UnsavedActions } from '~/context/UnsavedChanges';
import { useNextEntity, usePreviousEntity } from '~/modules/entities/hooks';
import { STRING_LINK_COPIED } from '~/modules/notification/messages';

import './EntityNavigation.css';

/**
 * Component showing entity navigation toolbar.
 *
 * Shows copy link and next/previous buttons.
 */
export function EntityNavigation(): React.ReactElement {
  const location = useContext(Location);
  const showNotification = useContext(ShowNotification);
  const nextEntity = useNextEntity();
  const previousEntity = usePreviousEntity();
  const { checkUnsavedChanges } = useContext(UnsavedActions);

  const copyLinkToClipboard = useCallback(async () => {
    const { locale, project, resource, entity } = location;

    const url = new URL(
      `/${locale}/${project}/${resource}/`,
      window.location.href,
    );
    url.searchParams.append('string', String(entity));
    await navigator.clipboard.writeText(String(url));

    showNotification(STRING_LINK_COPIED);
  }, [location]);

  const goToEntity = useCallback(
    (entity: number | undefined) => {
      if (entity) {
        checkUnsavedChanges(() => {
          location.push({ entity });
        });
      }
    },
    [location],
  );

  const goToNextEntity = useCallback(
    () => goToEntity(nextEntity?.pk),
    [goToEntity, nextEntity],
  );

  const goToPreviousEntity = useCallback(
    () => goToEntity(previousEntity?.pk),
    [goToEntity, previousEntity],
  );

  useEffect(() => {
    function handleShortcuts(ev: KeyboardEvent) {
      if (ev.altKey && !ev.ctrlKey && !ev.shiftKey) {
        switch (ev.key) {
          // On Alt + Up, move to the previous entity.
          case 'ArrowUp':
            ev.preventDefault();
            goToPreviousEntity();
            break;

          // On Alt + Down, move to the next entity.
          case 'ArrowDown':
            ev.preventDefault();
            goToNextEntity();
            break;
        }
      }
    }

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
          disabled={!nextEntity}
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
          disabled={!previousEntity}
          title='Go To Previous String (Alt + Up)'
          onClick={goToPreviousEntity}
        >
          {'<glyph></glyph>PREVIOUS'}
        </button>
      </Localized>
    </div>
  );
}
