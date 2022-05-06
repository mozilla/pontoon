export async function fetchL10n(locale: string): Promise<string> {
  const url = new URL(
    `/static/locale/${locale}/translate.ftl`,
    window.location.origin,
  );
  const response = await fetch(url.toString());
  return response.text();
}
