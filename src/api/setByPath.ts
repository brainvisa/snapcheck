/**
 * Pure, immutable updater for a snap field addressed with the same dot syntax
 * as the backend PATCH endpoint:
 *   - "title"
 *   - "boards.0.description"          (numeric index)
 *   - "ratings.{id:sujet}.value"      (filter a list by attribute)
 *
 * Only the nodes along the path are cloned; siblings keep their identity so
 * TanStack's structural sharing keeps re-renders minimal.
 */
function parseSegment(seg: string): { kind: 'index'; index: number } | { kind: 'filter'; key: string; value: string } | { kind: 'key'; key: string } {
  if (/^\d+$/.test(seg)) return { kind: 'index', index: Number(seg) };
  if (seg.startsWith('{') && seg.endsWith('}')) {
    const [key, value] = seg.slice(1, -1).split(':', 2);
    return { kind: 'filter', key, value };
  }
  return { kind: 'key', key: seg };
}

export function setByPath<T>(root: T, fieldPath: string, value: unknown): T {
  const segments = fieldPath.split('.').map(parseSegment);

  const recurse = (node: any, depth: number): any => {
    const seg = segments[depth];
    const isLast = depth === segments.length - 1;

    if (seg.kind === 'index') {
      const arr = Array.isArray(node) ? [...node] : [];
      arr[seg.index] = isLast ? value : recurse(arr[seg.index], depth + 1);
      return arr;
    }
    if (seg.kind === 'filter') {
      const arr = Array.isArray(node) ? [...node] : [];
      const i = arr.findIndex((o) => o != null && String(o[seg.key]) === seg.value);
      if (i === -1) return arr;
      arr[i] = isLast ? value : recurse(arr[i], depth + 1);
      return arr;
    }
    const obj = { ...(node ?? {}) };
    obj[seg.key] = isLast ? value : recurse(obj[seg.key], depth + 1);
    return obj;
  };

  return recurse(root, 0);
}
