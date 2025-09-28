export default function HomePage() {
  return (
    <main className="container mx-auto min-h-screen flex items-center justify-center">
      <div className="text-center space-y-8">
        <h1 className="text-6xl font-bold text-gradient">
          AutoForge Nexus
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          高品質なAIプロンプトの作成・最適化・管理を支援する統合プラットフォーム
        </p>
        <div className="flex gap-4 justify-center">
          <button className="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity">
            Get Started
          </button>
          <button className="px-6 py-3 border border-border rounded-lg hover:bg-muted transition-colors">
            Learn More
          </button>
        </div>
        <div className="pt-8 space-y-2 text-sm text-muted-foreground">
          <p>Next.js 15.5.4 • React 19.0.0 • TypeScript 5.9.2</p>
          <p>Tailwind CSS 4.0.0 • shadcn/ui 3.3.1</p>
        </div>
      </div>
    </main>
  );
}