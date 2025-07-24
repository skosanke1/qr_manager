// mockData.ts
export const MOCK_CHANNELS = ["@pokerev", "@ctr"];

export const MOCK_VIDEOS = [
  {
    channel: "@pokerev",
    video: "Video_1",
    total_codes: 3,
    codes: [
      { code: "ABC-1234-XYZ-789", image: "qr_001.png" },
      { code: "DEF-5678-QWE-456", image: "qr_002.png" },
      { code: "GHI-9012-ASD-123", image: "qr_003.png" }
    ],
    data_path: "@pokerev/Video_1"
  },
  {
    channel: "@ctr",
    video: "Video_2",
    total_codes: 2,
    codes: [
      { code: "JKL-3456-ZXC-987", image: "qr_004.png" },
      { code: "MNO-7890-VBN-654", image: "qr_005.png" }
    ],
    data_path: "@ctr/Video_2"
  }
];
