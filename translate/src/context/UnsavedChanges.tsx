import React, { createContext, useMemo, useState } from 'react';

export type UnsavedChanges = Readonly<{
  check(): boolean;
  onIgnore: (() => void) | null;
}>;

export type UnsavedActions = {
  /**
   * The `callback` is called as `setTimout(callback)`
   * to avoid an occasional React complaint about
   * updating one component while rendering a different component.
   */
  checkUnsavedChanges(callback: () => void): void;

  /**
   * If `ignore` is true and `checkUnsavedChanges` has been called,
   * its callback is triggered.
   */
  resetUnsavedChanges(ignore: boolean): void;
  setUnsavedChanges(check: () => boolean): void;
};

const initUnsavedChanges: UnsavedChanges = {
  check: () => false,
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
          if (prev.check()) {
            return { check: () => true, onIgnore: callback };
          } else {
            setTimeout(callback);
            return prev;
          }
        }),

      resetUnsavedChanges: (ignore) =>
        setState((prev) => {
          const { onIgnore } = prev;
          if (onIgnore) {
            if (ignore) {
              setTimeout(onIgnore);
              return { check: () => false, onIgnore: null };
            }
            return { ...prev, onIgnore: null };
          } else {
            return prev;
          }
        }),

      setUnsavedChanges: (check: () => boolean) =>
        setState({ check, onIgnore: null }),
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
