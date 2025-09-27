/**
 * Unit tests for enhanced MMM components with real data features.
 * Tests the new performance indicators and insights functionality.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import {
  SimpleContributionChart,
  SimpleMMInsights,
} from "@/components/mmm/simple-charts";

// Mock the auth hook
const mockUseAuth = vi.fn();
vi.mock("@/lib/auth", () => ({
  useAuth: () => mockUseAuth(),
}));

// Mock the MMM data hook
const mockUseMMMData = vi.fn();
vi.mock("@/hooks/use-mmm-data", () => ({
  useMMMData: () => mockUseMMMData(),
}));

describe("Enhanced MMM Components", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Default auth state
    mockUseAuth.mockReturnValue({
      token: "mock-token",
      user: { id: 1, email: "test@example.com" },
    });
  });

  describe("SimpleContributionChart with Performance Indicators", () => {
    it("renders loading state correctly", () => {
      mockUseMMMData.mockReturnValue({
        getChannelSummary: vi.fn(),
        getResponseCurves: vi.fn(),
        loading: true,
        error: null,
      });

      render(<SimpleContributionChart />);

      expect(
        screen.getByText("Loading contribution data..."),
      ).toBeInTheDocument();
      expect(screen.getByRole("status")).toBeInTheDocument(); // Loading spinner
    });

    it("renders error state correctly", () => {
      mockUseMMMData.mockReturnValue({
        getChannelSummary: vi.fn(),
        getResponseCurves: vi.fn(),
        loading: false,
        error: "Failed to load data",
      });

      render(<SimpleContributionChart />);

      expect(screen.getByText("Error loading data")).toBeInTheDocument();
      expect(screen.getByText("Failed to load data")).toBeInTheDocument();
    });

    it("renders enhanced contribution chart with performance indicators", async () => {
      const mockChannelSummary = {
        Channel0: { total_contribution: 1000000 },
        Channel1: { total_contribution: 800000 },
        Channel2: { total_contribution: 600000 },
      };

      const mockResponseCurves = {
        curves: {
          Channel0: {
            efficiency: 1.58,
            saturation_point: 30000,
            adstock_rate: 0.77,
          },
          Channel1: {
            efficiency: 0.92,
            saturation_point: 35000,
            adstock_rate: 0.64,
          },
          Channel2: {
            efficiency: 1.43,
            saturation_point: 40000,
            adstock_rate: 0.4,
          },
        },
      };

      const mockGetChannelSummary = vi
        .fn()
        .mockResolvedValue(mockChannelSummary);
      const mockGetResponseCurves = vi
        .fn()
        .mockResolvedValue(mockResponseCurves);

      mockUseMMMData.mockReturnValue({
        getChannelSummary: mockGetChannelSummary,
        getResponseCurves: mockGetResponseCurves,
        loading: false,
        error: null,
      });

      render(<SimpleContributionChart />);

      await waitFor(() => {
        expect(
          screen.getByText("Channel Performance & Efficiency"),
        ).toBeInTheDocument();
      });

      // Should show total contribution
      expect(screen.getByText("2,400,000")).toBeInTheDocument(); // Total
      expect(screen.getByText("Total Contribution")).toBeInTheDocument();

      // Should show average ROI
      expect(screen.getByText("Avg ROI")).toBeInTheDocument();

      // Should show performance insight
      expect(screen.getByText("Performance Insight:")).toBeInTheDocument();
    });

    it("displays performance indicators correctly", async () => {
      const mockChannelSummary = {
        Channel0: { total_contribution: 1000000 },
        Channel1: { total_contribution: 500000 },
      };

      const mockResponseCurves = {
        curves: {
          Channel0: {
            efficiency: 1.58,
            saturation_point: 30000,
            adstock_rate: 0.77,
          }, // High performer
          Channel1: {
            efficiency: 0.75,
            saturation_point: 35000,
            adstock_rate: 0.64,
          }, // Underperformer
        },
      };

      const mockGetChannelSummary = vi
        .fn()
        .mockResolvedValue(mockChannelSummary);
      const mockGetResponseCurves = vi
        .fn()
        .mockResolvedValue(mockResponseCurves);

      mockUseMMMData.mockReturnValue({
        getChannelSummary: mockGetChannelSummary,
        getResponseCurves: mockGetResponseCurves,
        loading: false,
        error: null,
      });

      render(<SimpleContributionChart />);

      await waitFor(() => {
        // Should show ROI values
        expect(screen.getByText("ROI: 1.58")).toBeInTheDocument();
        expect(screen.getByText("ROI: 0.75")).toBeInTheDocument();
      });
    });

    it("handles empty data gracefully", async () => {
      const mockGetChannelSummary = vi.fn().mockResolvedValue({});
      const mockGetResponseCurves = vi.fn().mockResolvedValue({ curves: {} });

      mockUseMMMData.mockReturnValue({
        getChannelSummary: mockGetChannelSummary,
        getResponseCurves: mockGetResponseCurves,
        loading: false,
        error: null,
      });

      render(<SimpleContributionChart />);

      await waitFor(() => {
        expect(
          screen.getByText("Channel Performance & Efficiency"),
        ).toBeInTheDocument();
      });

      // Should show zero values
      expect(screen.getByText("0")).toBeInTheDocument(); // Total contribution
      expect(screen.getByText("0.00")).toBeInTheDocument(); // Avg ROI
    });
  });

  describe("SimpleMMInsights with Enhanced Recommendations", () => {
    it("renders loading state correctly", () => {
      mockUseMMMData.mockReturnValue({
        getChannelSummary: vi.fn(),
        getMMMInfo: vi.fn(),
        getResponseCurves: vi.fn(),
        loading: true,
        error: null,
      });

      render(<SimpleMMInsights />);

      expect(
        screen.getByText("Generating recommendations..."),
      ).toBeInTheDocument();
    });

    it("renders error state correctly", () => {
      mockUseMMMData.mockReturnValue({
        getChannelSummary: vi.fn(),
        getMMMInfo: vi.fn(),
        getResponseCurves: vi.fn(),
        loading: false,
        error: "Failed to generate insights",
      });

      render(<SimpleMMInsights />);

      expect(screen.getByText("Error loading insights")).toBeInTheDocument();
      expect(
        screen.getByText("Failed to generate insights"),
      ).toBeInTheDocument();
    });

    it("generates enhanced insights with real data", async () => {
      const mockChannelSummary = {
        Channel0: { efficiency: 1.58 }, // Top performer
        Channel1: { efficiency: 0.75 }, // Underperformer
      };

      const mockMMMInfo = {
        model_type: "Google Meridian",
        data_source: "real_model",
        total_weeks: 156,
        channels: ["Channel0", "Channel1"],
      };

      const mockResponseCurves = {
        curves: {
          Channel0: {
            efficiency: 1.58,
            saturation_point: 30000,
            adstock_rate: 0.77,
          },
          Channel1: {
            efficiency: 0.75,
            saturation_point: 35000,
            adstock_rate: 0.64,
          },
        },
      };

      const mockGetChannelSummary = vi
        .fn()
        .mockResolvedValue(mockChannelSummary);
      const mockGetMMMInfo = vi.fn().mockResolvedValue(mockMMMInfo);
      const mockGetResponseCurves = vi
        .fn()
        .mockResolvedValue(mockResponseCurves);

      mockUseMMMData.mockReturnValue({
        getChannelSummary: mockGetChannelSummary,
        getMMMInfo: mockGetMMMInfo,
        getResponseCurves: mockGetResponseCurves,
        loading: false,
        error: null,
      });

      render(<SimpleMMInsights />);

      await waitFor(() => {
        expect(screen.getByText("MMM Insights")).toBeInTheDocument();
      });

      // Should show model information
      expect(screen.getByText(/Google Meridian/)).toBeInTheDocument();
      expect(screen.getByText(/real_model/)).toBeInTheDocument();

      // Should show key insights
      expect(screen.getByText("Key Insights")).toBeInTheDocument();

      // Should identify top performer
      expect(screen.getByText(/Channel0.*top performer/)).toBeInTheDocument();

      // Should identify underperformer
      expect(screen.getByText(/Channel1.*underperforming/)).toBeInTheDocument();
    });

    it("generates budget optimization recommendations", async () => {
      const mockChannelSummary = {
        Channel0: { efficiency: 1.58 },
        Channel1: { efficiency: 0.75 },
      };

      const mockMMMInfo = {
        total_weeks: 156,
        channels: ["Channel0", "Channel1"],
      };

      const mockResponseCurves = {
        curves: {
          Channel0: { efficiency: 1.58, saturation_point: 30000 },
          Channel1: { efficiency: 0.75, saturation_point: 35000 },
        },
      };

      const mockGetChannelSummary = vi
        .fn()
        .mockResolvedValue(mockChannelSummary);
      const mockGetMMMInfo = vi.fn().mockResolvedValue(mockMMMInfo);
      const mockGetResponseCurves = vi
        .fn()
        .mockResolvedValue(mockResponseCurves);

      mockUseMMMData.mockReturnValue({
        getChannelSummary: mockGetChannelSummary,
        getMMMInfo: mockGetMMMInfo,
        getResponseCurves: mockGetResponseCurves,
        loading: false,
        error: null,
      });

      render(<SimpleMMInsights />);

      await waitFor(() => {
        // Should show budget optimization opportunity
        expect(
          screen.getByText(/Budget Optimization Opportunity/),
        ).toBeInTheDocument();
        expect(
          screen.getByText(/Shifting budget from.*Channel1.*to.*Channel0/),
        ).toBeInTheDocument();
      });
    });

    it("shows portfolio performance summary", async () => {
      const mockChannelSummary = {
        Channel0: { efficiency: 1.58 },
        Channel1: { efficiency: 0.92 },
        Channel2: { efficiency: 1.25 },
      };

      const mockMMMInfo = {
        total_weeks: 156,
        channels: ["Channel0", "Channel1", "Channel2"],
      };

      const mockResponseCurves = {
        curves: {
          Channel0: { efficiency: 1.58, saturation_point: 30000 },
          Channel1: { efficiency: 0.92, saturation_point: 35000 },
          Channel2: { efficiency: 1.25, saturation_point: 40000 },
        },
      };

      const mockGetChannelSummary = vi
        .fn()
        .mockResolvedValue(mockChannelSummary);
      const mockGetMMMInfo = vi.fn().mockResolvedValue(mockMMMInfo);
      const mockGetResponseCurves = vi
        .fn()
        .mockResolvedValue(mockResponseCurves);

      mockUseMMMData.mockReturnValue({
        getChannelSummary: mockGetChannelSummary,
        getMMMInfo: mockGetMMMInfo,
        getResponseCurves: mockGetResponseCurves,
        loading: false,
        error: null,
      });

      render(<SimpleMMInsights />);

      await waitFor(() => {
        // Should show portfolio performance
        expect(screen.getByText(/Portfolio Performance/)).toBeInTheDocument();
        expect(screen.getByText(/Average ROI: 1.25/)).toBeInTheDocument(); // (1.58 + 0.92 + 1.25) / 3
        expect(screen.getByText(/Best: 1.58/)).toBeInTheDocument();
        expect(screen.getByText(/Worst: 0.92/)).toBeInTheDocument();
      });
    });

    it("handles saturation alerts", async () => {
      const mockChannelSummary = {
        Channel0: { efficiency: 1.58 },
      };

      const mockMMMInfo = {
        total_weeks: 156,
        channels: ["Channel0"],
      };

      const mockResponseCurves = {
        curves: {
          Channel0: { efficiency: 1.58, saturation_point: 25000 }, // Low saturation point
        },
      };

      const mockGetChannelSummary = vi
        .fn()
        .mockResolvedValue(mockChannelSummary);
      const mockGetMMMInfo = vi.fn().mockResolvedValue(mockMMMInfo);
      const mockGetResponseCurves = vi
        .fn()
        .mockResolvedValue(mockResponseCurves);

      mockUseMMMData.mockReturnValue({
        getChannelSummary: mockGetChannelSummary,
        getMMMInfo: mockGetMMMInfo,
        getResponseCurves: mockGetResponseCurves,
        loading: false,
        error: null,
      });

      render(<SimpleMMInsights />);

      await waitFor(() => {
        // Should show saturation alert for low saturation point
        expect(screen.getByText(/Saturation Alert/)).toBeInTheDocument();
        expect(
          screen.getByText(/Channel0.*low saturation/),
        ).toBeInTheDocument();
      });
    });
  });

  describe("Component Integration", () => {
    it("handles authentication state changes", () => {
      // Test without token
      mockUseAuth.mockReturnValue({
        token: null,
        user: null,
      });

      mockUseMMMData.mockReturnValue({
        getChannelSummary: vi.fn(),
        getResponseCurves: vi.fn(),
        loading: false,
        error: null,
      });

      const { rerender } = render(<SimpleContributionChart />);

      // Should not fetch data without token
      expect(
        screen.getByText("Channel Performance & Efficiency"),
      ).toBeInTheDocument();

      // Add token
      mockUseAuth.mockReturnValue({
        token: "mock-token",
        user: { id: 1, email: "test@example.com" },
      });

      rerender(<SimpleContributionChart />);

      // Should now attempt to fetch data
      expect(mockUseMMMData().getChannelSummary).toHaveBeenCalled();
    });

    it("handles API errors gracefully", async () => {
      const mockGetChannelSummary = vi
        .fn()
        .mockRejectedValue(new Error("API Error"));
      const mockGetResponseCurves = vi
        .fn()
        .mockRejectedValue(new Error("API Error"));

      mockUseMMMData.mockReturnValue({
        getChannelSummary: mockGetChannelSummary,
        getResponseCurves: mockGetResponseCurves,
        loading: false,
        error: null,
      });

      render(<SimpleContributionChart />);

      // Should handle errors gracefully without crashing
      await waitFor(() => {
        expect(
          screen.getByText("Channel Performance & Efficiency"),
        ).toBeInTheDocument();
      });
    });
  });
});
