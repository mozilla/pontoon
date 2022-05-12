import React, {
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';

import type { FailedChecks } from '~/api/translation';
import { Locale } from '~/context/locale';
import { Location } from '~/context/location';
import { usePluralForm, useTranslationForEntity } from '~/context/pluralForm';
import { useCheckUnsavedChanges } from '~/context/unsavedChanges';
import {
  resetFailedChecks,
  resetHelperElementIndex,
  updateTranslation,
  updateFailedChecks,
  updateSelection,
} from '~/core/editor/actions';
import { useNextEntity, useSelectedEntity } from '~/core/entities/hooks';
import { TERM } from '~/core/term';
import { get as getTerms } from '~/core/term/actions';
import { USER } from '~/core/user';
import { getOptimizedContent } from '~/core/utils';
import { useAppDispatch, useAppSelector, useAppStore } from '~/hooks';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import { ChangeOperation, History, HISTORY } from '~/modules/history';
import {
  deleteTranslation_,
  get as getHistory,
  request as requestHistory,
  updateStatus,
} from '~/modules/history/actions';
import { OTHERLOCALES } from '~/modules/otherlocales';
import { get as getOtherLocales } from '~/modules/otherlocales/actions';
import { TEAM_COMMENTS } from '~/modules/teamcomments';
import {
  get as getTeamComments,
  request as requestTeamComments,
  togglePinnedStatus as togglePinnedTeamCommentStatus,
} from '~/modules/teamcomments/actions';

import { EditorSelector } from './EditorSelector';
import './EntityDetails.css';
import { EntityNavigation } from './EntityNavigation';
import { Helpers } from './Helpers';
import { Metadata } from './Metadata';

/**
 * Component showing details about an entity.
 *
 * Shows the metadata of the entity and an editor for translations.
 */
export function EntityDetails(): React.ReactElement<'section'> | null {
  const history = useAppSelector((state) => state[HISTORY]);
  const isReadOnlyEditor = useReadonlyEditor();
  const location = useContext(Location);
  const nextEntity = useNextEntity();
  const otherlocales = useAppSelector((state) => state[OTHERLOCALES]);
  const teamComments = useAppSelector((state) => state[TEAM_COMMENTS]);
  const terms = useAppSelector((state) => state[TERM]);
  const user = useAppSelector((state) => state[USER]);
  const dispatch = useAppDispatch();
  const store = useAppStore();

  const selectedEntity = useSelectedEntity();
  const activeTranslation = useTranslationForEntity(selectedEntity);
  const { pluralForm, setPluralForm } = usePluralForm(selectedEntity);

  const commentTabRef = useRef<{ _reactInternalFiber: { index: number } }>(
    null,
  );
  const [commentTabIndex, setCommentTabIndex] = useState(0);
  const [contactPerson, setContactPerson] = useState('');
  const resetContactPerson = useCallback(() => setContactPerson(''), []);
  const locale = useContext(Locale);
  const checkUnsavedChanges = useCheckUnsavedChanges();

  const { entity, locale: lc, project } = location;

  useEffect(() => {
    if (!selectedEntity) {
      return;
    }

    // Only show failed checks for active translations that are approved,
    // pretranslated or fuzzy, i.e. when their status icon is colored as
    // error/warning in the string list
    if (
      activeTranslation &&
      (activeTranslation.errors.length || activeTranslation.warnings.length) &&
      (activeTranslation.approved ||
        activeTranslation.pretranslated ||
        activeTranslation.fuzzy)
    ) {
      const failedChecks: FailedChecks = {
        clErrors: activeTranslation.errors,
        clWarnings: activeTranslation.warnings,
        pErrors: [],
        pndbWarnings: [],
        ttWarnings: [],
      };
      dispatch(updateFailedChecks(failedChecks, 'stored'));
    } else {
      dispatch(resetFailedChecks());
    }

    dispatch(resetHelperElementIndex());
    dispatch(requestHistory(entity, pluralForm));
    dispatch(getHistory(entity, lc, pluralForm));

    const { format, machinery_original, pk } = selectedEntity;
    const source = getOptimizedContent(machinery_original, format);

    if (source !== terms.sourceString && project !== 'terminology') {
      dispatch(getTerms(source, lc));
    }

    if (pk !== otherlocales.entity) {
      dispatch(getOtherLocales(entity, lc));
    }

    if (pk !== teamComments.entity) {
      dispatch(requestTeamComments(entity));
      dispatch(getTeamComments(entity, lc));
    }
  }, [activeTranslation]);

  const navigateToPath = useCallback(
    (path: string) => checkUnsavedChanges(() => location.push(path)),
    [dispatch, location, store],
  );

  const updateEditorTranslation = useCallback(
    (translation: string, changeSource: string) =>
      dispatch(updateTranslation(translation, changeSource)),
    [dispatch],
  );

  const addTextToEditorTranslation = useCallback(
    (content: string, changeSource?: string) =>
      dispatch(updateSelection(content, changeSource)),
    [dispatch],
  );

  const deleteTranslation__ = useCallback(
    (translationId: number) =>
      dispatch(deleteTranslation_(entity, lc, pluralForm, translationId)),
    [dispatch, entity, lc, pluralForm],
  );

  const togglePinnedStatus = useCallback(
    (pinned: boolean, commentId: number) =>
      dispatch(togglePinnedTeamCommentStatus(pinned, commentId)),
    [dispatch],
  );

  /*
   * This is a copy of EditorBase.updateTranslationStatus().
   * When changing this function, you probably want to change both.
   * We might want to refactor to keep the logic in one place only.
   */
  const updateTranslationStatus = useCallback(
    (translationId: number, change: ChangeOperation) => {
      if (!selectedEntity) {
        return;
      }

      // No need to check for unsaved changes in `EditorBase.updateTranslationStatus()`,
      // because it cannot be triggered for the use case of bug 1508474.
      checkUnsavedChanges(() =>
        dispatch(
          updateStatus(
            change,
            selectedEntity,
            locale,
            { pluralForm, setPluralForm },
            translationId,
            nextEntity,
            location,
            false,
          ),
        ),
      );
    },
    [dispatch, locale, nextEntity, location, pluralForm, selectedEntity, store],
  );

  if (!selectedEntity) {
    return <section className='entity-details'></section>;
  }

  return (
    <section className='entity-details'>
      <section className='main-column'>
        <EntityNavigation />
        <Metadata
          entity={selectedEntity}
          isReadOnlyEditor={isReadOnlyEditor}
          pluralForm={pluralForm}
          terms={terms}
          addTextToEditorTranslation={addTextToEditorTranslation}
          navigateToPath={navigateToPath}
          teamComments={teamComments}
          user={user}
          commentTabRef={commentTabRef}
          setCommentTabIndex={setCommentTabIndex}
          setContactPerson={setContactPerson}
        />
        <EditorSelector
          fileFormat={selectedEntity.format}
          key={selectedEntity.pk}
        />
        <History
          entity={selectedEntity}
          history={history}
          isReadOnlyEditor={isReadOnlyEditor}
          user={user}
          deleteTranslation={deleteTranslation__}
          updateTranslationStatus={updateTranslationStatus}
          updateEditorTranslation={updateEditorTranslation}
        />
      </section>
      <section className='third-column'>
        <Helpers
          entity={selectedEntity}
          isReadOnlyEditor={isReadOnlyEditor}
          otherlocales={otherlocales}
          teamComments={teamComments}
          terms={terms}
          togglePinnedStatus={togglePinnedStatus}
          parameters={location}
          user={user}
          addTextToEditorTranslation={addTextToEditorTranslation}
          navigateToPath={navigateToPath}
          commentTabRef={commentTabRef}
          commentTabIndex={commentTabIndex}
          setCommentTabIndex={setCommentTabIndex}
          contactPerson={contactPerson}
          resetContactPerson={resetContactPerson}
        />
      </section>
    </section>
  );
}
