export function keysToCamelCase(results: any): any {
  if (Array.isArray(results)) {
    return results.map(keysToCamelCase);
  } else if (results && typeof results === 'object') {
    const newObj: Record<string, unknown> = {};
    for (let [key, value] of Object.entries(results)) {
      const camelKey = key.replace(/([-_][a-z])/gi, ($1) =>
        $1.toUpperCase().replace('-', '').replace('_', ''),
      );
      newObj[camelKey] = keysToCamelCase(value);
    }

    return newObj;
  }
  return results;
}
