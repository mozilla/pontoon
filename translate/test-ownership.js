/**
 * This file defines tests that have been migrated to
 * Vitest and must not be executed by Jest.
 *
 * Only add paths for tests that are migrated to vitest.
 *
 * This file is temporary and will be deleted after the
 * Vitest migration is complete.
 */
export const ignoreFromJest = [
  './src/modules/editor',
  './src/hooks/',
  './src/modules/comments/',
  './src/modules/entitydetails/',
  './src/modules/history/',
  './src/modules/machinery/',
  './src/modules/otherlocales/',
  './src/modules/resourceprogress/',
  './src/modules/teamcomments/',
  './src/modules/unsavedchanges/',
  './src/modules/user/',
  './src/modules/entities/',
];
export const includeInVitest = ignoreFromJest.map((x) => {
  return `${x}/**/*.test.*`;
});
