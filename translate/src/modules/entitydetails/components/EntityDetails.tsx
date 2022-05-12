import React, {
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';

import type { Entity } from '~/api/entity';
import { FailedChecks } from '~/api/translation';
import { Locale } from '~/context/locale';
import { Location, LocationType } from '~/context/location';
import {
  PluralFormType,
  usePluralForm,
  useTranslationForEntity,
} from '~/context/pluralForm';
import { useCheckUnsavedChanges } from '~/context/unsavedChanges';
import { addComment_ } from '~/core/comments/actions';
import {
  resetEditor,
  resetFailedChecks,
  resetHelperElementIndex,
  updateTranslation,
  updateFailedChecks,
  updateSelection,
} from '~/core/editor/actions';
import {
  useNextEntity,
  usePreviousEntity,
  useSelectedEntity,
} from '~/core/entities/hooks';
import { addNotification } from '~/core/notification/actions';
import { notificationMessages } from '~/core/notification/messages';
import { TERM, TermState } from '~/core/term';
import { get as getTerms } from '~/core/term/actions';
import { USER, UserState } from '~/core/user';
import { getOptimizedContent } from '~/core/utils';
import { AppStore, useAppDispatch, useAppSelector, useAppStore } from '~/hooks';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import {
  ChangeOperation,
  History,
  HistoryState,
  HISTORY,
} from '~/modules/history';
import {
  deleteTranslation_,
  get as getHistory,
  request as requestHistory,
  updateStatus,
} from '~/modules/history/actions';
import { MachineryState, MACHINERY } from '~/modules/machinery';
import {
  get as getMachinery,
  getConcordanceSearchResults,
  resetSearch,
  setEntity,
} from '~/modules/machinery/actions';
import { LocalesState, OTHERLOCALES } from '~/modules/otherlocales';
import { get as getOtherLocales } from '~/modules/otherlocales/actions';
import { TEAM_COMMENTS, TeamCommentState } from '~/modules/teamcomments';
import {
  get as getTeamComments,
  request as requestTeamComments,
  togglePinnedStatus as togglePinnedTeamCommentStatus,
} from '~/modules/teamcomments/actions';
import type { AppDispatch } from '~/store';

import { EditorSelector } from './EditorSelector';
import './EntityDetails.css';
import { EntityNavigation } from './EntityNavigation';
import { Helpers } from './Helpers';
import { Metadata } from './Metadata';

type Props = {
  activeTranslationString: string;
  history: HistoryState;
  isReadOnlyEditor: boolean;
  machinery: MachineryState;
  nextEntity?: Entity;
  previousEntity?: Entity;
  otherlocales: LocalesState;
  teamComments: TeamCommentState;
  terms: TermState;
  parameters: LocationType;
  pluralForm: PluralFormType;
  selectedEntity?: Entity;
  user: UserState;
};

type InternalProps = Props & {
  dispatch: AppDispatch;
  store: AppStore;
};

/**
 * Component showing details about an entity.
 *
 * Shows the metadata of the entity and an editor for translations.
 */
export function EntityDetailsBase({
  activeTranslationString,
  dispatch,
  history,
  isReadOnlyEditor,
  machinery,
  nextEntity,
  previousEntity,
  otherlocales,
  teamComments,
  terms,
  parameters,
  pluralForm: { pluralForm, setPluralForm },
  selectedEntity,
  store,
  user,
}: InternalProps): React.ReactElement<'section'> | null {
  const commentTabRef = useRef<{ _reactInternalFiber: { index: number } }>(
    null,
  );
  const [commentTabIndex, setCommentTabIndex] = useState(0);
  const [contactPerson, setContactPerson] = useState('');
  const resetContactPerson = useCallback(() => setContactPerson(''), []);
  const locale = useContext(Locale);
  const checkUnsavedChanges = useCheckUnsavedChanges();

  const { entity, locale: lc, project } = parameters;

  const updateFailedChecks_ = useCallback(() => {
    if (!selectedEntity) {
      return;
    }

    const plural = pluralForm === -1 ? 0 : pluralForm;
    const translation = selectedEntity.translation[plural];

    // Only show failed checks for active translations that are approved,
    // pretranslated or fuzzy, i.e. when their status icon is colored as
    // error/warning in the string list
    if (
      translation &&
      (translation.errors.length || translation.warnings.length) &&
      (translation.approved || translation.pretranslated || translation.fuzzy)
    ) {
      const failedChecks: FailedChecks = {
        clErrors: translation.errors,
        clWarnings: translation.warnings,
        pErrors: [],
        pndbWarnings: [],
        ttWarnings: [],
      };
      dispatch(updateFailedChecks(failedChecks, 'stored'));
    } else {
      dispatch(resetFailedChecks());
    }
  }, [dispatch, pluralForm, selectedEntity]);

  /*
   * Only fetch helpers data if the entity changes.
   * Also fetch history data if the pluralForm changes.
   */
  const fetchHelpersData = () => {
    if (!entity || !selectedEntity) {
      return;
    }

    dispatch(resetHelperElementIndex());

    const { pk } = selectedEntity;

    if (
      pk !== history.entity ||
      pluralForm !== history.pluralForm ||
      selectedEntity === nextEntity
    ) {
      dispatch(requestHistory(entity, pluralForm));
      dispatch(getHistory(entity, lc, pluralForm));
    }

    const source = getOptimizedContent(
      selectedEntity.machinery_original,
      selectedEntity.format,
    );

    if (source !== terms.sourceString && project !== 'terminology') {
      dispatch(getTerms(source, lc));
    }

    if (pk !== machinery.entity) {
      dispatch(resetSearch(''));
      dispatch(setEntity(pk, source));
      dispatch(getMachinery(source, locale, user.isAuthenticated, pk));
    }

    if (pk !== otherlocales.entity) {
      dispatch(getOtherLocales(entity, lc));
    }

    if (pk !== teamComments.entity) {
      dispatch(requestTeamComments(entity));
      dispatch(getTeamComments(entity, lc));
    }
  };

  useEffect(() => {
    updateFailedChecks_();
    fetchHelpersData();
  }, [pluralForm, selectedEntity]);

  const mounted = useRef(false);
  useEffect(() => {
    if (mounted.current) {
      if (selectedEntity === nextEntity) {
        updateFailedChecks_();
        fetchHelpersData();
      }
    } else {
      mounted.current = true;
    }
  }, [activeTranslationString]);

  const searchMachinery = useCallback(
    (query: string, page?: number) => {
      if (query) {
        if (page) {
          dispatch(getConcordanceSearchResults(query, locale, page));
        } else {
          dispatch(resetSearch(query));
          dispatch(getConcordanceSearchResults(query, locale));
          dispatch(getMachinery(query, locale, user.isAuthenticated, null));
        }
      } else {
        dispatch(resetSearch(''));
        if (selectedEntity) {
          // On empty query, use source string as input
          const source = getOptimizedContent(
            selectedEntity.machinery_original,
            selectedEntity.format,
          );
          dispatch(
            getMachinery(
              source,
              locale,
              user.isAuthenticated,
              selectedEntity.pk,
            ),
          );
        }
      }
    },
    [dispatch, locale, selectedEntity, user.isAuthenticated],
  );

  const copyLinkToClipboard = useCallback(async () => {
    const { locale, project, resource, entity } = parameters;
    const { protocol, host } = window.location;

    const string_link = `${protocol}//${host}/${locale}/${project}/${resource}/?string=${entity}`;
    await navigator.clipboard.writeText(string_link);

    // Notify the user of the change that happened.
    dispatch(addNotification(notificationMessages.STRING_LINK_COPIED));
  }, [dispatch, parameters]);

  const goToNextEntity = useCallback(
    () =>
      checkUnsavedChanges(() => {
        parameters.push({ entity: nextEntity?.pk ?? 0 });
        dispatch(resetEditor());
      }),
    [dispatch, parameters, nextEntity, store],
  );

  const goToPreviousEntity = useCallback(
    () =>
      checkUnsavedChanges(() => {
        parameters.push({ entity: previousEntity?.pk ?? 0 });
        dispatch(resetEditor());
      }),
    [dispatch, parameters, previousEntity, store],
  );

  const navigateToPath = useCallback(
    (path: string) => checkUnsavedChanges(() => parameters.push(path)),
    [dispatch, parameters, store],
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

  const addComment__ = useCallback(
    (comment: string, translation: number | null | undefined) =>
      dispatch(addComment_(entity, lc, pluralForm, translation, comment)),
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
            parameters,
            false,
          ),
        ),
      );
    },
    [
      dispatch,
      locale,
      nextEntity,
      parameters,
      pluralForm,
      selectedEntity,
      store,
    ],
  );

  if (!selectedEntity) {
    return <section className='entity-details'></section>;
  }

  return (
    <section className='entity-details'>
      <section className='main-column'>
        <EntityNavigation
          copyLinkToClipboard={copyLinkToClipboard}
          goToNextEntity={goToNextEntity}
          goToPreviousEntity={goToPreviousEntity}
        />
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
          addComment={addComment__}
          updateTranslationStatus={updateTranslationStatus}
          updateEditorTranslation={updateEditorTranslation}
        />
      </section>
      <section className='third-column'>
        <Helpers
          entity={selectedEntity}
          isReadOnlyEditor={isReadOnlyEditor}
          machinery={machinery}
          otherlocales={otherlocales}
          teamComments={teamComments}
          terms={terms}
          addComment={addComment__}
          togglePinnedStatus={togglePinnedStatus}
          parameters={parameters}
          user={user}
          searchMachinery={searchMachinery}
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

export function EntityDetails(): React.ReactElement<typeof EntityDetailsBase> {
  const entity = useSelectedEntity();
  const state = {
    activeTranslationString: useTranslationForEntity(entity)?.string ?? '',
    history: useAppSelector((state) => state[HISTORY]),
    isReadOnlyEditor: useReadonlyEditor(),
    machinery: useAppSelector((state) => state[MACHINERY]),
    nextEntity: useNextEntity(),
    previousEntity: usePreviousEntity(),
    otherlocales: useAppSelector((state) => state[OTHERLOCALES]),
    teamComments: useAppSelector((state) => state[TEAM_COMMENTS]),
    terms: useAppSelector((state) => state[TERM]),
    parameters: useContext(Location),
    pluralForm: usePluralForm(entity),
    selectedEntity: entity,
    user: useAppSelector((state) => state[USER]),
  };
  return (
    <EntityDetailsBase
      {...state}
      dispatch={useAppDispatch()}
      store={useAppStore()}
    />
  );
}
