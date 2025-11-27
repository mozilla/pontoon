import { Localized } from '@fluent/react';
import React, { useCallback, useContext, useEffect } from 'react';

import { EntitiesList } from '~/context/EntitiesList';
import { EntityView } from '~/context/EntityView';
import { Location } from '~/context/Location';
import { ShowNotification } from '~/context/Notification';
import { UnsavedActions } from '~/context/UnsavedChanges';
import { useAppSelector } from '~/hooks';
import { ENTITIES } from '~/modules/entities/reducer';
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
  const entities = useAppSelector((state) => state[ENTITIES].entities);
  const { entity } = useContext(EntityView);
  const { checkUnsavedChanges } = useContext(UnsavedActions);
  const entitiesList = useContext(EntitiesList);

  let nextEntityId = 0;
  let prevEntityId = 0;

  const entityIdx = entities.indexOf(entity);
  if (entityIdx !== -1 && entities.length >= 2) {
    const next = (entityIdx + 1) % entities.length;
    nextEntityId = entities[next].pk;
    const prev = (entityIdx - 1 + entities.length) % entities.length;
    prevEntityId = entities[prev].pk;
  }

  const goToStringList = () => {
    entitiesList.show(true);
  };

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

  const goToNextEntity = useCallback(() => {
    if (nextEntityId) {
      checkUnsavedChanges(() => location.push({ entity: nextEntityId }));
    }
  }, [location, nextEntityId]);

  const goToPreviousEntity = useCallback(() => {
    if (prevEntityId) {
      checkUnsavedChanges(() => location.push({ entity: prevEntityId }));
    }
  }, [location, prevEntityId]);

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

  return entity.obsolete ? (
    <div className='entity-obsolete clearfix'>
      <Localized id='entitydetails-obsolete'>
        <span>Obsolete entity</span>
      </Localized>
    </div>
  ) : (
    <div className='entity-navigation clearfix'>
      <Localized
        id='entitydetails-EntityNavigation--string-list'
        attrs={{ title: true }}
        elems={{ glyph: <i className='fas fa-chevron-left fa-lg' /> }}
      >
        <button
          className='string-list'
          title='Go to String List'
          onClick={goToStringList}
        >
          {'<glyph></glyph>STRINGS'}
        </button>
      </Localized>
      <Localized
        id='entitydetails-EntityNavigation--link'
        attrs={{ title: true }}
        elems={{ glyph: <i className='fas fa-link fa-lg' /> }}
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
          glyph: <i className='fas fa-chevron-down fa-lg' />,
        }}
      >
        <button
          className='next'
          disabled={!nextEntityId}
          title='Go To Next String (Alt + Down)'
          onClick={goToNextEntity}
        >
          {'<glyph></glyph>NEXT'}
        </button>
      </Localized>
      <Localized
        id='entitydetails-EntityNavigation--previous'
        attrs={{ title: true }}
        elems={{ glyph: <i className='fas fa-chevron-up fa-lg' /> }}
      >
        <button
          className='previous'
          disabled={!prevEntityId}
          title='Go To Previous String (Alt + Up)'
          onClick={goToPreviousEntity}
        >
          {'<glyph></glyph>PREVIOUS'}
        </button>
      </Localized>
    </div>
  );
}
