/**
 * This file defines tests that have been migrated to
 * Vitest and must not be executed by Jest.
 *
 * Only add paths for tests that are migrated to vitest.
 *
 * This file is temporary and will be deleted after the
 * Vitest migration is complete.
 */
export const ignoreFromVitest = [
  'src/modules/entitieslist/components/EntitiesList.test.js',
  'src/utils/message/getEmptyMessage.test.js',
];
export const includeInJest = ignoreFromVitest.map((x) => `<rootDir>/${x}`);
