import React, { createContext, useMemo, useState } from 'react';

export type UnsavedChanges = Readonly<{
  onIgnore: (() => void) | null;
  exist: boolean;
}>;

export type UnsavedActions = {
  checkUnsavedChanges(callback: () => void): void;

  /**
   * If `ignore` is true and `checkUnsavedChanges` has been called,
   * its callback is triggered.
   */
  resetUnsavedChanges(ignore: boolean): void;
  setUnsavedChanges(exist: boolean): void;
};

const initUnsavedChanges: UnsavedChanges = {
  exist: false,
  onIgnore: null,
};

const initUnsavedActions: UnsavedActions = {
  checkUnsavedChanges: (callback) => {
    callback();
  },
  resetUnsavedChanges: () => {},
  setUnsavedChanges: () => {},
};

export const UnsavedChanges = createContext(initUnsavedChanges);
export const UnsavedActions = createContext(initUnsavedActions);

/**
 * Wraps the `UnsavedChanges` provider with an additional ref provider used by
 * `useCheckUnsavedChanges` and `useSetUnsavedChanges` to avoid re-renders.
 */
export function UnsavedChangesProvider({
  children,
}: {
  children: React.ReactElement;
}) {
  const [state, setState] = useState(initUnsavedChanges);

  const actions = useMemo<UnsavedActions>(
    () => ({
      checkUnsavedChanges: (callback: () => void) =>
        setState((prev) => {
          if (prev.exist) {
            return { ...prev, onIgnore: callback };
          } else {
            callback();
            return prev;
          }
        }),

      resetUnsavedChanges: (ignore) =>
        setState((prev) => {
          if (prev.onIgnore) {
            if (ignore) {
              // Needs to happen after the return to avoid an occasional React
              // complaint about updating one component while rendering a
              // different component.
              const { onIgnore } = prev;
              setTimeout(onIgnore);

              return { ...prev, exist: false, onIgnore: null };
            }
            return { ...prev, onIgnore: null };
          } else {
            return prev;
          }
        }),

      setUnsavedChanges: (exist: boolean) =>
        setState((prev) =>
          prev.exist === exist && !prev.onIgnore
            ? prev
            : { ...prev, exist, onIgnore: null },
        ),
    }),
    [],
  );

  return (
    <UnsavedChanges.Provider value={state}>
      <UnsavedActions.Provider value={actions}>
        {children}
      </UnsavedActions.Provider>
    </UnsavedChanges.Provider>
  );
}
