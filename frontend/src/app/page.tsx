export default function HomePage() {
  return (
    <main className="container mx-auto flex min-h-screen items-center justify-center">
      <div className="space-y-8 text-center">
        <h1 className="text-gradient text-6xl font-bold">AutoForge Nexus</h1>
        <p className="mx-auto max-w-2xl text-xl text-muted-foreground">
          高品質なAIプロンプトの作成・最適化・管理を支援する統合プラットフォーム
        </p>
        <div className="flex justify-center gap-4">
          <button className="text-primary-foreground rounded-lg bg-primary px-6 py-3 transition-opacity hover:opacity-90">
            Get Started
          </button>
          <button className="rounded-lg border border-border px-6 py-3 transition-colors hover:bg-muted">
            Learn More
          </button>
        </div>
        <div className="space-y-2 pt-8 text-sm text-muted-foreground">
          <p>Next.js 15.5.4 • React 19.0.0 • TypeScript 5.9.2</p>
          <p>Tailwind CSS 4.0.0 • shadcn/ui 3.3.1</p>
        </div>
      </div>
    </main>
  );
}
