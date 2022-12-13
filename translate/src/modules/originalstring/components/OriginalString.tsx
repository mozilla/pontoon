import React, {
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';
import { TermType } from '~/api/terminology';
import { EditorActions } from '~/context/Editor';

import { EntityView } from '~/context/EntityView';
import { Highlight } from '~/core/placeable/components/Highlight';
import type { TermState } from '~/core/term';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import { getPlainMessage, getSyntaxType, parseEntry } from '~/utils/message';

import { PluralString } from './PluralString';
import { RichString } from './RichString';
import { TermsPopup } from './TermsPopup';

type Props = {
  navigateToPath: (path: string) => void;
  terms: TermState;
};

/**
 * Proxy for an OriginalString component based on the format of the entity.
 */
export function OriginalString({
  navigateToPath,
  terms,
}: Props): React.ReactElement {
  const { entity } = useContext(EntityView);
  const isReadOnlyEditor = useReadonlyEditor();
  const { setEditorSelection } = useContext(EditorActions);

  const [popupTerms, setPopupTerms] = useState<TermType[]>([]);
  const hidePopupTerms = useCallback(() => setPopupTerms([]), []);

  const mounted = useRef(false);
  useEffect(() => {
    if (mounted.current) {
      setPopupTerms([]);
    } else {
      mounted.current = true;
    }
  }, [entity]);

  const handleClickOnPlaceable = useCallback(
    ({ target }: React.MouseEvent<HTMLElement>) => {
      if (target instanceof HTMLElement) {
        if (target.classList.contains('placeable')) {
          if (isReadOnlyEditor) {
            return;
          }
          if (target.dataset['match']) {
            setEditorSelection(target.dataset['match']);
          } else if (target.firstChild instanceof Text) {
            setEditorSelection(target.firstChild.data);
          }
        }

        // Handle click on Term
        const markedTerm = target.dataset['match'];
        if (markedTerm) {
          setPopupTerms(
            terms.terms?.filter((t) => t.text === markedTerm) ?? [],
          );
        }
      }
    },
    [isReadOnlyEditor, setEditorSelection, terms],
  );

  return (
    <>
      <InnerOriginalString onClick={handleClickOnPlaceable} terms={terms} />
      {popupTerms.length > 0 && (
        <TermsPopup
          navigateToPath={navigateToPath}
          onClick={hidePopupTerms}
          terms={popupTerms}
        />
      )}
    </>
  );
}

function InnerOriginalString({
  onClick,
  terms,
}: {
  onClick: (event: React.MouseEvent<HTMLElement>) => void;
  terms: TermState;
}): React.ReactElement {
  const { entity, hasPluralForms } = useContext(EntityView);

  let { format, original } = entity;
  const isFluent = format === 'ftl';

  if (isFluent) {
    const entry = parseEntry(original);
    const syntax = getSyntaxType(entry);
    if (entry) {
      switch (syntax) {
        case 'rich':
          return <RichString entry={entry} onClick={onClick} terms={terms} />;

        case 'simple':
          original = getPlainMessage(entry, format);
          break;
      }
    }
  } else if (hasPluralForms) {
    return <PluralString onClick={onClick} terms={terms} />;
  }

  return (
    <p className='original' onClick={onClick}>
      <Highlight fluent={isFluent} terms={terms}>
        {original}
      </Highlight>
    </p>
  );
}
