import { Localized } from '@fluent/react';
import React, {
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  useMemo,
} from 'react';

import { Location } from '~/context/Location';
import { ShowBadgeTooltip } from '~/context/BadgeTooltip';
import { useAppDispatch, useAppSelector } from '~/hooks';

import { performAction, resetSelection, selectAll } from '../actions';
import { BATCHACTIONS } from '../reducer';

import { ApproveAll } from './ApproveAll';
import './BatchActions.css';
import { RejectAll } from './RejectAll';
import { ReplaceAll } from './ReplaceAll';
import { CopyFromLocale } from './CopyFromLocale';
import { fetchAllLocales } from '~/api/other-locales';
import type { LocaleOption } from '~/api/other-locales';
import LocaleMenu from '~/modules/locale/components/LocaleMenu';
import { Locale } from '~/context/Locale';
import { Pretranslate } from './Pretranslate';

/**
 * Renders batch editor, used for performing mass actions on translations.
 */
export function BatchActions(): React.ReactElement<'div'> {
  const batchactions = useAppSelector((state) => state[BATCHACTIONS]);
  const location = useContext(Location);
  const showBadgeTooltip = useContext(ShowBadgeTooltip);
  const dispatch = useAppDispatch();

  const find = useRef<HTMLInputElement>(null);
  const replace = useRef<HTMLInputElement>(null);

  const [otherLocale, setOtherLocale] = useState('');
  const [locales, setLocales] = useState<LocaleOption[]>([]);

  const quitBatchActions = useCallback(() => dispatch(resetSelection()), []);
  const locale = useContext(Locale);

  useEffect(() => {
    const handleShortcuts = (ev: KeyboardEvent) => {
      if (ev.key === 'Escape') {
        quitBatchActions();
      }
    };

    document.addEventListener('keydown', handleShortcuts);
    return () => document.removeEventListener('keydown', handleShortcuts);
  }, []);

  useEffect(() => {
    fetchAllLocales().then((all) => {
      setLocales(all);
    });
  }, []);

  const selectAllEntities = useCallback(
    () => dispatch(selectAll(location)),
    [location],
  );

  const approveAll = useCallback(() => {
    if (!batchactions.requestInProgress) {
      dispatch(
        performAction(
          location,
          'approve',
          batchactions.entities,
          showBadgeTooltip,
        ),
      );
    }
  }, [location, batchactions]);

  const rejectAll = useCallback(() => {
    if (!batchactions.requestInProgress) {
      dispatch(
        performAction(
          location,
          'reject',
          batchactions.entities,
          showBadgeTooltip,
        ),
      );
    }
  }, [location, batchactions]);

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
            batchactions.entities,
            showBadgeTooltip,
            encodeURIComponent(fv),
            encodeURIComponent(rv),
          ),
        );
      }
    }
  }, [location, batchactions]);

  const pretranslate = useCallback(() => {
    if (!batchactions.requestInProgress) {
      dispatch(
        performAction(
          location,
          'pretranslate',
          batchactions.entities,
          showBadgeTooltip,
          undefined,
          undefined,
        ),
      );
    }
  }, [location, batchactions, showBadgeTooltip]);

  const canPretranslate = useMemo(() => {
    const root = document.getElementById('root');
    const isGoogleTranslateSupported =
      root?.dataset.isGoogleTranslateSupported === 'true';
    return isGoogleTranslateSupported && !!locale.googleTranslateCode;
  }, [locale.googleTranslateCode]);

  const copyFromLocale = useCallback(() => {
    if (!batchactions.requestInProgress) {
      dispatch(
        performAction(
          location,
          'copy_from_locale',
          batchactions.entities,
          showBadgeTooltip,
          undefined,
          undefined,
          otherLocale,
        ),
      );
    }
  }, [location, batchactions, showBadgeTooltip, otherLocale]);

  const submitReplaceForm = useCallback(
    (ev: React.SyntheticEvent<HTMLFormElement>) => {
      ev.preventDefault();
      replaceAll();
    },
    [replaceAll],
  );

  const submitCopyFromLocaleForm = useCallback(
    (ev: React.SyntheticEvent<HTMLFormElement>) => {
      ev.preventDefault();
      copyFromLocale();
    },
    [copyFromLocale],
  );

  const submitPretranslateForm = useCallback(
    (ev: React.SyntheticEvent<HTMLElement>) => {
      ev.preventDefault();
      pretranslate();
    },
    [pretranslate],
  );

  return (
    <div className='batch-actions'>
      <div className='topbar clearfix'>
        <Localized
          id='batchactions-BatchActions--header-select-all'
          attrs={{ title: true }}
          elems={{ glyph: <i className='fas fa-check fa-lg' /> }}
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
          <div className='selecting fas fa-sync fa-spin'></div>
        ) : (
          <Localized
            id='batchactions-BatchActions--header-selected-count'
            attrs={{ title: true }}
            elems={{
              glyph: <i className='fas fa-times fa-lg' />,
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
        <div className='copy-from-locale'>
          <Localized id='batchactions-BatchActions--copy-from-locale-heading'>
            <h2>COPY FROM ANOTHER LOCALE</h2>
          </Localized>
          <form id='copy-locale-form' onSubmit={submitCopyFromLocaleForm}>
            <LocaleMenu
              locales={locales}
              currentLocale={location.locale}
              selected={otherLocale}
              onSelect={setOtherLocale}
            />
            <CopyFromLocale
              copyFromLocale={copyFromLocale}
              batchactions={batchactions}
            />
          </form>
        </div>
        {canPretranslate && (
          <div className='pretranslate'>
            <Localized id='batchactions-BatchActions--pretranslate-heading'>
              <h2>PRETRANSLATE</h2>
            </Localized>
            <form id='pretranslate-form' onSubmit={submitPretranslateForm}>
              <Pretranslate
                pretranslate={pretranslate}
                batchactions={batchactions}
              />
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
