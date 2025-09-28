import { render, screen } from '@testing-library/react';
import HomePage from './page';

describe('HomePage', () => {
  it('renders the main heading', () => {
    render(<HomePage />);

    const heading = screen.getByRole('heading', {
      name: /AutoForge Nexus/i,
      level: 1,
    });

    expect(heading).toBeInTheDocument();
  });

  it('renders the description', () => {
    render(<HomePage />);

    const description = screen.getByText(
      /高品質なAIプロンプトの作成・最適化・管理を支援する統合プラットフォーム/i
    );

    expect(description).toBeInTheDocument();
  });

  it('renders the Get Started button', () => {
    render(<HomePage />);

    const getStartedButton = screen.getByRole('button', {
      name: /Get Started/i,
    });

    expect(getStartedButton).toBeInTheDocument();
  });

  it('renders the Learn More button', () => {
    render(<HomePage />);

    const learnMoreButton = screen.getByRole('button', {
      name: /Learn More/i,
    });

    expect(learnMoreButton).toBeInTheDocument();
  });

  it('displays version information', () => {
    render(<HomePage />);

    expect(screen.getByText(/Next.js 15.5.4/i)).toBeInTheDocument();
    expect(screen.getByText(/React 19.0.0/i)).toBeInTheDocument();
    expect(screen.getByText(/TypeScript 5.9.2/i)).toBeInTheDocument();
  });
});