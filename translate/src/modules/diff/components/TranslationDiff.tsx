import { diff_match_patch, DIFF_INSERT, DIFF_DELETE } from 'diff-match-patch';
import React from 'react';

import './TranslationDiff.css';

const dmp = new diff_match_patch();

type Props = {
  base: string;
  target: string;
};

/**
 * Render diff between the base and the target string.
 *
 * Unchanged slices are wrapped in <span>.
 * Added slices are wrapped in <ins>.
 * Removed slices are wrapped in <del>.
 */
export function TranslationDiff({ base, target }: Props): React.ReactElement {
  const diff = dmp.diff_main(base, target);
  dmp.diff_cleanupSemantic(diff);
  dmp.diff_cleanupEfficiency(diff);

  return (
    <>
      {diff.map(([type, slice], index) => {
        switch (type) {
          case DIFF_INSERT:
            return <ins key={index}>{slice}</ins>;

          case DIFF_DELETE:
            return <del key={index}>{slice}</del>;

          default:
            return slice;
        }
      })}
    </>
  );
}
