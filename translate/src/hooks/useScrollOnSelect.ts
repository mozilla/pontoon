import { useEffect, useRef } from 'react';

import { scrollIntoView } from '~/utils/scrollIntoView';

/**
 * Ref for a list item that scrolls itself into view when it becomes selected,
 * e.g. by keyboard navigation of the Machinery or Locales helper tabs.
 */
export function useScrollOnSelect<T extends Element>(isSelected: boolean) {
  const ref = useRef<T>(null);
  useEffect(() => {
    if (isSelected) {
      scrollIntoView(ref.current);
    }
  }, [isSelected]);
  return ref;
}
