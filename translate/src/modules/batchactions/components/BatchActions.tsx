import { Localized } from '@fluent/react';
import React, { useCallback, useContext, useEffect, useRef } from 'react';

import { Location } from '~/context/location';
import { useAppDispatch, useAppSelector } from '~/hooks';

import { performAction, resetSelection, selectAll } from '../actions';
import { NAME as BATCHACTIONS } from '../reducer';

import ApproveAll from './ApproveAll';
import './BatchActions.css';
import RejectAll from './RejectAll';
import ReplaceAll from './ReplaceAll';

/**
 * Renders batch editor, used for performing mass actions on translations.
 */
export function BatchActions(): React.ReactElement<'div'> {
  const batchactions = useAppSelector((state) => state[BATCHACTIONS]);
  const location = useContext(Location);
  const dispatch = useAppDispatch();

  const find = useRef<HTMLInputElement>(null);
  const replace = useRef<HTMLInputElement>(null);

  const quitBatchActions = useCallback(() => dispatch(resetSelection()), []);

  const { entity, locale, project, resource } = location;

  useEffect(() => {
    const handleShortcuts = (ev: KeyboardEvent) => {
      // On Esc, quit batch actions
      if (ev.keyCode === 27) {
        quitBatchActions();
      }
    };

    document.addEventListener('keydown', handleShortcuts);
    return () => document.removeEventListener('keydown', handleShortcuts);
  }, []);

  const selectAllEntities = useCallback(
    () => dispatch(selectAll(location)),
    [dispatch, location],
  );

  const approveAll = useCallback(() => {
    if (!batchactions.requestInProgress) {
      dispatch(
        performAction(location, 'approve', entity, batchactions.entities),
      );
    }
  }, [dispatch, entity, locale, project, resource, batchactions]);

  const rejectAll = useCallback(() => {
    if (!batchactions.requestInProgress) {
      dispatch(
        performAction(location, 'reject', entity, batchactions.entities),
      );
    }
  }, [dispatch, entity, locale, project, resource, batchactions]);

  const replaceAll = useCallback(() => {
    if (find.current && replace.current && !batchactions.requestInProgress) {
      const fv = find.current.value;
      const rv = replace.current.value;
      if (fv === '') {
        find.current.focus();
      } else if (fv === rv) {
        replace.current.focus();
      } else {
        dispatch(
          performAction(
            location,
            'replace',
            entity,
            batchactions.entities,
            encodeURIComponent(fv),
            encodeURIComponent(rv),
          ),
        );
      }
    }
  }, [dispatch, entity, locale, project, resource, batchactions]);

  const submitReplaceForm = useCallback(
    (ev: React.SyntheticEvent<HTMLFormElement>) => {
      ev.preventDefault();
      replaceAll();
    },
    [replaceAll],
  );

  return (
    <div className='batch-actions'>
      <div className='topbar clearfix'>
        <Localized
          id='batchactions-BatchActions--header-select-all'
          attrs={{ title: true }}
          elems={{ glyph: <i className='fa fa-check fa-lg' /> }}
        >
          <button
            className='select-all'
            title='Select All Strings (Ctrl + Shift + A)'
            onClick={selectAllEntities}
          >
            {'<glyph></glyph> SELECT ALL'}
          </button>
        </Localized>
        {batchactions.requestInProgress === 'select-all' ? (
          <div className='selecting fa fa-sync fa-spin'></div>
        ) : (
          <Localized
            id='batchactions-BatchActions--header-selected-count'
            attrs={{ title: true }}
            elems={{
              glyph: <i className='fa fa-times fa-lg' />,
              stress: <span className='stress' />,
            }}
            vars={{ count: batchactions.entities.length }}
          >
            <button
              className='selected-count'
              title='Quit Batch Editing (Esc)'
              onClick={quitBatchActions}
            >
              {'<glyph></glyph> <stress>{ $count }</stress> STRINGS SELECTED'}
            </button>
          </Localized>
        )}
      </div>

      <div className='actions-panel'>
        <div className='intro'>
          <Localized
            id='batchactions-BatchActions--warning'
            elems={{ stress: <span className='stress' /> }}
          >
            <p>
              {
                '<stress>Warning:</stress> These actions will be applied to all selected strings and cannot be undone.'
              }
            </p>
          </Localized>
        </div>

        <div className='review'>
          <Localized id='batchactions-BatchActions--review-heading'>
            <h2>REVIEW TRANSLATIONS</h2>
          </Localized>

          <ApproveAll approveAll={approveAll} batchactions={batchactions} />
          <RejectAll rejectAll={rejectAll} batchactions={batchactions} />
        </div>

        <div className='find-replace'>
          <Localized id='batchactions-BatchActions--find-replace-heading'>
            <h2>FIND & REPLACE IN TRANSLATIONS</h2>
          </Localized>

          <form onSubmit={submitReplaceForm}>
            <Localized
              id='batchactions-BatchActions--find'
              attrs={{ placeholder: true }}
            >
              <input
                className='find'
                type='search'
                autoComplete='off'
                placeholder='Find'
                ref={find}
              />
            </Localized>

            <Localized
              id='batchactions-BatchActions--replace-with'
              attrs={{ placeholder: true }}
            >
              <input
                className='replace'
                type='search'
                autoComplete='off'
                placeholder='Replace with'
                ref={replace}
              />
            </Localized>

            <ReplaceAll replaceAll={replaceAll} batchactions={batchactions} />
          </form>
        </div>
      </div>
    </div>
  );
}
