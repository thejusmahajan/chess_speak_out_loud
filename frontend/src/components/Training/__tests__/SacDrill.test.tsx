import { render, screen, fireEvent, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import SacDrill from '../SacDrill';
import * as trainingApi from '../../../api/training';

vi.mock('../../../api/training', () => ({
  startSacSession: vi.fn(),
  submitSacGuess: vi.fn(),
  getSacStats: vi.fn(),
}));

// Mock TrainingBoard to simulate user moves
vi.mock('../TrainingBoard', () => ({
  default: ({ onMove, interactive }: any) => (
    <div data-testid="mock-training-board" data-interactive={interactive ? 'true' : 'false'}>
      <button data-testid="move-btn-d4" onClick={() => onMove && onMove('d2d4', 'd4')}>
        Play d4
      </button>
      <button data-testid="move-btn-c3" onClick={() => onMove && onMove('c2c3', 'c3')}>
        Play c3
      </button>
    </div>
  ),
}));

describe('SacDrill UI Tests', () => {
  const mockPositions: trainingApi.SacPosition[] = [
    {
      id: 's-001-p020',
      fen: 'r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3',
    },
    {
      id: 's-003-p030',
      fen: 'r1bq1rk1/pp3pb1/2n3pp/2ppn3/5B2/2P1PN1P/PPBN1PP1/R2Q1RK1 w - - 0 12',
    },
  ];

  const mockStats: trainingApi.SacStats = {
    total: 8,
    correct: 4,
    acceptable: 2,
    accuracy: 0.5,
    recent_accuracy: 0.6,
  };

  beforeEach(() => {
    vi.resetAllMocks();
    (trainingApi.startSacSession as any).mockImplementation(() => Promise.resolve(mockPositions));
    (trainingApi.getSacStats as any).mockImplementation(() => Promise.resolve(mockStats));
  });

  it('1. Renders board and find-the-sac prompt for the first position', async () => {
    render(<SacDrill />);

    expect(screen.getByText(/Loading sacrifice drill session/i)).toBeInTheDocument();

    await act(async () => {
      await Promise.resolve();
    });

    expect(screen.getByTestId('mock-training-board')).toBeInTheDocument();
    expect(screen.getByText(/A strong sacrifice is available here — find it/i)).toBeInTheDocument();
    expect(screen.getByText(/Position 1 of 2/i)).toBeInTheDocument();
  });

  it('2. Making a move calls submitSacGuess and displays soundness reveal panel', async () => {
    const mockGuessResult: trainingApi.SacGuessResult = {
      correct: true,
      acceptable: false,
      sac_move: { uci: 'd2d4', san: 'd4', eval_cp: 15, complexity: 4.5 },
      safe_move: { san: 'Bb5', eval_cp: 30 },
      eval_loss_cp: 15,
      playable_candidates: [
        { uci: 'd2d4', complexity: 4.5, eval_cp: 15 },
        { uci: 'c2c3', complexity: 2.1, eval_cp: 25 },
      ],
    };

    (trainingApi.submitSacGuess as any).mockImplementation(() => Promise.resolve(mockGuessResult));

    render(<SacDrill />);

    await act(async () => {
      await Promise.resolve();
    });

    const moveBtn = screen.getByTestId('move-btn-d4');
    await act(async () => {
      fireEvent.click(moveBtn);
    });

    expect(trainingApi.submitSacGuess).toHaveBeenCalledWith('s-001-p020', 'd2d4');

    // Reveal panel check
    expect(screen.getByText(/HIT! You found the sacrifice!/i)).toBeInTheDocument();
    expect(screen.getByText(/concedes only/i)).toBeInTheDocument();
    expect(screen.getByText(/complexity 4.50/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Next Position/i })).toBeInTheDocument();
  });

  it('3. Completing session displays session summary accuracy and lifetime stats', async () => {
    const mockHitResult: trainingApi.SacGuessResult = {
      correct: true,
      acceptable: false,
      sac_move: { uci: 'd2d4', san: 'd4', eval_cp: 15, complexity: 4.5 },
      safe_move: { san: 'Bb5', eval_cp: 30 },
      eval_loss_cp: 15,
      playable_candidates: [],
    };

    (trainingApi.submitSacGuess as any).mockImplementation(() => Promise.resolve(mockHitResult));

    render(<SacDrill />);

    await act(async () => {
      await Promise.resolve();
    });

    // Position 1: Guess d4
    await act(async () => {
      fireEvent.click(screen.getByTestId('move-btn-d4'));
    });

    // Next Position -> Position 2
    const nextBtn = screen.getByRole('button', { name: /Next Position/i });
    await act(async () => {
      fireEvent.click(nextBtn);
    });

    // Position 2: Guess d4
    await act(async () => {
      fireEvent.click(screen.getByTestId('move-btn-d4'));
    });

    // Finish Session button
    const finishBtn = screen.getByRole('button', { name: /Finish Session/i });
    await act(async () => {
      fireEvent.click(finishBtn);
    });

    expect(screen.getByText(/Session Complete!/i)).toBeInTheDocument();
    expect(screen.getByText(/2 \/ 2/i)).toBeInTheDocument();
    expect(screen.getByText(/100.0%/i)).toBeInTheDocument();
    expect(screen.getByText(/Lifetime Sacrifice Stats/i)).toBeInTheDocument();
    expect(screen.getByText(/50.0%/i)).toBeInTheDocument();
  });
});
