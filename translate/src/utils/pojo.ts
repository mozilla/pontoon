/**
 * Deeply compare two POJO values.
 *
 * Supports primitives, arrays, Maps, Sets, and plain objects.
 * For objects, only enumerable properties are considered,
 * their order does not matter, and `undefined` as a value
 * is considered equal to a missing property.
 * Functions are compared by identity.
 */
export function pojoEquals<T>(a: T, b: T): boolean {
  if (a === b) {
    return true;
  }

  if (typeof a !== 'object' || typeof b !== 'object' || !a || !b) {
    return false;
  }

  if (Array.isArray(a)) {
    if (!Array.isArray(b) || a.length !== b.length) {
      return false;
    }
    for (let i = 0; i < a.length; ++i) {
      if (!pojoEquals(a[i], b[i])) {
        return false;
      }
    }
    return true;
  }
  if (Array.isArray(b)) {
    return false;
  }

  if (a instanceof Map) {
    if (!(b instanceof Map) || a.size !== b.size) {
      return false;
    }
    for (const [ak, av] of a) {
      if (!b.has(ak) || !pojoEquals(av, b.get(ak))) {
        return false;
      }
    }
    return true;
  }
  if (b instanceof Map) {
    return false;
  }

  if (a instanceof Set) {
    if (!(b instanceof Set) || a.size !== b.size) {
      return false;
    }
    for (const value of a) {
      if (!b.has(value)) {
        return false;
      }
    }
    return true;
  }
  if (b instanceof Set) {
    return false;
  }

  const keys = new Set();
  for (const [key, av] of Object.entries(a)) {
    if (av !== undefined) {
      const bv = (b as Record<string, unknown>)[key];
      if (!pojoEquals(av, bv)) {
        return false;
      }
      keys.add(key);
    }
  }
  for (const [key, bv] of Object.entries(b)) {
    if (bv !== undefined && !keys.has(key)) {
      return false;
    }
  }
  return true;
}
