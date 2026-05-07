const TIMEZONE_SUFFIX_PATTERN = /(Z|[+-]\d{2}:\d{2})$/i;

export function normalize_api_datetime(value: string): string {
  const trimmed = value.trim();
  if (!trimmed) {
    return trimmed;
  }
  return TIMEZONE_SUFFIX_PATTERN.test(trimmed) ? trimmed : `${trimmed}Z`;
}

export function parse_api_datetime(value: string | null | undefined): Date | null {
  if (!value) {
    return null;
  }
  const normalized = normalize_api_datetime(value);
  if (!normalized) {
    return null;
  }
  const parsed = new Date(normalized);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}
