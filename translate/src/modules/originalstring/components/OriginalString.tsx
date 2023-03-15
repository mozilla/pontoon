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
import { Highlight } from '~/modules/placeable/components/Highlight';
import type { TermState } from '~/modules/terms';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import { parseEntry, requiresSourceView } from '~/utils/message';
import { editMessageEntry } from '~/utils/message/editMessageEntry';

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
  const isFluent = entity.format === 'ftl';
  let source = entity.original;

  if (isFluent) {
    const entry = parseEntry(source);
    if (entry && !requiresSourceView(entry)) {
      const msg = editMessageEntry(entry);
      if (msg.length === 1) {
        source = msg[0].value;
        // fallthrough
      } else {
        return <RichString message={msg} onClick={onClick} terms={terms} />;
      }
    }
  } else if (hasPluralForms) {
    return <PluralString onClick={onClick} terms={terms} />;
  }

  return (
    <p className='original' onClick={onClick}>
      <Highlight fluent={isFluent} terms={terms}>
        {source}
      </Highlight>
    </p>
  );
}
