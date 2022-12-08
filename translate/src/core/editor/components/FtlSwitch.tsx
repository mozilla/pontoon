import { Localized } from '@fluent/react';
import classNames from 'classnames';
import React, { useCallback, useContext, useMemo } from 'react';

import { EditorActions, EditorData } from '~/context/Editor';
import { ShowNotification } from '~/context/Notification';
import { FTL_NOT_SUPPORTED_RICH_EDITOR } from '~/core/notification/messages';
import { USER } from '~/core/user';
import { getSyntaxType, parseEntry } from '~/utils/fluent';
import { useAppSelector } from '~/hooks';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';

import './FtlSwitch.css';

/**
 * Show a button to allow switching to the source editor,
 * but only if the user is logged in and the string is not read-only.
 * When the syntax is complex, the editor is blocked in source mode,
 * and it becomes impossible to switch to a different editor type.
 * Thus we show a notification to the user if they try to use the
 * "FTL" switch button.
 */
export function FtlSwitch() {
  const showNotification = useContext(ShowNotification);
  const readonly = useReadonlyEditor();
  const isAuthenticated = useAppSelector(
    (state) => state[USER].isAuthenticated,
  );
  const { toggleFtlView } = useContext(EditorActions);
  const { format, value, view } = useContext(EditorData);

  const canToggle = useMemo(() => {
    if (view === 'source' && typeof value === 'string') {
      const entry = parseEntry(value);
      return getSyntaxType(entry) !== 'complex';
    } else {
      return true;
    }
  }, [value, view]);

  const handleClick = useCallback(() => {
    if (canToggle) {
      toggleFtlView();
    } else {
      showNotification(FTL_NOT_SUPPORTED_RICH_EDITOR);
    }
  }, [canToggle, toggleFtlView]);

  if (format !== 'ftl' || !isAuthenticated || readonly) {
    return null;
  }

  const cn = classNames('ftl', view === 'source' && 'active');
  const id = canToggle
    ? 'editor-FtlSwitch--toggle'
    : 'editor-FtlSwitch--active';
  return (
    <Localized id={id} attrs={{ title: true }}>
      <button className={cn} onClick={handleClick}>
        FTL
      </button>
    </Localized>
  );
}
