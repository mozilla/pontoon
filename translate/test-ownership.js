/**
 * This file defines tests that have been migrated to
 * Vitest and must not be executed by Jest.
 *
 * Only add paths for tests that are migrated to vitest.
 *
 * This file is temporary and will be deleted after the
 * Vitest migration is complete.
 */
export const ingoreFromVitest = [
  'src/modules/interactivetour/components/InteractiveTour.test.js',
  'src/modules/entitieslist/components/EntitiesList.test.js',
];
export const includeInJest = ingoreFromVitest.map((x) => `<rootDir>/${x}`);
