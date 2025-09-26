// Meridian Model Data Processing
// Based on analysis of saved_mmm.pkl structure

export interface MediaChannel {
  name: string;
  spend: number[];
  contribution: number[];
  roi: number;
  mroi: number;
  reach?: number[];
  frequency?: number[];
}

export interface KPIMetrics {
  revenue: number[];
  revenue_per_kpi: number[];
  total_spend: number[];
  total_outcome: number[];
  competitor_sales_control: number[];
  roi_m: number[];
  roi_rf: number[];
  mroi_m: number[];
  mroi_rf: number[];
}

export interface ResponseCurve {
  channel: string;
  spend: number[];
  outcome: number[];
  curve_type: 'saturating' | 'diminishing' | 'linear';
}

export interface MeridianModelData {
  channels: MediaChannel[];
  kpi: KPIMetrics;
  response_curves: ResponseCurve[];
  time_range: {
    start: string;
    end: string;
    frequency: 'weekly' | 'daily' | 'monthly';
  };
  model_info: {
    total_data_points: number;
    media_channels_count: number;
    model_type: string;
  };
}

// Mock data structure based on actual model analysis
export const mockMeridianData: MeridianModelData = {
  time_range: {
    start: '2021-01-25',
    end: '2024-01-15',
    frequency: 'weekly'
  },
  model_info: {
    total_data_points: 156,
    media_channels_count: 8,
    model_type: 'Media Mix Model'
  },
  channels: [
    {
      name: 'TV',
      spend: [100000, 120000, 110000, 130000, 125000, 140000, 135000, 150000, 145000, 160000],
      contribution: [45000, 52000, 48000, 55000, 53000, 58000, 56000, 61000, 59000, 64000],
      roi: 0.45,
      mroi: 0.42,
      reach: [8500000, 9200000, 8800000, 9500000, 9300000, 9800000, 9600000, 10100000, 9900000, 10400000]
    },
    {
      name: 'Digital Search',
      spend: [50000, 55000, 52000, 58000, 57000, 62000, 60000, 65000, 63000, 68000],
      contribution: [35000, 38000, 36000, 40000, 39000, 42000, 41000, 44000, 43000, 46000],
      roi: 0.70,
      mroi: 0.68,
      reach: [1200000, 1350000, 1280000, 1420000, 1390000, 1480000, 1450000, 1550000, 1520000, 1620000]
    },
    {
      name: 'Social Media',
      spend: [30000, 32000, 31000, 34000, 33000, 36000, 35000, 38000, 37000, 40000],
      contribution: [18000, 19500, 18800, 21000, 20500, 22500, 21800, 24000, 23500, 25500],
      roi: 0.60,
      mroi: 0.58,
      reach: [2100000, 2280000, 2220000, 2400000, 2340000, 2520000, 2460000, 2640000, 2580000, 2760000]
    },
    {
      name: 'Display',
      spend: [25000, 27000, 26000, 28000, 27500, 29000, 28500, 30000, 29500, 31000],
      contribution: [12000, 13000, 12500, 13500, 13200, 14000, 13700, 14500, 14200, 15000],
      roi: 0.48,
      mroi: 0.46,
      reach: [4500000, 4800000, 4650000, 4950000, 4870000, 5100000, 5020000, 5250000, 5170000, 5400000]
    },
    {
      name: 'YouTube',
      spend: [20000, 22000, 21000, 23000, 22500, 24000, 23500, 25000, 24500, 26000],
      contribution: [11000, 11800, 11500, 12500, 12200, 13000, 12700, 13500, 13200, 14000],
      roi: 0.55,
      mroi: 0.53,
      reach: [1800000, 1950000, 1870000, 2020000, 1980000, 2100000, 2060000, 2180000, 2140000, 2260000]
    },
    {
      name: 'Organic Social',
      spend: [8000, 8500, 8200, 8800, 8600, 9000, 8800, 9200, 9000, 9400],
      contribution: [4000, 4200, 4100, 4400, 4300, 4500, 4400, 4600, 4500, 4700],
      roi: 0.50,
      mroi: 0.48,
      reach: [3200000, 3400000, 3280000, 3520000, 3440000, 3600000, 3520000, 3680000, 3600000, 3760000]
    },
    {
      name: 'Radio',
      spend: [15000, 16000, 15500, 16500, 16200, 17000, 16700, 17500, 17200, 18000],
      contribution: [6000, 6400, 6200, 6600, 6480, 6800, 6680, 7000, 6880, 7200],
      roi: 0.40,
      mroi: 0.38,
      reach: [3800000, 4050000, 3920000, 4180000, 4100000, 4300000, 4220000, 4420000, 4340000, 4550000]
    },
    {
      name: 'Print',
      spend: [5000, 5200, 5100, 5300, 5250, 5400, 5350, 5450, 5400, 5500],
      contribution: [1500, 1560, 1530, 1590, 1575, 1620, 1605, 1635, 1620, 1650],
      roi: 0.30,
      mroi: 0.28,
      reach: [1200000, 1240000, 1220000, 1260000, 1250000, 1280000, 1270000, 1300000, 1290000, 1320000]
    }
  ],
  kpi: {
    revenue: [180000, 195000, 188000, 205000, 200000, 215000, 210000, 225000, 220000, 235000],
    revenue_per_kpi: [1800, 1950, 1880, 2050, 2000, 2150, 2100, 2250, 2200, 2350],
    total_spend: [250000, 268000, 258000, 278000, 273000, 288000, 283000, 298000, 293000, 308000],
    total_outcome: [135000, 146000, 141000, 153000, 149000, 158000, 155000, 164000, 161000, 170000],
    competitor_sales_control: [120000, 125000, 122000, 128000, 126000, 131000, 129000, 134000, 132000, 137000],
    roi_m: [0.54, 0.55, 0.55, 0.55, 0.55, 0.55, 0.55, 0.55, 0.55, 0.55],
    roi_rf: [0.52, 0.53, 0.53, 0.53, 0.53, 0.53, 0.53, 0.53, 0.53, 0.53],
    mroi_m: [0.50, 0.51, 0.51, 0.51, 0.51, 0.51, 0.51, 0.51, 0.51, 0.51],
    mroi_rf: [0.48, 0.49, 0.49, 0.49, 0.49, 0.49, 0.49, 0.49, 0.49, 0.49]
  },
  response_curves: [
    {
      channel: 'TV',
      spend: [0, 25000, 50000, 75000, 100000, 125000, 150000, 175000, 200000],
      outcome: [0, 8500, 16000, 22500, 28000, 32500, 36000, 38500, 40000],
      curve_type: 'saturating'
    },
    {
      channel: 'Digital Search',
      spend: [0, 10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000],
      outcome: [0, 6200, 11800, 16800, 21200, 25000, 28200, 30800, 32800],
      curve_type: 'diminishing'
    },
    {
      channel: 'Social Media',
      spend: [0, 5000, 10000, 15000, 20000, 25000, 30000, 35000, 40000],
      outcome: [0, 2800, 5400, 7800, 10000, 12000, 13800, 15400, 16800],
      curve_type: 'saturating'
    }
  ]
};

// Data processing functions
export function calculateBudgetAllocation(channels: MediaChannel[]): { channel: string; percentage: number }[] {
  const totalSpend = channels.reduce((sum, ch) => sum + ch.spend.reduce((a, b) => a + b, 0), 0);

  return channels.map(channel => ({
    channel: channel.name,
    percentage: (channel.spend.reduce((a, b) => a + b, 0) / totalSpend) * 100
  }));
}

export function calculateChannelEfficiency(channels: MediaChannel[]): { channel: string; efficiency: number }[] {
  return channels.map(channel => ({
    channel: channel.name,
    efficiency: channel.roi
  }));
}

export function getTopPerformers(channels: MediaChannel[], metric: 'roi' | 'mroi' | 'contribution', topN: number = 3) {
  return channels
    .sort((a, b) => {
      const aVal = metric === 'contribution' ? a.contribution.reduce((sum, val) => sum + val, 0) : a[metric];
      const bVal = metric === 'contribution' ? b.contribution.reduce((sum, val) => sum + val, 0) : b[metric];
      return bVal - aVal;
    })
    .slice(0, topN);
}

export function generateTimeSeriesData(kpi: KPIMetrics, timeRange: { start: string; end: string }) {
  const startDate = new Date(timeRange.start);
  const endDate = new Date(timeRange.end);
  const weeks = Math.ceil((endDate.getTime() - startDate.getTime()) / (7 * 24 * 60 * 60 * 1000));

  const dates = [];
  const current = new Date(startDate);

  for (let i = 0; i < weeks; i++) {
    dates.push(new Date(current));
    current.setDate(current.getDate() + 7);
  }

  return {
    dates,
    revenue: kpi.revenue.slice(0, weeks),
    spend: kpi.total_spend.slice(0, weeks),
    roi: kpi.roi_m.slice(0, weeks)
  };
}
