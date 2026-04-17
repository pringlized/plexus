export const theme = $state({ mode: 'dark' as 'dark' | 'light' });

export function initTheme() {
  if (typeof window === 'undefined') return;
  const stored = localStorage.getItem('plexus-theme');
  theme.mode = stored === 'light' ? 'light' : 'dark';
  document.documentElement.classList.toggle('dark', theme.mode === 'dark');
}

export function toggleTheme() {
  theme.mode = theme.mode === 'dark' ? 'light' : 'dark';
  if (typeof window !== 'undefined') {
    localStorage.setItem('plexus-theme', theme.mode);
    document.documentElement.classList.toggle('dark', theme.mode === 'dark');
  }
}
