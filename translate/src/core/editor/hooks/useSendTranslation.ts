import { useContext } from 'react';

import { Locale } from '~/context/locale';
import { useNextEntity, useSelectedEntity } from '~/core/entities/hooks';
import { usePluralForm } from '~/core/plural/hooks';
import { useAppDispatch, useAppSelector } from '~/hooks';
import { useLocation } from '~/hooks/useLocation';

import actions from '../actions';

/**
 * Return a function to send a translation to the server.
 */
export default function useSendTranslation(): (
  ignoreWarnings?: boolean,
  content?: string,
) => void {
  const dispatch = useAppDispatch();

  const translation = useAppSelector((state) => state.editor.translation);
  const isRunningRequest = useAppSelector(
    (state) => state.editor.isRunningRequest,
  );
  const machinerySources = useAppSelector(
    (state) => state.editor.machinerySources,
  );
  const machineryTranslation = useAppSelector(
    (state) => state.editor.machineryTranslation,
  );
  const entity = useSelectedEntity();
  const locale = useContext(Locale);
  const user = useAppSelector((state) => state.user);
  const router = useAppSelector((state) => state.router);
  const pluralForm = usePluralForm(entity);
  const nextEntity = useNextEntity();
  const { resource } = useLocation();

  return (ignoreWarnings?: boolean, content?: string) => {
    if (isRunningRequest || !entity || !locale) {
      return;
    }

    const translationContent = content || translation;

    if (typeof translationContent !== 'string') {
      throw new Error(
        'Trying to save an unsupported non-string translation: ' +
          typeof translationContent,
      );
    }

    let realMachinerySources = machinerySources;
    if (realMachinerySources && machineryTranslation !== translation) {
      realMachinerySources = [];
    }

    dispatch(
      actions.sendTranslation(
        entity,
        translationContent,
        locale,
        pluralForm,
        user.settings.forceSuggestions,
        nextEntity,
        router,
        resource,
        ignoreWarnings,
        realMachinerySources,
      ),
    );
  };
}
