import React, {
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';

import { EntityView, useActiveTranslation } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { Location } from '~/context/Location';
import { UnsavedActions } from '~/context/UnsavedChanges';
import { Editor } from '~/modules/editor/components/Editor';
import { OriginalString } from '~/modules/originalstring';
import { TERM } from '~/modules/terms';
import { get as getTerms } from '~/modules/terms/actions';
import { USER } from '~/modules/user';
import { useAppDispatch, useAppSelector, useAppStore } from '~/hooks';
import { History } from '~/modules/history/components/History';
import { OTHERLOCALES } from '~/modules/otherlocales';
import { get as getOtherLocales } from '~/modules/otherlocales/actions';
import { TEAM_COMMENTS } from '~/modules/teamcomments';
import {
  get as getTeamComments,
  request as requestTeamComments,
  togglePinnedStatus as togglePinnedTeamCommentStatus,
} from '~/modules/teamcomments/actions';
import { getPlainMessage } from '~/utils/message';

import { ContextIssueButton } from './ContextIssueButton';
import { EntityNavigation } from './EntityNavigation';
import { Helpers } from './Helpers';
import { Metadata } from './Metadata';
import { Screenshots } from './Screenshots';

import './EntityDetails.css';

/**
 * Component showing details about an entity.
 *
 * Shows the metadata of the entity and an editor for translations.
 */
export function EntityDetails(): React.ReactElement<'section'> | null {
  const location = useContext(Location);
  const otherlocales = useAppSelector((state) => state[OTHERLOCALES]);
  const teamComments = useAppSelector((state) => state[TEAM_COMMENTS]);
  const terms = useAppSelector((state) => state[TERM]);
  const user = useAppSelector((state) => state[USER]);
  const dispatch = useAppDispatch();
  const store = useAppStore();

  const activeTranslation = useActiveTranslation();
  const { entity: selectedEntity } = useContext(EntityView);

  const commentTabRef = useRef<{ _reactInternalFiber: { index: number } }>(
    null,
  );
  const [commentTabIndex, setCommentTabIndex] = useState(0);
  const [contactPerson, setContactPerson] = useState('');
  const resetContactPerson = useCallback(() => setContactPerson(''), []);
  const { checkUnsavedChanges } = useContext(UnsavedActions);

  const { entity, locale: lc, project } = location;

  useEffect(() => {
    const { format, machinery_original, pk } = selectedEntity;
    const source = getPlainMessage(machinery_original, format);

    if (source !== terms.sourceString && project !== 'terminology') {
      dispatch(getTerms(source, lc));
    }

    if (entity > 0) {
      if (pk !== otherlocales.entity) {
        dispatch(getOtherLocales(entity, lc));
      }

      if (pk !== teamComments.entity) {
        dispatch(requestTeamComments(entity));
        dispatch(getTeamComments(entity, lc));
      }
    }
  }, [activeTranslation, selectedEntity]);

  const navigateToPath = useCallback(
    (path: string) => checkUnsavedChanges(() => location.push(path)),
    [dispatch, location, store],
  );

  const togglePinnedStatus = useCallback(
    (pinned: boolean, commentId: number) =>
      dispatch(togglePinnedTeamCommentStatus(pinned, commentId)),
    [dispatch],
  );

  const { code } = useContext(Locale);

  const openTeamComments = useCallback(() => {
    const teamCommentsTab = commentTabRef.current;

    // FIXME: This is an ugly hack.
    // https://github.com/mozilla/pontoon/issues/2300
    const index = teamCommentsTab?._reactInternalFiber.index ?? 0;

    setCommentTabIndex(index);
    setContactPerson(selectedEntity.project.contact.name);
  }, [selectedEntity, setCommentTabIndex, setContactPerson]);

  const showContextIssueButton =
    user.isAuthenticated && selectedEntity.project.contact;

  // No content while loading entity data
  return selectedEntity.pk === 0 ? null : (
    <section className='entity-details'>
      <section className='main-column'>
        <EntityNavigation />
        <section className='original-string-panel'>
          {showContextIssueButton && (
            <ContextIssueButton openTeamComments={openTeamComments} />
          )}
          <Screenshots source={selectedEntity.comment} locale={code} />
          <OriginalString navigateToPath={navigateToPath} terms={terms} />
          <Metadata
            entity={selectedEntity}
            navigateToPath={navigateToPath}
            teamComments={teamComments}
          />
        </section>
        <Editor />
        <History />
      </section>
      <section className='third-column'>
        <Helpers
          entity={selectedEntity}
          otherlocales={otherlocales}
          teamComments={teamComments}
          terms={terms}
          togglePinnedStatus={togglePinnedStatus}
          parameters={location}
          user={user}
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
