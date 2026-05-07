const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/i;

function repeated_character_run_length(value: string): number {
  let longestRun = 1;
  let currentRun = 1;
  for (let i = 1; i < value.length; i += 1) {
    if (value[i] === value[i - 1]) {
      currentRun += 1;
      longestRun = Math.max(longestRun, currentRun);
    } else {
      currentRun = 1;
    }
  }
  return longestRun;
}

export function is_valid_email(value: string): boolean {
  const normalized = value.trim().toLowerCase();
  if (!normalized || normalized.length > 254) {
    return false;
  }
  if (!EMAIL_REGEX.test(normalized)) {
    return false;
  }
  const [localPart, domain] = normalized.split('@');
  if (!localPart || !domain) {
    return false;
  }
  if (localPart.startsWith('.') || localPart.endsWith('.') || domain.includes('..')) {
    return false;
  }
  if (!domain.includes('.')) {
    return false;
  }
  return true;
}

interface TextQualityOptions {
  minLength?: number;
  minWords?: number;
}

export function validate_post_quality(value: string, options: TextQualityOptions = {}): string | null {
  const minLength = options.minLength ?? 8;
  const minWords = options.minWords ?? 2;
  const normalized = value.trim();
  if (!normalized) {
    return 'Post cannot be empty.';
  }
  if (normalized.length < minLength) {
    return `Post must be at least ${minLength} characters.`;
  }

  const words = normalized.split(/\s+/).filter(Boolean);
  if (words.length < minWords) {
    return `Post must include at least ${minWords} words.`;
  }

  const alphaMatches = normalized.match(/[a-z]/gi) ?? [];
  if (alphaMatches.length < Math.ceil(normalized.length * 0.3)) {
    return 'Post looks too noisy. Please add meaningful text.';
  }

  if (repeated_character_run_length(normalized) >= 6) {
    return 'Post has too many repeated characters.';
  }

  const compact = normalized.toLowerCase().replace(/\s+/g, '');
  const uniqueRatio = new Set(compact).size / compact.length;
  if (compact.length >= 16 && uniqueRatio < 0.2) {
    return 'Post appears low quality. Please add clearer details.';
  }

  return null;
}
