import NProgress from 'nprogress';
import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

import { fetchEntityHistory } from '~/api/entity';
import { deleteTranslation, HistoryTranslation } from '~/api/translation';
import { addNotification } from '~/core/notification/actions';
import { notificationMessages } from '~/core/notification/messages';
import { useAppDispatch } from '~/hooks';

import { EntityView } from './EntityView';
import { Locale } from './Locale';

export type HistoryData = {
  readonly fetching: boolean;
  readonly translations: HistoryTranslation[];
  updateHistory(): void;
};

const initialHistory: HistoryData = {
  fetching: false,
  translations: [],
  updateHistory: () => {},
};

export const HistoryData = createContext(initialHistory);

export function HistoryProvider({
  children,
}: {
  children: React.ReactElement;
}) {
  const { code } = useContext(Locale);
  const {
    entity: { pk },
    hasPluralForms,
    pluralForm,
  } = useContext(EntityView);

  const [fetching, setFetching] = useState(false);
  const [translations, setTranslations] = useState<HistoryTranslation[]>([]);

  const pf = hasPluralForms ? pluralForm : -1;
  const updateHistory = useCallback(() => {
    if (pk) {
      setFetching(true);
      // Not using async/await to not leak function color
      fetchEntityHistory(pk, code, pf).then((translations) => {
        setTranslations(translations);
        setFetching(false);
      });
    } else {
      setFetching(false);
      setTranslations([]);
    }
  }, [code, pk, pf]);

  useEffect(() => {
    setTranslations([]);
    updateHistory();
  }, [updateHistory]);

  const value = useMemo(
    () => ({ fetching, translations, updateHistory }),
    [fetching, translations, updateHistory],
  );

  return <HistoryData.Provider value={value}>{children}</HistoryData.Provider>;
}

export function useDeleteTranslation() {
  const dispatch = useAppDispatch();
  const { updateHistory } = useContext(HistoryData);

  return useCallback(
    async (translationId: number) => {
      NProgress.start();

      const { status } = await deleteTranslation(translationId);
      if (status) {
        dispatch(addNotification(notificationMessages.TRANSLATION_DELETED));
        updateHistory();
      } else {
        dispatch(
          addNotification(notificationMessages.UNABLE_TO_DELETE_TRANSLATION),
        );
      }

      NProgress.done();
    },
    [updateHistory],
  );
}
