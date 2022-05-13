import classNames from 'classnames';
import React from 'react';

import { useTranslationForEntity } from '~/context/PluralForm';
import { EDITOR } from '~/core/editor';
import { useSelectedEntity } from '~/core/entities/hooks';
import { addNotification } from '~/core/notification/actions';
import { notificationMessages } from '~/core/notification/messages';
import { USER } from '~/core/user';
import { useAppDispatch, useAppSelector } from '~/hooks';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';

import { useLoadTranslation } from '../hooks/useLoadTranslation';
import { getSyntaxType } from '../hooks/getSyntaxType';
import { useForceSource } from '../hooks/useForceSource';
import './FluentEditor.css';
import { RichEditor } from './rich/RichEditor';
import { SimpleEditor } from './simple/SimpleEditor';
import { SourceEditor } from './source/SourceEditor';

/**
 * Editor dedicated to modifying Fluent strings.
 *
 * Renders the most appropriate type of editor for the current translation.
 */
export function FluentEditor(): null | React.ReactElement<React.ElementType> {
  const dispatch = useAppDispatch();

  const translation = useAppSelector((state) => state[EDITOR].translation);
  const readonly = useReadonlyEditor();
  const entity = useSelectedEntity();
  const activeTranslation = useTranslationForEntity(entity);
  const isAuthenticated = useAppSelector(
    (state) => state[USER].isAuthenticated,
  );

  const [forceSource, toggleForceSource] = useForceSource();
  useLoadTranslation();

  if (!entity) {
    return null;
  }

  const syntax = getSyntaxType(
    translation || activeTranslation?.string || entity.original,
  );

  if (syntax === 'complex') {
    // When the syntax is complex, the editor is blocked in source mode, and it
    // becomes impossible to switch to a different editor type. Thus we show a
    // notification to the user if they try to use the "FTL" switch button.

    // TODO: To Localize
    const ftlSwitch =
      isAuthenticated && !readonly ? (
        <button
          className='ftl active'
          title='Advanced FTL mode enabled'
          onClick={() =>
            dispatch(
              addNotification(
                notificationMessages.FTL_NOT_SUPPORTED_RICH_EDITOR,
              ),
            )
          }
        >
          FTL
        </button>
      ) : null;
    return <SourceEditor ftlSwitch={ftlSwitch} />;
  }

  // Choose which editor implementation to render.
  const Editor = forceSource
    ? SourceEditor
    : syntax === 'simple'
    ? SimpleEditor
    : RichEditor;

  // Show a button to allow switching to the source editor.
  // But only if the user is logged in and the string is not read-only.
  // TODO: To Localize
  const ftlSwitch =
    isAuthenticated && !readonly ? (
      <button
        className={classNames('ftl', forceSource && 'active')}
        title='Toggle between simple and advanced FTL mode'
        onClick={toggleForceSource}
      >
        FTL
      </button>
    ) : null;

  return <Editor ftlSwitch={ftlSwitch} />;
}
