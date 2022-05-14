import React, {
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';

import type { FailedChecks } from '~/api/translation';
import { HelperSelectionProvider } from '~/context/HelperSelection';
import { Location } from '~/context/Location';
import { usePluralForm, useTranslationForEntity } from '~/context/PluralForm';
import { UnsavedActions } from '~/context/UnsavedChanges';
import { Editor } from '~/core/editor/components/Editor';
import {
  resetFailedChecks,
  updateFailedChecks,
  updateSelection,
} from '~/core/editor/actions';
import { useSelectedEntity } from '~/core/entities/hooks';
import { TERM } from '~/core/term';
import { get as getTerms } from '~/core/term/actions';
import { USER } from '~/core/user';
import { getOptimizedContent } from '~/core/utils';
import { useAppDispatch, useAppSelector, useAppStore } from '~/hooks';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import { History } from '~/modules/history';
import {
  get as getHistory,
  request as requestHistory,
} from '~/modules/history/actions';
import { OTHERLOCALES } from '~/modules/otherlocales';
import { get as getOtherLocales } from '~/modules/otherlocales/actions';
import { TEAM_COMMENTS } from '~/modules/teamcomments';
import {
  get as getTeamComments,
  request as requestTeamComments,
  togglePinnedStatus as togglePinnedTeamCommentStatus,
} from '~/modules/teamcomments/actions';

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
  const isReadOnlyEditor = useReadonlyEditor();
  const location = useContext(Location);
  const otherlocales = useAppSelector((state) => state[OTHERLOCALES]);
  const teamComments = useAppSelector((state) => state[TEAM_COMMENTS]);
  const terms = useAppSelector((state) => state[TERM]);
  const user = useAppSelector((state) => state[USER]);
  const dispatch = useAppDispatch();
  const store = useAppStore();

  const selectedEntity = useSelectedEntity();
  const activeTranslation = useTranslationForEntity(selectedEntity);
  const { pluralForm } = usePluralForm(selectedEntity);

  const commentTabRef = useRef<{ _reactInternalFiber: { index: number } }>(
    null,
  );
  const [commentTabIndex, setCommentTabIndex] = useState(0);
  const [contactPerson, setContactPerson] = useState('');
  const resetContactPerson = useCallback(() => setContactPerson(''), []);
  const { checkUnsavedChanges } = useContext(UnsavedActions);

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

  const addTextToEditorTranslation = useCallback(
    (content: string, changeSource?: string) =>
      dispatch(updateSelection(content, changeSource)),
    [dispatch],
  );

  const togglePinnedStatus = useCallback(
    (pinned: boolean, commentId: number) =>
      dispatch(togglePinnedTeamCommentStatus(pinned, commentId)),
    [dispatch],
  );

  if (!selectedEntity) {
    return <section className='entity-details'></section>;
  }

  return (
    <HelperSelectionProvider translation={activeTranslation}>
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
          <Editor fileFormat={selectedEntity.format} key={selectedEntity.pk} />
          <History />
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
    </HelperSelectionProvider>
  );
}
