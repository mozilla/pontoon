import { Localized } from '@fluent/react';
import React, { useCallback, useState } from 'react';
import { Link } from '~/context/Location';
import { Stats, useStats } from '~/modules/stats';
import { asLocaleString, useOnDiscard } from '~/utils';
import { ProgressChart } from './ProgressChart';
import './ResourceProgress.css';

type Props = {
  percent: number;
  stats: Stats;
  onDiscard: () => void;
};

function ResourceProgressDialog({ percent, stats, onDiscard }: Props) {
  const {
    approved,
    pretranslated,
    warnings,
    errors,
    missing,
    unreviewed,
    total,
  } = stats;

  const ref = React.useRef<HTMLElement>(null);
  useOnDiscard(ref, onDiscard);

  return (
    <aside ref={ref} className='menu'>
      <div className='main'>
        <header>
          <h2>
            <Localized id='resourceprogress-ResourceProgress--all-strings'>
              ALL STRINGS
            </Localized>
            <span className='value'>{asLocaleString(total)}</span>
          </h2>
          <h2 className='small'>
            <Localized id='resourceprogress-ResourceProgress--unreviewed'>
              UNREVIEWED
            </Localized>
            <span className='value'>{asLocaleString(unreviewed)}</span>
          </h2>
        </header>
        <ProgressChart stats={stats} size={220} />
        <span className='percent'>{percent}</span>
      </div>
      <div className='details'>
        <div className='approved'>
          <span className='title'>
            <Localized id='resourceprogress-ResourceProgress--translated'>
              TRANSLATED
            </Localized>
          </span>
          <p className='value' onClick={onDiscard}>
            <Link to={{ status: 'translated' }}>
              {asLocaleString(approved)}
            </Link>
          </p>
        </div>
        <div className='pretranslated'>
          <span className='title'>
            <Localized id='resourceprogress-ResourceProgress--pretranslated'>
              PRETRANSLATED
            </Localized>
          </span>
          <p className='value' onClick={onDiscard}>
            <Link to={{ status: 'pretranslated' }}>
              {asLocaleString(pretranslated)}
            </Link>
          </p>
        </div>
        <div className='warnings'>
          <span className='title'>
            <Localized id='resourceprogress-ResourceProgress--warnings'>
              WARNINGS
            </Localized>
          </span>
          <p className='value' onClick={onDiscard}>
            <Link to={{ status: 'warnings' }}>{asLocaleString(warnings)}</Link>
          </p>
        </div>
        <div className='errors'>
          <span className='title'>
            <Localized id='resourceprogress-ResourceProgress--errors'>
              ERRORS
            </Localized>
          </span>
          <p className='value' onClick={onDiscard}>
            <Link to={{ status: 'errors' }}>{asLocaleString(errors)}</Link>
          </p>
        </div>
        <div className='missing'>
          <span className='title'>
            <Localized id='resourceprogress-ResourceProgress--missing'>
              MISSING
            </Localized>
          </span>
          <p className='value' onClick={onDiscard}>
            <Link to={{ status: 'missing' }}>{asLocaleString(missing)}</Link>
          </p>
        </div>
      </div>
    </aside>
  );
}

/**
 * Show a panel with progress chart and stats for the current resource.
 */
export function ResourceProgress(): React.ReactElement<'div'> | null {
  const stats = useStats();
  const [visible, setVisible] = useState(false);
  const toggleVisible = useCallback(() => setVisible((prev) => !prev), []);
  const handleDiscard = useCallback(() => setVisible(false), []);

  // Do not show resource progress until stats are available
  if (!stats.total) {
    return null;
  }

  const complete = stats.approved + stats.pretranslated + stats.warnings;
  const percent = Math.floor((complete / stats.total) * 100);

  return (
    <div className='progress-chart'>
      <div className='selector' onClick={toggleVisible}>
        <ProgressChart stats={stats} size={44} />
        <span className='percent unselectable'>{percent}</span>
      </div>
      {visible ? (
        <ResourceProgressDialog
          percent={percent}
          stats={stats}
          onDiscard={handleDiscard}
        />
      ) : null}
    </div>
  );
}
