import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';

export type UnsavedChanges = Readonly<{
  /** Call with `null` to reset all fields */
  set: (
    next:
      | { exist: boolean; ignore: false }
      | { callback: () => void; show: true }
      | { ignore: true }
      | null,
  ) => void;
  callback: (() => void) | null;
  exist: boolean;
  ignore: boolean;
  show: boolean;
}>;

const initUnsavedChanges: UnsavedChanges = {
  callback: null,
  exist: false,
  ignore: false,
  show: false,
  set: () => {},
};

export const UnsavedChanges = createContext(initUnsavedChanges);

const UnsavedChangesRef = createContext<React.MutableRefObject<UnsavedChanges>>(
  { current: initUnsavedChanges },
);

/**
 * Wraps the `UnsavedChanges` provider with an additional ref provider used by
 * `useCheckUnsavedChanges` and `useSetUnsavedChanges` to avoid re-renders.
 */
export function UnsavedChangesProvider({
  children,
}: {
  children: React.ReactElement;
}) {
  const ref = useRef<UnsavedChanges>(initUnsavedChanges);
  const [state, setState] = useState<UnsavedChanges>(() => ({
    ...initUnsavedChanges,
    set: (next) =>
      setState((prev) => {
        let update: UnsavedChanges;
        if (next) {
          update = { ...prev, ...next };
        } else if (prev.callback || prev.exist || prev.ignore || prev.show) {
          update = { ...initUnsavedChanges, set: prev.set };
        } else {
          return prev;
        }
        ref.current = update;
        return update;
      }),
  }));

  const { callback, ignore, set } = state;
  useEffect(() => {
    if (callback && ignore) {
      callback();
      set(null);
    }
  }, [ignore]);

  return (
    <UnsavedChanges.Provider value={state}>
      <UnsavedChangesRef.Provider value={ref}>
        {children}
      </UnsavedChangesRef.Provider>
    </UnsavedChanges.Provider>
  );
}

/**
 * Check if the editor has unsaved changes by comparing its content
 * with the active translation. Show unsaved changes if they exist and
 * aren't explicitly ignored, or else execute callback function.
 */
export function useCheckUnsavedChanges() {
  const ref = useContext(UnsavedChangesRef);
  return useCallback(
    (callback: () => void) => {
      const { exist, ignore, set } = ref.current;
      if (exist && !ignore) {
        set({ callback, show: true });
      } else {
        callback();
      }
    },
    [ref],
  );
}

export function useSetUnsavedChanges() {
  const ref = useContext(UnsavedChangesRef);
  return useCallback(ref.current.set, [ref]);
}
