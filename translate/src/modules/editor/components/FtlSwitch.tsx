import { Localized } from '@fluent/react';
import classNames from 'classnames';
import React, { useCallback, useContext, useMemo } from 'react';

import { EditorActions, EditorData, EditorResult } from '~/context/Editor';
import { ShowNotification } from '~/context/Notification';
import { FTL_NOT_SUPPORTED_RICH_EDITOR } from '~/modules/notification/messages';
import { USER } from '~/modules/user';
import { requiresSourceView, parseEntry } from '~/utils/message';
import { useAppSelector } from '~/hooks';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';

import './FtlSwitch.css';
import { EntityView } from '~/context/EntityView';

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
  const { toggleSourceView } = useContext(EditorActions);
  const { sourceView } = useContext(EditorData);
  const edit = useContext(EditorResult);
  const { entity } = useContext(EntityView);

  const hasError = useMemo(() => {
    if (sourceView && entity.format === 'fluent') {
      const source = edit[0].value;
      return (
        !source || requiresSourceView('fluent', parseEntry('fluent', source))
      );
    } else {
      return false;
    }
  }, [sourceView, edit, entity.format]);

  const handleClick = useCallback(() => {
    if (hasError) {
      showNotification(FTL_NOT_SUPPORTED_RICH_EDITOR);
    } else {
      toggleSourceView();
    }
  }, [hasError, toggleSourceView]);

  if (entity.format !== 'fluent' || !isAuthenticated || readonly) {
    return null;
  }

  const cn = classNames('ftl', sourceView && 'active', hasError && 'error');
  const id = sourceView
    ? 'editor-FtlSwitch--active'
    : 'editor-FtlSwitch--toggle';
  return (
    <Localized id={id} attrs={{ title: true }}>
      <button className={cn} onClick={handleClick}>
        FTL
      </button>
    </Localized>
  );
}
