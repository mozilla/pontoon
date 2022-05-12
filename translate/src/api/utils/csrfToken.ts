export function getCSRFToken(): string {
  const root = document.getElementById('root');
  return root?.dataset.csrfToken ?? '';
}
