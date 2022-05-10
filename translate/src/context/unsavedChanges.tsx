import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';

export interface UnsavedChanges {
  /** Call with `null` to reset all fields */
  readonly set: (next: Partial<UnsavedChanges> | null) => void;
  readonly callback: (() => void) | null;
  readonly exist: boolean;
  readonly ignore: boolean;
  readonly show: boolean;
}

const emptyUnsavedChanges: UnsavedChanges = {
  callback: null,
  exist: false,
  ignore: false,
  show: false,
  set: () => {},
};

export const UnsavedChanges = createContext(emptyUnsavedChanges);

const UnsavedChangesRef = createContext<React.MutableRefObject<UnsavedChanges>>(
  { current: emptyUnsavedChanges },
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
  const ref = useRef<UnsavedChanges>(emptyUnsavedChanges);
  const [state, setState] = useState<UnsavedChanges>(() => ({
    ...emptyUnsavedChanges,
    set: (next) =>
      setState((prev) => {
        const update = next
          ? { ...prev, ...next }
          : { ...emptyUnsavedChanges, set: prev.set };
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
