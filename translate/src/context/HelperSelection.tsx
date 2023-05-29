import React, { createContext, useEffect, useState } from 'react';

import { useActiveTranslation } from './EntityView';

type HelperSelection = Readonly<{
  /**
   * Index of selected tab in the helpers box. Assumes the following:
   * - `0`: Machinery
   * - `1`: Other Locales
   */
  tab: number;

  /** Index of selected item in the helpers box */
  element: number;

  setElement(element: number): void;
  setTab(tab: number): void;
}>;

const initHelpers: HelperSelection = {
  tab: 0,
  element: -1,
  setElement: () => {},
  setTab: () => {},
};

export const HelperSelection = createContext(initHelpers);

export function HelperSelectionProvider({
  children,
}: {
  children: React.ReactElement;
}) {
  const translation = useActiveTranslation();
  const [state, setState] = useState(() => ({
    ...initHelpers,
    setElement: (element) => setState((prev) => ({ ...prev, element })),
    setTab: (tab) => setState((prev) => ({ ...prev, tab, element: -1 })),
  })) as [
    HelperSelection,
    React.Dispatch<React.SetStateAction<HelperSelection>>,
  ];

  useEffect(() => state.setElement(-1), [translation]);

  return (
    <HelperSelection.Provider value={state}>
      {children}
    </HelperSelection.Provider>
  );
}
