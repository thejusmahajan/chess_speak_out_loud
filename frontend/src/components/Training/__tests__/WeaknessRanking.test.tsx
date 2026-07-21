import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import ProfileReport from '../ProfileReport';
import * as trainingApi from '../../../api/training';

vi.mock('../../../api/training', () => ({
  getWeaknessRanking: vi.fn(),
}));

describe('WeaknessRanking UI Tests', () => {
  const dummyProfile = {
    player_name: 'TestPlayer',
    games_analyzed: 10,
    aggregates: {
      by_opening: { C61: { moves: 120, blind_rate: 0.40 } },
    },
  };

  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('5. Loading state renders while the fetch promise is pending', async () => {
    let resolvePromise: (val: any) => void = () => {};
    const pendingPromise = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    (trainingApi.getWeaknessRanking as any).mockReturnValue(pendingPromise);

    render(
      <ProfileReport
        profile={dummyProfile}
        onFindingClick={vi.fn()}
        onGenerateDrills={vi.fn()}
      />
    );

    expect(screen.getByTestId('ranking-loading')).toBeInTheDocument();
    expect(screen.getByText(/Analyzing opening performance/i)).toBeInTheDocument();

    // Clean up pending promise
    resolvePromise({ ranking: [] });
    await waitFor(() => {
      expect(screen.queryByTestId('ranking-loading')).not.toBeInTheDocument();
    });
  });

  it('6. Renders ranked items in order with weakness and strength indicators', async () => {
    const mockRanking = [
      { dim: 'C61', value: 0.40, count: 120, ref_value: 0.11, grade: -2.9, importance: 31.7, kind: 'weakness' as const },
      { dim: 'B12', value: 0.35, count: 80, ref_value: 0.11, grade: -2.1, importance: 18.8, kind: 'weakness' as const },
      { dim: 'E60', value: 0.05, count: 90, ref_value: 0.15, grade: 1.2, importance: 11.4, kind: 'strength' as const },
    ];
    (trainingApi.getWeaknessRanking as any).mockResolvedValue({ ranking: mockRanking });

    render(
      <ProfileReport
        profile={dummyProfile}
        onFindingClick={vi.fn()}
        onGenerateDrills={vi.fn()}
      />
    );

    await waitFor(() => {
      expect(screen.getByTestId('ranking-list')).toBeInTheDocument();
    });

    const itemC61 = screen.getByTestId('ranking-item-C61');
    const itemB12 = screen.getByTestId('ranking-item-B12');
    const itemE60 = screen.getByTestId('ranking-item-E60');

    expect(itemC61).toHaveClass('weakness');
    expect(itemB12).toHaveClass('weakness');
    expect(itemE60).toHaveClass('strength');

    // Verify ordering in DOM: C61 before B12 before E60
    const items = screen.getAllByTestId(/^ranking-item-/);
    expect(items[0]).toHaveTextContent('C61');
    expect(items[1]).toHaveTextContent('B12');
    expect(items[2]).toHaveTextContent('E60');
  });

  it('7. Formatting — value 0.40 renders as 40.0% and count 120 as games; ref_value/importance not raw dumped', async () => {
    const mockRanking = [
      { dim: 'C61', value: 0.40, count: 120, ref_value: 0.112345, grade: -2.9, importance: 31.789, kind: 'weakness' as const },
    ];
    (trainingApi.getWeaknessRanking as any).mockResolvedValue({ ranking: mockRanking });

    render(
      <ProfileReport
        profile={dummyProfile}
        onFindingClick={vi.fn()}
        onGenerateDrills={vi.fn()}
      />
    );

    await waitFor(() => {
      expect(screen.getByTestId('ranking-item-C61')).toBeInTheDocument();
    });

    const item = screen.getByTestId('ranking-item-C61');
    expect(item).toHaveTextContent('40.0% blind');
    expect(item).toHaveTextContent('120 games');

    // Verify ref_value and importance are not dumped raw as noise in the text
    expect(item.textContent).not.toContain('0.112345');
    expect(item.textContent).not.toContain('31.789');
  });

  it('8. Empty ranking ({ ranking: [] }) renders friendly message and profile remains intact', async () => {
    (trainingApi.getWeaknessRanking as any).mockResolvedValue({ ranking: [] });

    render(
      <ProfileReport
        profile={dummyProfile}
        onFindingClick={vi.fn()}
        onGenerateDrills={vi.fn()}
      />
    );

    await waitFor(() => {
      expect(screen.getByTestId('ranking-empty')).toBeInTheDocument();
    });

    expect(screen.getByText(/Not enough games analyzed yet to rank your openings/i)).toBeInTheDocument();
    // Rest of profile intact
    expect(screen.getByRole('heading', { name: /Weakness Profile/i })).toBeInTheDocument();
  });

  it('9. Fetch error renders graceful inline message and profile remains intact', async () => {
    (trainingApi.getWeaknessRanking as any).mockRejectedValue(new Error('Network error fetching ranking'));

    render(
      <ProfileReport
        profile={dummyProfile}
        onFindingClick={vi.fn()}
        onGenerateDrills={vi.fn()}
      />
    );

    await waitFor(() => {
      expect(screen.getByTestId('ranking-error')).toBeInTheDocument();
    });

    expect(screen.getByText(/Network error fetching ranking/i)).toBeInTheDocument();
    // Rest of profile intact
    expect(screen.getByRole('heading', { name: /Weakness Profile/i })).toBeInTheDocument();
  });
});
