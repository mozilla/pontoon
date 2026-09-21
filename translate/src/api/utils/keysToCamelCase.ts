/**
 * Fields holding a message data model, in which every key is significant:
 * variable and option names are user data, and `attr` holds format metadata
 * such as the `fluent-fn` naming a Fluent function. Renaming any of them
 * corrupts the message.
 */
const OPAQUE_KEYS = new Set(['value', 'properties']);

export function keysToCamelCase(results: any): any {
  if (Array.isArray(results)) {
    return results.map(keysToCamelCase);
  } else if (results && typeof results === 'object') {
    const newObj: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(results)) {
      const camelKey = key.replace(/([-_][a-z])/gi, ($1) =>
        $1.toUpperCase().replace('-', '').replace('_', ''),
      );
      newObj[camelKey] = OPAQUE_KEYS.has(key) ? value : keysToCamelCase(value);
    }

    return newObj;
  }
  return results;
}
