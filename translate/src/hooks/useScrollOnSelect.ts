import { useEffect } from 'react';

import { scrollIntoView } from '~/utils/scrollIntoView';

/** Scroll `ref` into view whenever it becomes selected. */
export function useScrollOnSelect(
  ref: React.RefObject<Element | null>,
  isSelected: boolean,
): void {
  useEffect(() => {
    if (isSelected) {
      scrollIntoView(ref.current);
    }
  }, [isSelected]);
}
