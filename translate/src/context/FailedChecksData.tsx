import React, { createContext, useEffect, useState } from 'react';
import type { ApiFailedChecks, EntityTranslation } from '~/api/translation';

// Not using Readonly<{ ... }> due to https://github.com/microsoft/TypeScript/issues/48636
export type FailedChecksData = {
  readonly errors: readonly string[];
  readonly warnings: readonly string[];

  /**
   * A source of failed checks (errors and warnings). Possible values:
   *   - `'stored'`: failed checks of the translation stored in the DB
   *   - `'submitted'`: failed checks of the submitted translation
   *   - `number` (translationId): failed checks of the approved translation
   *   - `null`: no failed checks are displayed (default)
   */
  readonly source: 'stored' | 'submitted' | number | null;

  resetFailedChecks(): void;
  setFailedChecks(
    data: ApiFailedChecks,
    source: 'stored' | 'submitted' | number,
  ): void;
};

const initFailedChecks: FailedChecksData = {
  errors: [],
  warnings: [],
  source: null,
  resetFailedChecks: () => {},
  setFailedChecks: () => {},
};

export const FailedChecksData = createContext(initFailedChecks);

export function FailedChecksProvider({
  children,
  translation,
}: {
  children: React.ReactElement;
  translation: EntityTranslation | undefined;
}) {
  const [state, setState] = useState<FailedChecksData>(() => ({
    ...initFailedChecks,

    resetFailedChecks() {
      setState((prev) =>
        prev.source
          ? { ...prev, errors: [], warnings: [], source: null }
          : prev,
      );
    },

    setFailedChecks(data, source) {
      const errors = data.clErrors.concat(data.pErrors);
      const warnings = data.clWarnings.concat(
        data.pndbWarnings,
        data.ttWarnings,
      );
      setState((prev) => ({ ...prev, errors, warnings, source }));
    },
  }));

  useEffect(() => {
    // Only show failed checks for active translations that are approved,
    // pretranslated or fuzzy, i.e. when their status icon is colored as
    // error/warning in the string list
    if (translation) {
      const { approved, errors, fuzzy, pretranslated, warnings } = translation;
      if (
        (errors.length || warnings.length) &&
        (approved || pretranslated || fuzzy)
      ) {
        setState((prev) => ({ ...prev, errors, warnings, source: 'stored' }));
        return;
      }
    }
    state.resetFailedChecks();
  }, [translation]);

  return (
    <FailedChecksData.Provider value={state}>
      {children}
    </FailedChecksData.Provider>
  );
}
