export function renderRiskBanner(score: number): string {
  const tone = score >= 0.72 ? "review" : "normal";
  return `<aside data-tone="${tone}">Evidence risk: ${score.toFixed(2)}</aside>`;
}

export function renderFooter(build: string): string {
  return `<footer>Example build ${build}</footer>`;
}
