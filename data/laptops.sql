-- =============================================================================
-- Laptop Recommendation Database -- Normalized Schema
-- 7 tables | 28 laptops | CHF retail prices 2024-2025
-- cpu_specs / gpu_specs / ram_specs / storage_specs -> laptops (FK)
-- connectivity_standards -> laptop_connectivity (junction with count)
-- display columns inlined in laptops (unique per unit, no FK needed)
-- =============================================================================
-- MacBooks:      laptop_001-006  (CHF 1 299 - 3 999)
-- Everyday/Work: laptop_007-018  (CHF 599 - 1 999)
-- Gaming:        laptop_019-028  (CHF 849 - 4 299)
-- =============================================================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS laptop_connectivity;
DROP TABLE IF EXISTS laptop_use_cases;
DROP TABLE IF EXISTS laptops;
DROP TABLE IF EXISTS cpu_specs;
DROP TABLE IF EXISTS gpu_specs;
DROP TABLE IF EXISTS ram_specs;
DROP TABLE IF EXISTS storage_specs;
DROP TABLE IF EXISTS connectivity_standards;

-- ─────────────────────────────────────────────────────────────
-- COMPONENT TABLES (shared reference data)
-- ─────────────────────────────────────────────────────────────

CREATE TABLE cpu_specs (
    cpu_id          TEXT PRIMARY KEY,
    brand           TEXT NOT NULL,
    model           TEXT NOT NULL,
    architecture    TEXT,
    cores           INTEGER,
    threads         INTEGER,       -- = cores for Apple & Lunar Lake (no HyperThreading)
    base_ghz        REAL,
    boost_ghz       REAL,          -- = base_ghz for Apple (no boost concept)
    tdp_w           INTEGER
);

CREATE TABLE gpu_specs (
    gpu_id          TEXT PRIMARY KEY,
    type            TEXT NOT NULL CHECK(type IN ('integrated','dedicated')),
    model           TEXT NOT NULL,
    architecture    TEXT,
    vram_gb         INTEGER        -- NULL for integrated & Apple unified memory
);

CREATE TABLE ram_specs (
    ram_id          TEXT PRIMARY KEY,
    gb              INTEGER NOT NULL,
    type            TEXT NOT NULL,
    speed_mhz       INTEGER,
    upgradeable     INTEGER DEFAULT 0,
    slots           INTEGER DEFAULT 0,
    max_gb          INTEGER
);

CREATE TABLE storage_specs (
    storage_id      TEXT PRIMARY KEY,
    gb              INTEGER NOT NULL,
    type            TEXT NOT NULL DEFAULT 'NVMe SSD',
    pcie_gen        INTEGER,
    upgradeable     INTEGER DEFAULT 0,
    m2_slots        INTEGER DEFAULT 0
);

CREATE TABLE connectivity_standards (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    standard_type   TEXT NOT NULL, -- thunderbolt|usb_c|usb_a|hdmi|sd|ethernet|
                                   -- bluetooth|wifi|audio|magsafe|dp|sim|surface_connect
    version         TEXT,
    max_speed_gbps  REAL,          -- NULL for wireless/audio/charging
    max_power_w     INTEGER,       -- NULL for data-only ports
    notes           TEXT
);

-- ─────────────────────────────────────────────────────────────
-- MAIN FACT TABLE
-- ─────────────────────────────────────────────────────────────

CREATE TABLE laptops (
    -- Identity
    id                      TEXT PRIMARY KEY,
    name                    TEXT NOT NULL,
    brand                   TEXT NOT NULL,
    model_line              TEXT,
    category                TEXT NOT NULL CHECK(category IN ('macbook','everyday','gaming')),
    subcategory             TEXT,
    release_year            INTEGER,
    release_month           INTEGER,
    price_chf               INTEGER NOT NULL,
    os                      TEXT NOT NULL,

    -- Component FKs
    cpu_id                  TEXT REFERENCES cpu_specs(cpu_id),
    gpu_id                  TEXT REFERENCES gpu_specs(gpu_id),
    gpu_tgp_w               INTEGER,   -- per-laptop TGP (W); NULL for integrated/Apple

    ram_id                  TEXT REFERENCES ram_specs(ram_id),
    storage_id              TEXT REFERENCES storage_specs(storage_id),

    -- Display (inlined — each laptop has a unique panel configuration)
    disp_inches             REAL,
    disp_width_px           INTEGER,
    disp_height_px          INTEGER,
    disp_refresh_hz         INTEGER,
    disp_panel_type         TEXT,      -- IPS|OLED|Mini-LED IPS|Liquid Retina XDR Mini-LED|...
    disp_nits               INTEGER,
    disp_peak_nits          INTEGER,
    disp_color_srgb_pct     INTEGER,
    disp_color_p3_pct       INTEGER,
    disp_hdr                TEXT,      -- NULL|'XDR'|'DisplayHDR 1000'|'DisplayHDR True Black 600'
    disp_vsr                TEXT,      -- NULL|'ProMotion VRR'|'G-Sync Compatible'
    disp_aspect_ratio       TEXT,
    disp_touch              INTEGER DEFAULT 0,
    disp_glossy             INTEGER DEFAULT 0,

    -- Battery & mobility
    battery_wh              REAL,
    battery_life_hours      INTEGER,
    charger_watts           INTEGER,
    supports_usbc_charging  INTEGER DEFAULT 0,
    weight_kg               REAL,
    thickness_mm            REAL,

    -- Build & input
    build_material          TEXT,
    keyboard_backlit        INTEGER DEFAULT 1,
    keyboard_type           TEXT DEFAULT 'scissor',
    has_numpad              INTEGER DEFAULT 0,

    -- Security & camera
    fingerprint_reader      INTEGER DEFAULT 0,
    face_recognition        INTEGER DEFAULT 0,
    has_ir_camera           INTEGER DEFAULT 0,
    webcam_resolution       TEXT DEFAULT '1080p',

    -- Audio
    speaker_count           INTEGER DEFAULT 2,
    has_dolby_atmos         INTEGER DEFAULT 0,

    -- AI / NPU
    npu_tops                INTEGER DEFAULT 0,  -- Copilot+ PC threshold = 40 TOPS

    -- Gaming
    gaming_capable          INTEGER DEFAULT 0,
    gaming_tier             TEXT DEFAULT 'none'
                                CHECK(gaming_tier IN ('none','light','medium','heavy','enthusiast')),

    -- Recommendation metadata
    good_for                TEXT,      -- comma-separated use-case tags (denorm, for quick filter)
    warranty_years          INTEGER DEFAULT 1,

    -- Scores 1-10
    value_score             INTEGER,
    performance_score       INTEGER,
    portability_score       INTEGER,
    build_quality_score     INTEGER,
    display_score           INTEGER
);

-- ─────────────────────────────────────────────────────────────
-- JUNCTION TABLES
-- ─────────────────────────────────────────────────────────────

CREATE TABLE laptop_connectivity (
    laptop_id       TEXT NOT NULL REFERENCES laptops(id) ON DELETE CASCADE,
    standard_id     TEXT NOT NULL REFERENCES connectivity_standards(id),
    count           INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (laptop_id, standard_id)
);

CREATE TABLE laptop_use_cases (
    laptop_id       TEXT NOT NULL REFERENCES laptops(id) ON DELETE CASCADE,
    use_case        TEXT NOT NULL,
    PRIMARY KEY (laptop_id, use_case)
);

-- ─────────────────────────────────────────────────────────────
-- INDEXES
-- ─────────────────────────────────────────────────────────────
CREATE INDEX idx_laptops_category     ON laptops(category);
CREATE INDEX idx_laptops_price        ON laptops(price_chf);
CREATE INDEX idx_laptops_weight       ON laptops(weight_kg);
CREATE INDEX idx_laptops_battery      ON laptops(battery_life_hours);
CREATE INDEX idx_laptops_gaming_tier  ON laptops(gaming_tier);
CREATE INDEX idx_laptops_npu          ON laptops(npu_tops);
CREATE INDEX idx_laptops_cpu          ON laptops(cpu_id);
CREATE INDEX idx_laptops_gpu          ON laptops(gpu_id);
CREATE INDEX idx_cpu_brand            ON cpu_specs(brand);
CREATE INDEX idx_gpu_type             ON gpu_specs(type);
CREATE INDEX idx_conn_type            ON connectivity_standards(standard_type);
CREATE INDEX idx_lconn_standard       ON laptop_connectivity(standard_id);
CREATE INDEX idx_use_cases_uc         ON laptop_use_cases(use_case);

-- =============================================================================
-- cpu_specs
-- =============================================================================
INSERT INTO cpu_specs VALUES ('cpu_apple_m4', 'Apple', 'Apple M4', 'Apple M4 (ARM)', 10, 10, 4.4, 4.4, 15);
INSERT INTO cpu_specs VALUES ('cpu_apple_m4_pro', 'Apple', 'Apple M4 Pro', 'Apple M4 Pro (ARM)', 14, 14, 4.45, 4.45, 40);
INSERT INTO cpu_specs VALUES ('cpu_apple_m4_max', 'Apple', 'Apple M4 Max', 'Apple M4 Max (ARM)', 16, 16, 4.5, 4.5, 60);
INSERT INTO cpu_specs VALUES ('cpu_i5_1235u', 'Intel', 'Intel Core i5-1235U', 'Intel Alder Lake', 10, 12, 1.3, 4.4, 15);
INSERT INTO cpu_specs VALUES ('cpu_r5_7520u', 'AMD', 'AMD Ryzen 5 7520U', 'AMD Barcelo-R (Zen 2)', 4, 8, 2.8, 4.3, 15);
INSERT INTO cpu_specs VALUES ('cpu_r5_7530u', 'AMD', 'AMD Ryzen 5 7530U', 'AMD Rembrandt-U (Zen 3)', 6, 12, 2.0, 4.5, 15);
INSERT INTO cpu_specs VALUES ('cpu_i5_1335u', 'Intel', 'Intel Core i5-1335U', 'Intel Raptor Lake-U', 10, 12, 1.3, 4.6, 15);
INSERT INTO cpu_specs VALUES ('cpu_sdx_x1e80', 'Qualcomm', 'Snapdragon X Elite X1E-80-100', 'Qualcomm Oryon Gen 1', 12, 12, 3.8, 4.2, 23);
INSERT INTO cpu_specs VALUES ('cpu_r_ai9_hx370', 'AMD', 'AMD Ryzen AI 9 HX 370', 'AMD Strix Point (Zen 5)', 12, 24, 2.0, 5.1, 28);
INSERT INTO cpu_specs VALUES ('cpu_cu7_155h', 'Intel', 'Intel Core Ultra 7 155H', 'Intel Meteor Lake', 16, 22, 1.4, 4.8, 28);
INSERT INTO cpu_specs VALUES ('cpu_cu5_125u', 'Intel', 'Intel Core Ultra 5 125U', 'Intel Meteor Lake', 12, 14, 0.9, 4.4, 15);
INSERT INTO cpu_specs VALUES ('cpu_r_ai7_pro360', 'AMD', 'AMD Ryzen AI 7 PRO 360', 'AMD Hawk Point Pro (Zen 4)', 8, 16, 2.0, 5.1, 28);
INSERT INTO cpu_specs VALUES ('cpu_r5_7535hs', 'AMD', 'AMD Ryzen 5 7535HS', 'AMD Rembrandt-H (Zen 3+)', 6, 12, 3.3, 4.55, 35);
INSERT INTO cpu_specs VALUES ('cpu_i7_13700h', 'Intel', 'Intel Core i7-13700H', 'Intel Raptor Lake-H', 14, 20, 2.4, 5.0, 45);
INSERT INTO cpu_specs VALUES ('cpu_r9_7845hx', 'AMD', 'AMD Ryzen 9 7845HX', 'AMD Dragon Range (Zen 4)', 12, 24, 2.3, 5.4, 55);
INSERT INTO cpu_specs VALUES ('cpu_i7_13620h', 'Intel', 'Intel Core i7-13620H', 'Intel Raptor Lake-H', 10, 16, 2.4, 4.9, 45);
INSERT INTO cpu_specs VALUES ('cpu_cu9_185hx', 'Intel', 'Intel Core Ultra 9 185HX', 'Intel Meteor Lake-HX', 24, 24, 2.3, 5.1, 55);
INSERT INTO cpu_specs VALUES ('cpu_cu9_285h', 'Intel', 'Intel Core Ultra 9 285H', 'Intel Arrow Lake-H', 24, 24, 2.3, 5.1, 45);
INSERT INTO cpu_specs VALUES ('cpu_cu9_285hx', 'Intel', 'Intel Core Ultra 9 285HX', 'Intel Arrow Lake-HX', 24, 24, 2.3, 5.5, 55);
INSERT INTO cpu_specs VALUES ('cpu_i9_13980hx', 'Intel', 'Intel Core i9-13980HX', 'Intel Raptor Lake-HX', 24, 32, 2.2, 5.6, 55);

-- =============================================================================
-- gpu_specs
-- =============================================================================
INSERT INTO gpu_specs VALUES ('gpu_apple_m4_10c', 'integrated', 'Apple M4 10-core GPU', 'Apple M4 GPU', NULL);
INSERT INTO gpu_specs VALUES ('gpu_apple_m4pro_20c', 'integrated', 'Apple M4 Pro 20-core GPU', 'Apple M4 Pro GPU', NULL);
INSERT INTO gpu_specs VALUES ('gpu_apple_m4max_40c', 'integrated', 'Apple M4 Max 40-core GPU', 'Apple M4 Max GPU', NULL);
INSERT INTO gpu_specs VALUES ('gpu_iris_xe_lp', 'integrated', 'Intel Iris Xe Graphics', 'Intel Xe-LP', NULL);
INSERT INTO gpu_specs VALUES ('gpu_radeon_610m', 'integrated', 'AMD Radeon 610M', 'AMD RDNA 2', NULL);
INSERT INTO gpu_specs VALUES ('gpu_radeon_vega7', 'integrated', 'AMD Radeon Vega 7', 'AMD GCN Vega', NULL);
INSERT INTO gpu_specs VALUES ('gpu_adreno_x185', 'integrated', 'Qualcomm Adreno X1-85', 'Qualcomm Adreno', NULL);
INSERT INTO gpu_specs VALUES ('gpu_radeon_890m', 'integrated', 'AMD Radeon 890M', 'AMD RDNA 3.5', NULL);
INSERT INTO gpu_specs VALUES ('gpu_arc_mtl', 'integrated', 'Intel Arc Graphics (Meteor Lake)', 'Intel Xe-LPG', NULL);
INSERT INTO gpu_specs VALUES ('gpu_intel_mtl', 'integrated', 'Intel Graphics (Meteor Lake)', 'Intel Xe-LPG', NULL);
INSERT INTO gpu_specs VALUES ('gpu_radeon_780m', 'integrated', 'AMD Radeon 780M', 'AMD RDNA 3', NULL);
INSERT INTO gpu_specs VALUES ('gpu_rx_7600s', 'dedicated', 'AMD Radeon RX 7600S', 'AMD RDNA 3', 8);
INSERT INTO gpu_specs VALUES ('gpu_rtx_4050', 'dedicated', 'NVIDIA GeForce RTX 4050', 'NVIDIA Ada Lovelace', 6);
INSERT INTO gpu_specs VALUES ('gpu_rtx_4060', 'dedicated', 'NVIDIA GeForce RTX 4060', 'NVIDIA Ada Lovelace', 8);
INSERT INTO gpu_specs VALUES ('gpu_rtx_4070', 'dedicated', 'NVIDIA GeForce RTX 4070', 'NVIDIA Ada Lovelace', 8);
INSERT INTO gpu_specs VALUES ('gpu_rtx_4090', 'dedicated', 'NVIDIA GeForce RTX 4090', 'NVIDIA Ada Lovelace', 16);
INSERT INTO gpu_specs VALUES ('gpu_rtx_5080', 'dedicated', 'NVIDIA GeForce RTX 5080', 'NVIDIA Blackwell', 16);
INSERT INTO gpu_specs VALUES ('gpu_rtx_5090', 'dedicated', 'NVIDIA GeForce RTX 5090', 'NVIDIA Blackwell', 24);

-- =============================================================================
-- ram_specs
-- =============================================================================
INSERT INTO ram_specs VALUES ('ram_16_lpddr5xu_7500_0s_32', 16, 'LPDDR5X Unified', 7500, 0, 0, 32);
INSERT INTO ram_specs VALUES ('ram_48_lpddr5xu_7500_0s_128', 48, 'LPDDR5X Unified', 7500, 0, 0, 128);
INSERT INTO ram_specs VALUES ('ram_8_ddr4_3200_2s_32', 8, 'DDR4', 3200, 1, 2, 32);
INSERT INTO ram_specs VALUES ('ram_8_lpddr5_6400_0s_16', 8, 'LPDDR5', 6400, 0, 0, 16);
INSERT INTO ram_specs VALUES ('ram_16_ddr4_3200_2s_32', 16, 'DDR4', 3200, 1, 2, 32);
INSERT INTO ram_specs VALUES ('ram_16_ddr4_3200_2s_48', 16, 'DDR4', 3200, 1, 2, 48);
INSERT INTO ram_specs VALUES ('ram_16_lpddr5x_8448_0s_64', 16, 'LPDDR5X', 8448, 0, 0, 64);
INSERT INTO ram_specs VALUES ('ram_32_lpddr5x_7500_0s_32', 32, 'LPDDR5X', 7500, 0, 0, 32);
INSERT INTO ram_specs VALUES ('ram_16_lpddr5x_6400_0s_32', 16, 'LPDDR5X', 6400, 0, 0, 32);
INSERT INTO ram_specs VALUES ('ram_16_lpddr5x_6400_1s_64', 16, 'LPDDR5X', 6400, 1, 1, 64);
INSERT INTO ram_specs VALUES ('ram_32_lpddr5x_7500_0s_64', 32, 'LPDDR5X', 7500, 0, 0, 64);
INSERT INTO ram_specs VALUES ('ram_16_ddr5_4800_2s_32', 16, 'DDR5', 4800, 1, 2, 32);
INSERT INTO ram_specs VALUES ('ram_16_ddr5_5600_2s_64', 16, 'DDR5', 5600, 1, 2, 64);
INSERT INTO ram_specs VALUES ('ram_32_lpddr5x_7467_0s_32', 32, 'LPDDR5X', 7467, 0, 0, 32);
INSERT INTO ram_specs VALUES ('ram_64_ddr5_5600_4s_128', 64, 'DDR5', 5600, 1, 4, 128);
INSERT INTO ram_specs VALUES ('ram_32_lpddr5x_7467_2s_64', 32, 'LPDDR5X', 7467, 1, 2, 64);

-- =============================================================================
-- storage_specs
-- =============================================================================
INSERT INTO storage_specs VALUES ('stor_256_pcie4_0s', 256, 'NVMe SSD', 4, 0, 0);
INSERT INTO storage_specs VALUES ('stor_512_pcie4_0s', 512, 'NVMe SSD', 4, 0, 0);
INSERT INTO storage_specs VALUES ('stor_1024_pcie4_0s', 1024, 'NVMe SSD', 4, 0, 0);
INSERT INTO storage_specs VALUES ('stor_512_pcie3_1s', 512, 'NVMe SSD', 3, 1, 1);
INSERT INTO storage_specs VALUES ('stor_512_pcie3_1s_locked', 512, 'NVMe SSD', 3, 0, 1);
INSERT INTO storage_specs VALUES ('stor_512_pcie4_1s', 512, 'NVMe SSD', 4, 1, 1);
INSERT INTO storage_specs VALUES ('stor_512_pcie4_2s', 512, 'NVMe SSD', 4, 1, 2);
INSERT INTO storage_specs VALUES ('stor_512_pcie4_0s_locked', 512, 'NVMe SSD', 4, 0, 0);
INSERT INTO storage_specs VALUES ('stor_1024_pcie4_1s_locked', 1024, 'NVMe SSD', 4, 0, 1);
INSERT INTO storage_specs VALUES ('stor_1024_pcie4_2s', 1024, 'NVMe SSD', 4, 1, 2);
INSERT INTO storage_specs VALUES ('stor_2048_pcie4_2s', 2048, 'NVMe SSD', 4, 1, 2);
INSERT INTO storage_specs VALUES ('stor_2048_pcie4_4s', 2048, 'NVMe SSD', 4, 1, 4);

-- =============================================================================
-- connectivity_standards
-- =============================================================================
INSERT INTO connectivity_standards VALUES ('wifi_5', 'Wi-Fi 5', 'wifi', '802.11ac', NULL, NULL, '2.4/5 GHz, max 3.5 Gbps');
INSERT INTO connectivity_standards VALUES ('wifi_6', 'Wi-Fi 6', 'wifi', '802.11ax', NULL, NULL, '2.4/5 GHz, OFDMA, WPA3');
INSERT INTO connectivity_standards VALUES ('wifi_6e', 'Wi-Fi 6E', 'wifi', '802.11ax-6GHz', NULL, NULL, '2.4/5/6 GHz, lower congestion');
INSERT INTO connectivity_standards VALUES ('wifi_7', 'Wi-Fi 7', 'wifi', '802.11be', NULL, NULL, '2.4/5/6 GHz, MLO, up to 46 Gbps');
INSERT INTO connectivity_standards VALUES ('bt_5_0', 'Bluetooth 5.0', 'bluetooth', '5.0', NULL, NULL, NULL);
INSERT INTO connectivity_standards VALUES ('bt_5_1', 'Bluetooth 5.1', 'bluetooth', '5.1', NULL, NULL, NULL);
INSERT INTO connectivity_standards VALUES ('bt_5_2', 'Bluetooth 5.2', 'bluetooth', '5.2', NULL, NULL, 'LE Audio');
INSERT INTO connectivity_standards VALUES ('bt_5_3', 'Bluetooth 5.3', 'bluetooth', '5.3', NULL, NULL, 'LE Audio, improved coexistence');
INSERT INTO connectivity_standards VALUES ('bt_5_4', 'Bluetooth 5.4', 'bluetooth', '5.4', NULL, NULL, 'Advertising Coding Selection');
INSERT INTO connectivity_standards VALUES ('tb4', 'Thunderbolt 4', 'thunderbolt', '4', 40.0, 100, 'USB-C, min 40 Gbps, DP 1.4, PCIe tunneling, VT-d');
INSERT INTO connectivity_standards VALUES ('tb5', 'Thunderbolt 5', 'thunderbolt', '5', 120.0, 140, 'USB-C, up to 120 Gbps (Bandwidth Boost), DP 2.1');
INSERT INTO connectivity_standards VALUES ('usb4_40', 'USB4 40 Gbps', 'usb_c', 'USB4 Gen 3x2', 40.0, 100, 'No Thunderbolt cert; TB3/4 speed compatible');
INSERT INTO connectivity_standards VALUES ('usb_c_3_2', 'USB-C 3.2 Gen 2', 'usb_c', 'USB 3.2 Gen 2', 10.0, 100, 'USB-C, up to 10 Gbps, Power Delivery');
INSERT INTO connectivity_standards VALUES ('usb_a_3_2', 'USB-A 3.2 Gen 2', 'usb_a', 'USB 3.2 Gen 2', 10.0, NULL, 'USB-A, up to 10 Gbps');
INSERT INTO connectivity_standards VALUES ('usb_a_3_0', 'USB-A 3.0 / 3.1 Gen1', 'usb_a', 'USB 3.0', 5.0, NULL, 'USB-A, up to 5 Gbps');
INSERT INTO connectivity_standards VALUES ('usb_a_2_0', 'USB-A 2.0', 'usb_a', 'USB 2.0', 0.48, NULL, 'USB-A, up to 480 Mbps');
INSERT INTO connectivity_standards VALUES ('hdmi_1_4', 'HDMI 1.4', 'hdmi', '1.4', 10.2, NULL, '4K@30 Hz, 1080p@120 Hz');
INSERT INTO connectivity_standards VALUES ('hdmi_2_0', 'HDMI 2.0', 'hdmi', '2.0', 18.0, NULL, '4K@60 Hz, HDR');
INSERT INTO connectivity_standards VALUES ('hdmi_2_1', 'HDMI 2.1', 'hdmi', '2.1', 48.0, NULL, '8K@30 / 4K@120 Hz, VRR, eARC');
INSERT INTO connectivity_standards VALUES ('mini_dp_1_4', 'Mini DisplayPort 1.4', 'dp', '1.4 mini', 32.4, NULL, '8K@30 / 4K@120 Hz');
INSERT INTO connectivity_standards VALUES ('dp_1_4', 'DisplayPort 1.4', 'dp', '1.4', 32.4, NULL, '8K@30 / 4K@120 Hz');
INSERT INTO connectivity_standards VALUES ('sd_uhs_i', 'SD Card UHS-I', 'sd', 'UHS-I', 0.832, NULL, 'up to 104 MB/s');
INSERT INTO connectivity_standards VALUES ('sd_uhs_ii', 'SD Card UHS-II', 'sd', 'UHS-II', 2.496, NULL, 'up to 312 MB/s (MacBook Pro)');
INSERT INTO connectivity_standards VALUES ('rj45_1g', 'Ethernet RJ-45 1G', 'ethernet', '1 Gbps', 1.0, NULL, NULL);
INSERT INTO connectivity_standards VALUES ('audio_3_5mm', '3.5 mm Audio Jack', 'audio', '3.5 mm', NULL, NULL, 'Combo headphone/mic');
INSERT INTO connectivity_standards VALUES ('magsafe_3', 'MagSafe 3', 'magsafe', '3', NULL, 140, 'Apple magnetic charging, up to 140 W');
INSERT INTO connectivity_standards VALUES ('surface_connect', 'Surface Connect', 'surface_connect', '1', NULL, 65, 'Microsoft magnetic charging, up to 65 W');
INSERT INTO connectivity_standards VALUES ('nano_sim', 'nano-SIM Slot', 'sim', 'nano', NULL, NULL, 'Cellular / 5G slot');

-- =============================================================================
-- laptops
-- =============================================================================
INSERT INTO laptops VALUES ('laptop_001', 'MacBook Air 13" M4 (2025)', 'Apple', 'MacBook Air', 'macbook', 'mid-range', 2025, 3, 1299, 'macOS', 'cpu_apple_m4', 'gpu_apple_m4_10c', NULL, 'ram_16_lpddr5xu_7500_0s_32', 'stor_256_pcie4_0s', 13.6, 2560, 1664, 60, 'Liquid Retina IPS', 500, 500, 100, 100, NULL, NULL, '16:10', 0, 1, 52.6, 18, 35, 1, 1.24, 11.5, 'Aluminium', 1, 'scissor', 0, 1, 0, 0, '1080p FaceTime HD', 2, 1, 38, 1, 'light', 'study,work,university,design,video_editing,programming,office,everyday,streaming,portability', 1, 9, 9, 10, 10, 9);
INSERT INTO laptops VALUES ('laptop_002', 'MacBook Air 15" M4 (2025)', 'Apple', 'MacBook Air', 'macbook', 'mid-range', 2025, 3, 1599, 'macOS', 'cpu_apple_m4', 'gpu_apple_m4_10c', NULL, 'ram_16_lpddr5xu_7500_0s_32', 'stor_512_pcie4_0s', 15.3, 2880, 1864, 60, 'Liquid Retina IPS', 500, 500, 100, 100, NULL, NULL, '16:10', 0, 1, 66.5, 18, 70, 1, 1.51, 11.5, 'Aluminium', 1, 'scissor', 0, 1, 0, 0, '1080p FaceTime HD', 6, 1, 38, 1, 'light', 'study,work,university,design,video_editing,programming,office,everyday,streaming', 1, 8, 9, 8, 10, 10);
INSERT INTO laptops VALUES ('laptop_003', 'MacBook Pro 14" M4 (2024)', 'Apple', 'MacBook Pro', 'macbook', 'premium', 2024, 11, 1799, 'macOS', 'cpu_apple_m4', 'gpu_apple_m4_10c', NULL, 'ram_16_lpddr5xu_7500_0s_32', 'stor_512_pcie4_0s', 14.2, 3024, 1964, 120, 'Liquid Retina XDR Mini-LED', 1000, 1600, 100, 100, 'XDR', 'ProMotion VRR', '16:10', 0, 1, 72.4, 24, 70, 1, 1.55, 15.5, 'Aluminium', 1, 'scissor', 0, 1, 0, 0, '12 MP Center Stage', 6, 1, 38, 1, 'light', 'work,university,design,video_editing,photo_editing,programming,3d_rendering,music_production,portability', 1, 8, 10, 9, 10, 10);
INSERT INTO laptops VALUES ('laptop_004', 'MacBook Pro 14" M4 Pro (2024)', 'Apple', 'MacBook Pro', 'macbook', 'ultra-premium', 2024, 11, 2299, 'macOS', 'cpu_apple_m4_pro', 'gpu_apple_m4pro_20c', NULL, 'ram_16_lpddr5xu_7500_0s_32', 'stor_512_pcie4_0s', 14.2, 3024, 1964, 120, 'Liquid Retina XDR Mini-LED', 1000, 1600, 100, 100, 'XDR', 'ProMotion VRR', '16:10', 0, 1, 72.4, 24, 96, 1, 1.62, 15.5, 'Aluminium', 1, 'scissor', 0, 1, 0, 0, '12 MP Center Stage', 6, 1, 38, 1, 'medium', 'work,design,video_editing,4k_editing,photo_editing,programming,3d_rendering,music_production,machine_learning', 1, 7, 10, 9, 10, 10);
INSERT INTO laptops VALUES ('laptop_005', 'MacBook Pro 16" M4 Pro (2024)', 'Apple', 'MacBook Pro', 'macbook', 'ultra-premium', 2024, 11, 2799, 'macOS', 'cpu_apple_m4_pro', 'gpu_apple_m4pro_20c', NULL, 'ram_16_lpddr5xu_7500_0s_32', 'stor_512_pcie4_0s', 16.2, 3456, 2234, 120, 'Liquid Retina XDR Mini-LED', 1000, 1600, 100, 100, 'XDR', 'ProMotion VRR', '16:10', 0, 1, 99.6, 24, 140, 1, 2.14, 16.8, 'Aluminium', 1, 'scissor', 0, 1, 0, 0, '12 MP Center Stage', 6, 1, 38, 1, 'medium', 'work,design,video_editing,4k_editing,photo_editing,programming,3d_rendering,music_production,machine_learning', 1, 6, 10, 7, 10, 10);
INSERT INTO laptops VALUES ('laptop_006', 'MacBook Pro 16" M4 Max (2024)', 'Apple', 'MacBook Pro', 'macbook', 'ultra-premium', 2024, 11, 3999, 'macOS', 'cpu_apple_m4_max', 'gpu_apple_m4max_40c', NULL, 'ram_48_lpddr5xu_7500_0s_128', 'stor_1024_pcie4_0s', 16.2, 3456, 2234, 120, 'Liquid Retina XDR Mini-LED', 1000, 1600, 100, 100, 'XDR', 'ProMotion VRR', '16:10', 0, 1, 99.6, 24, 140, 1, 2.14, 16.8, 'Aluminium', 1, 'scissor', 0, 1, 0, 0, '12 MP Center Stage', 6, 1, 38, 1, 'heavy', 'work,design,video_editing,8k_editing,3d_rendering,machine_learning,music_production,vfx', 1, 5, 10, 6, 10, 10);
INSERT INTO laptops VALUES ('laptop_007', 'Acer Aspire 3 A315-58', 'Acer', 'Aspire 3', 'everyday', 'budget', 2023, 1, 599, 'Windows 11 Home', 'cpu_i5_1235u', 'gpu_iris_xe_lp', NULL, 'ram_8_ddr4_3200_2s_32', 'stor_512_pcie3_1s', 15.6, 1920, 1080, 60, 'IPS', 250, 250, 100, 62, NULL, NULL, '16:9', 0, 0, 48.0, 10, 65, 0, 1.9, 19.9, 'Plastic', 1, 'scissor', 1, 0, 0, 0, '720p', 2, 0, 0, 0, 'none', 'study,university,browsing,streaming,everyday,office,working_from_home', 1, 9, 5, 5, 4, 5);
INSERT INTO laptops VALUES ('laptop_008', 'Lenovo IdeaPad Slim 3 15ABA7', 'Lenovo', 'IdeaPad Slim 3', 'everyday', 'budget', 2023, 4, 649, 'Windows 11 Home', 'cpu_r5_7520u', 'gpu_radeon_610m', NULL, 'ram_8_lpddr5_6400_0s_16', 'stor_512_pcie3_1s_locked', 15.6, 1920, 1080, 60, 'IPS', 300, 300, 100, 68, NULL, NULL, '16:9', 0, 0, 47.0, 9, 45, 0, 1.7, 17.9, 'Plastic', 1, 'scissor', 1, 0, 0, 0, '720p', 2, 0, 0, 0, 'none', 'study,university,browsing,streaming,everyday,office', 1, 8, 5, 7, 4, 5);
INSERT INTO laptops VALUES ('laptop_009', 'HP 15s-fq5', 'HP', 'HP 15s', 'everyday', 'budget', 2023, 2, 699, 'Windows 11 Home', 'cpu_i5_1235u', 'gpu_iris_xe_lp', NULL, 'ram_8_ddr4_3200_2s_32', 'stor_512_pcie3_1s', 15.6, 1920, 1080, 60, 'IPS', 250, 250, 100, 62, NULL, NULL, '16:9', 0, 0, 41.0, 8, 45, 0, 1.75, 17.9, 'Plastic', 1, 'scissor', 1, 1, 0, 0, '720p', 2, 0, 0, 0, 'none', 'study,university,browsing,streaming,everyday,office,working_from_home', 1, 7, 5, 5, 5, 5);
INSERT INTO laptops VALUES ('laptop_010', 'Asus VivoBook 15 OLED K3504', 'Asus', 'VivoBook 15', 'everyday', 'budget', 2024, 1, 749, 'Windows 11 Home', 'cpu_r5_7530u', 'gpu_radeon_vega7', NULL, 'ram_16_ddr4_3200_2s_32', 'stor_512_pcie3_1s', 15.6, 1920, 1080, 60, 'OLED', 600, 800, 100, 100, 'DisplayHDR True Black 600', NULL, '16:9', 0, 1, 50.0, 9, 65, 1, 1.8, 17.9, 'Plastic', 1, 'scissor', 1, 1, 0, 0, '720p', 2, 1, 0, 0, 'none', 'study,university,browsing,streaming,everyday,office,design,photo_editing', 1, 9, 6, 5, 4, 9);
INSERT INTO laptops VALUES ('laptop_011', 'Dell Inspiron 15 3530', 'Dell', 'Inspiron 15', 'everyday', 'budget', 2023, 4, 799, 'Windows 11 Home', 'cpu_i5_1335u', 'gpu_iris_xe_lp', NULL, 'ram_16_ddr4_3200_2s_32', 'stor_512_pcie3_1s', 15.6, 1920, 1080, 60, 'IPS', 250, 250, 100, 62, NULL, NULL, '16:9', 0, 0, 54.0, 8, 65, 0, 1.85, 19.9, 'Plastic', 1, 'scissor', 1, 1, 0, 0, '720p', 2, 0, 0, 0, 'none', 'study,university,browsing,streaming,everyday,office,working_from_home', 1, 8, 5, 5, 5, 5);
INSERT INTO laptops VALUES ('laptop_012', 'Lenovo ThinkPad E16 Gen 1', 'Lenovo', 'ThinkPad E', 'everyday', 'mid-range', 2023, 6, 999, 'Windows 11 Pro', 'cpu_i5_1335u', 'gpu_iris_xe_lp', NULL, 'ram_16_ddr4_3200_2s_48', 'stor_512_pcie4_2s', 16.0, 1920, 1200, 60, 'IPS', 300, 300, 100, 65, NULL, NULL, '16:10', 0, 0, 57.0, 10, 65, 1, 1.87, 19.9, 'Plastic', 1, 'scissor', 1, 1, 0, 0, '1080p', 2, 0, 0, 0, 'none', 'work,office,university,programming,working_from_home,business', 1, 8, 6, 5, 6, 6);
INSERT INTO laptops VALUES ('laptop_013', 'Microsoft Surface Laptop 7 15"', 'Microsoft', 'Surface Laptop 7', 'everyday', 'premium', 2024, 6, 1499, 'Windows 11 Home', 'cpu_sdx_x1e80', 'gpu_adreno_x185', NULL, 'ram_16_lpddr5x_8448_0s_64', 'stor_512_pcie4_0s_locked', 15.0, 2496, 1664, 60, 'Liquid Crystal IPS', 600, 600, 100, 93, NULL, NULL, '3:2', 1, 1, 54.0, 20, 65, 1, 1.66, 14.5, 'Aluminium', 1, 'scissor', 0, 1, 1, 1, '1080p', 2, 0, 45, 0, 'none', 'work,office,university,everyday,portability,video_calls,streaming', 1, 8, 7, 7, 8, 7);
INSERT INTO laptops VALUES ('laptop_014', 'Asus Zenbook 14 OLED UM3406', 'Asus', 'Zenbook 14', 'everyday', 'mid-range', 2024, 10, 1099, 'Windows 11 Home', 'cpu_r_ai9_hx370', 'gpu_radeon_890m', NULL, 'ram_32_lpddr5x_7500_0s_32', 'stor_1024_pcie4_1s_locked', 14.0, 2880, 1800, 120, 'OLED', 600, 1200, 100, 100, 'DisplayHDR True Black 600', NULL, '16:10', 0, 1, 72.0, 14, 65, 1, 1.2, 14.9, 'Aluminium', 1, 'scissor', 0, 1, 0, 0, '1080p', 6, 0, 50, 0, 'none', 'work,university,everyday,portability,design,photo_editing,streaming,programming', 1, 9, 9, 9, 8, 10);
INSERT INTO laptops VALUES ('laptop_015', 'Dell XPS 13 9340', 'Dell', 'XPS 13', 'everyday', 'premium', 2024, 1, 1399, 'Windows 11 Home', 'cpu_cu7_155h', 'gpu_arc_mtl', NULL, 'ram_16_lpddr5x_6400_0s_32', 'stor_512_pcie4_0s_locked', 13.4, 1920, 1200, 60, 'IPS', 400, 400, 100, 95, NULL, NULL, '16:10', 0, 1, 54.5, 12, 60, 1, 1.17, 15.0, 'Aluminium', 1, 'scissor', 0, 1, 0, 0, '1080p', 4, 0, 11, 0, 'none', 'work,university,everyday,portability,office,programming,business', 1, 7, 8, 9, 9, 8);
INSERT INTO laptops VALUES ('laptop_016', 'Lenovo Yoga 7i 14 Gen 9', 'Lenovo', 'Yoga 7i', 'everyday', 'mid-range', 2024, 6, 1199, 'Windows 11 Home', 'cpu_cu5_125u', 'gpu_intel_mtl', NULL, 'ram_16_lpddr5x_6400_0s_32', 'stor_512_pcie4_1s', 14.0, 1920, 1200, 60, 'IPS', 400, 400, 100, 72, NULL, NULL, '16:10', 1, 1, 71.0, 12, 65, 1, 1.46, 16.9, 'Aluminium', 1, 'scissor', 0, 1, 0, 0, '1080p', 2, 0, 11, 0, 'none', 'work,university,everyday,portability,office,note_taking', 1, 7, 7, 7, 8, 7);
INSERT INTO laptops VALUES ('laptop_017', 'HP EliteBook 845 G11', 'HP', 'EliteBook', 'everyday', 'premium', 2024, 9, 1699, 'Windows 11 Pro', 'cpu_r_ai7_pro360', 'gpu_radeon_780m', NULL, 'ram_16_lpddr5x_6400_1s_64', 'stor_512_pcie4_1s', 14.0, 1920, 1200, 60, 'IPS', 400, 400, 100, 72, NULL, NULL, '16:10', 0, 0, 51.0, 12, 65, 1, 1.37, 17.2, 'Aluminium', 1, 'scissor', 0, 1, 1, 1, '1080p', 2, 0, 50, 0, 'none', 'work,office,business,video_calls,working_from_home,travel', 3, 7, 6, 7, 8, 7);
INSERT INTO laptops VALUES ('laptop_018', 'Asus ProArt Studiobook 16 OLED H7606', 'Asus', 'ProArt Studiobook', 'everyday', 'ultra-premium', 2024, 10, 1999, 'Windows 11 Pro', 'cpu_r_ai9_hx370', 'gpu_rx_7600s', 80, 'ram_32_lpddr5x_7500_0s_64', 'stor_1024_pcie4_2s', 16.0, 3840, 2400, 120, 'OLED', 600, 1200, 100, 100, 'DisplayHDR True Black 600', NULL, '16:10', 1, 1, 90.0, 10, 240, 1, 2.4, 20.0, 'Aluminium', 1, 'scissor', 0, 1, 0, 0, '1080p', 4, 1, 50, 1, 'medium', 'design,photo_editing,video_editing,3d_rendering,programming,work,university', 2, 6, 9, 4, 8, 10);
INSERT INTO laptops VALUES ('laptop_019', 'Lenovo IdeaPad Gaming 3 Gen 9 15"', 'Lenovo', 'IdeaPad Gaming 3', 'gaming', 'budget', 2024, 8, 849, 'Windows 11 Home', 'cpu_r5_7535hs', 'gpu_rtx_4050', 65, 'ram_16_ddr5_4800_2s_32', 'stor_512_pcie4_1s', 15.6, 1920, 1080, 144, 'IPS', 250, 250, 100, 62, NULL, 'G-Sync Compatible', '16:9', 0, 0, 60.0, 6, 170, 0, 2.2, 21.9, 'Plastic', 1, 'scissor', 1, 0, 0, 0, '720p', 2, 0, 0, 1, 'medium', 'gaming,study,university,streaming,everyday', 1, 8, 4, 5, 5, 6);
INSERT INTO laptops VALUES ('laptop_020', 'Acer Nitro 16 AN16-41', 'Acer', 'Nitro 16', 'gaming', 'budget', 2024, 5, 999, 'Windows 11 Home', 'cpu_r5_7535hs', 'gpu_rtx_4060', 80, 'ram_16_ddr5_4800_2s_32', 'stor_512_pcie4_2s', 16.0, 1920, 1080, 165, 'IPS', 300, 300, 100, 68, NULL, 'G-Sync Compatible', '16:9', 0, 0, 90.0, 7, 180, 0, 2.5, 24.9, 'Plastic', 1, 'scissor', 1, 0, 0, 0, '720p', 4, 0, 0, 1, 'heavy', 'gaming,heavy_gaming,study,university,streaming', 1, 8, 4, 4, 5, 7);
INSERT INTO laptops VALUES ('laptop_021', 'HP Victus 16 FA2074ng', 'HP', 'Victus 16', 'gaming', 'budget', 2024, 9, 1099, 'Windows 11 Home', 'cpu_i7_13700h', 'gpu_rtx_4060', 80, 'ram_16_ddr4_3200_2s_32', 'stor_512_pcie4_1s', 16.1, 1920, 1080, 144, 'IPS', 250, 250, 100, 62, NULL, 'G-Sync Compatible', '16:9', 0, 0, 70.0, 6, 200, 0, 2.3, 23.5, 'Plastic', 1, 'scissor', 1, 0, 0, 0, '720p', 2, 0, 0, 1, 'heavy', 'gaming,heavy_gaming,study,university,streaming,everyday', 1, 7, 4, 4, 5, 7);
INSERT INTO laptops VALUES ('laptop_022', 'Asus TUF Gaming A16 FA617NS', 'Asus', 'TUF Gaming A16', 'gaming', 'mid-range', 2024, 1, 1149, 'Windows 11 Home', 'cpu_r9_7845hx', 'gpu_rtx_4070', 115, 'ram_16_ddr5_4800_2s_32', 'stor_512_pcie4_2s', 16.0, 1920, 1080, 165, 'IPS', 300, 300, 100, 68, NULL, 'G-Sync Compatible', '16:9', 0, 0, 90.0, 8, 240, 0, 2.3, 22.0, 'Plastic', 1, 'scissor', 1, 0, 0, 0, '720p', 2, 0, 0, 1, 'heavy', 'gaming,heavy_gaming,esports,streaming,study', 2, 7, 4, 3, 6, 7);
INSERT INTO laptops VALUES ('laptop_023', 'MSI Thin 15 B13UC', 'MSI', 'MSI Thin', 'gaming', 'mid-range', 2024, 3, 1199, 'Windows 11 Home', 'cpu_i7_13620h', 'gpu_rtx_4050', 60, 'ram_16_ddr4_3200_2s_32', 'stor_512_pcie4_1s', 15.6, 1920, 1080, 144, 'IPS', 250, 250, 100, 62, NULL, 'G-Sync Compatible', '16:9', 0, 0, 53.8, 5, 180, 0, 1.86, 19.9, 'Plastic', 1, 'scissor', 0, 1, 0, 0, '720p', 2, 0, 0, 1, 'medium', 'gaming,study,university,everyday,portability', 1, 7, 5, 5, 6, 6);
INSERT INTO laptops VALUES ('laptop_024', 'Lenovo Legion 5i Pro 16 Gen 9', 'Lenovo', 'Legion 5i Pro', 'gaming', 'mid-range', 2024, 5, 1699, 'Windows 11 Home', 'cpu_cu9_185hx', 'gpu_rtx_4070', 140, 'ram_16_ddr5_5600_2s_64', 'stor_1024_pcie4_2s', 16.0, 2560, 1600, 240, 'IPS', 500, 500, 100, 100, NULL, 'G-Sync Compatible', '16:10', 0, 0, 99.9, 8, 300, 0, 2.5, 20.9, 'Aluminium', 1, 'scissor', 0, 1, 0, 0, '1080p', 2, 1, 0, 1, 'heavy', 'gaming,heavy_gaming,esports,4k_gaming,streaming,study', 2, 8, 4, 3, 8, 8);
INSERT INTO laptops VALUES ('laptop_025', 'Asus ROG Zephyrus G16 GU605', 'Asus', 'ROG Zephyrus G16', 'gaming', 'premium', 2025, 3, 2199, 'Windows 11 Home', 'cpu_cu9_285h', 'gpu_rtx_5080', 150, 'ram_32_lpddr5x_7467_0s_32', 'stor_1024_pcie4_2s', 16.0, 2560, 1600, 240, 'OLED', 400, 800, 100, 100, 'DisplayHDR True Black 600', 'G-Sync Compatible', '16:10', 0, 1, 90.0, 10, 240, 1, 1.85, 15.9, 'Aluminium', 1, 'scissor', 0, 1, 0, 0, '1080p', 6, 1, 13, 1, 'enthusiast', 'gaming,heavy_gaming,esports,4k_gaming,streaming,design,video_editing', 2, 8, 5, 9, 10, 10);
INSERT INTO laptops VALUES ('laptop_026', 'Razer Blade 16 (2025)', 'Razer', 'Blade 16', 'gaming', 'ultra-premium', 2025, 1, 3299, 'Windows 11 Home', 'cpu_cu9_285hx', 'gpu_rtx_5090', 150, 'ram_32_lpddr5x_7467_0s_32', 'stor_2048_pcie4_2s', 16.0, 2560, 1600, 240, 'OLED', 400, 800, 100, 100, 'DisplayHDR True Black 600', 'G-Sync Compatible', '16:10', 0, 1, 95.2, 10, 330, 1, 2.1, 16.0, 'Aluminium (CNC)', 1, 'scissor', 0, 1, 0, 0, '1080p', 6, 1, 13, 1, 'enthusiast', 'gaming,heavy_gaming,4k_gaming,esports,design,video_editing,3d_rendering,streaming', 2, 6, 3, 10, 10, 10);
INSERT INTO laptops VALUES ('laptop_027', 'MSI Titan GT77 HX 13VI', 'MSI', 'Titan GT77', 'gaming', 'ultra-premium', 2024, 1, 3799, 'Windows 11 Pro', 'cpu_i9_13980hx', 'gpu_rtx_4090', 150, 'ram_64_ddr5_5600_4s_128', 'stor_2048_pcie4_4s', 17.3, 3840, 2160, 144, 'IPS', 600, 1000, 100, 100, 'DisplayHDR 1000', NULL, '16:9', 0, 1, 99.9, 5, 330, 0, 3.0, 23.4, 'Aluminium', 1, 'scissor', 1, 1, 0, 0, '1080p', 6, 1, 0, 1, 'enthusiast', 'gaming,heavy_gaming,4k_gaming,3d_rendering,machine_learning,video_editing,vfx', 2, 5, 1, 9, 9, 9);
INSERT INTO laptops VALUES ('laptop_028', 'Asus ROG Strix SCAR 18 G834 (2025)', 'Asus', 'ROG Strix SCAR', 'gaming', 'ultra-premium', 2025, 2, 4299, 'Windows 11 Home', 'cpu_cu9_285hx', 'gpu_rtx_5090', 150, 'ram_32_lpddr5x_7467_2s_64', 'stor_2048_pcie4_2s', 18.0, 2560, 1600, 240, 'Mini-LED IPS', 500, 1100, 100, 100, 'DisplayHDR 1000', 'G-Sync Compatible', '16:10', 0, 0, 90.0, 8, 330, 0, 3.1, 27.2, 'Aluminium', 1, 'scissor', 1, 1, 0, 0, '1080p', 6, 1, 13, 1, 'enthusiast', 'gaming,heavy_gaming,4k_gaming,esports,3d_rendering,machine_learning,vfx,streaming', 2, 5, 1, 9, 9, 9);

-- =============================================================================
-- laptop_connectivity
-- =============================================================================
INSERT INTO laptop_connectivity VALUES ('laptop_001','tb4',2);
INSERT INTO laptop_connectivity VALUES ('laptop_001','magsafe_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_001','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_001','wifi_7',1);
INSERT INTO laptop_connectivity VALUES ('laptop_001','bt_5_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_002','tb4',2);
INSERT INTO laptop_connectivity VALUES ('laptop_002','magsafe_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_002','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_002','wifi_7',1);
INSERT INTO laptop_connectivity VALUES ('laptop_002','bt_5_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_003','tb4',3);
INSERT INTO laptop_connectivity VALUES ('laptop_003','magsafe_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_003','hdmi_2_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_003','sd_uhs_ii',1);
INSERT INTO laptop_connectivity VALUES ('laptop_003','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_003','wifi_7',1);
INSERT INTO laptop_connectivity VALUES ('laptop_003','bt_5_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_004','tb5',3);
INSERT INTO laptop_connectivity VALUES ('laptop_004','magsafe_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_004','hdmi_2_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_004','sd_uhs_ii',1);
INSERT INTO laptop_connectivity VALUES ('laptop_004','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_004','wifi_7',1);
INSERT INTO laptop_connectivity VALUES ('laptop_004','bt_5_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_005','tb5',3);
INSERT INTO laptop_connectivity VALUES ('laptop_005','magsafe_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_005','hdmi_2_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_005','sd_uhs_ii',1);
INSERT INTO laptop_connectivity VALUES ('laptop_005','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_005','wifi_7',1);
INSERT INTO laptop_connectivity VALUES ('laptop_005','bt_5_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_006','tb5',3);
INSERT INTO laptop_connectivity VALUES ('laptop_006','magsafe_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_006','hdmi_2_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_006','sd_uhs_ii',1);
INSERT INTO laptop_connectivity VALUES ('laptop_006','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_006','wifi_7',1);
INSERT INTO laptop_connectivity VALUES ('laptop_006','bt_5_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_007','usb_a_3_2',1);
INSERT INTO laptop_connectivity VALUES ('laptop_007','usb_a_2_0',2);
INSERT INTO laptop_connectivity VALUES ('laptop_007','usb_c_3_2',1);
INSERT INTO laptop_connectivity VALUES ('laptop_007','hdmi_1_4',1);
INSERT INTO laptop_connectivity VALUES ('laptop_007','rj45_1g',1);
INSERT INTO laptop_connectivity VALUES ('laptop_007','sd_uhs_i',1);
INSERT INTO laptop_connectivity VALUES ('laptop_007','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_007','wifi_6',1);
INSERT INTO laptop_connectivity VALUES ('laptop_007','bt_5_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_008','usb_a_3_2',2);
INSERT INTO laptop_connectivity VALUES ('laptop_008','usb_c_3_2',1);
INSERT INTO laptop_connectivity VALUES ('laptop_008','hdmi_1_4',1);
INSERT INTO laptop_connectivity VALUES ('laptop_008','sd_uhs_i',1);
INSERT INTO laptop_connectivity VALUES ('laptop_008','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_008','wifi_6',1);
INSERT INTO laptop_connectivity VALUES ('laptop_008','bt_5_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_009','usb_a_3_0',2);
INSERT INTO laptop_connectivity VALUES ('laptop_009','usb_c_3_2',1);
INSERT INTO laptop_connectivity VALUES ('laptop_009','hdmi_1_4',1);
INSERT INTO laptop_connectivity VALUES ('laptop_009','sd_uhs_i',1);
INSERT INTO laptop_connectivity VALUES ('laptop_009','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_009','wifi_5',1);
INSERT INTO laptop_connectivity VALUES ('laptop_009','bt_5_0',1);
INSERT INTO laptop_connectivity VALUES ('laptop_010','usb_a_3_2',3);
INSERT INTO laptop_connectivity VALUES ('laptop_010','usb_c_3_2',1);
INSERT INTO laptop_connectivity VALUES ('laptop_010','hdmi_1_4',1);
INSERT INTO laptop_connectivity VALUES ('laptop_010','sd_uhs_i',1);
INSERT INTO laptop_connectivity VALUES ('laptop_010','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_010','wifi_6',1);
INSERT INTO laptop_connectivity VALUES ('laptop_010','bt_5_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_011','usb_a_3_0',2);
INSERT INTO laptop_connectivity VALUES ('laptop_011','usb_c_3_2',1);
INSERT INTO laptop_connectivity VALUES ('laptop_011','hdmi_1_4',1);
INSERT INTO laptop_connectivity VALUES ('laptop_011','rj45_1g',1);
INSERT INTO laptop_connectivity VALUES ('laptop_011','sd_uhs_i',1);
INSERT INTO laptop_connectivity VALUES ('laptop_011','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_011','wifi_6',1);
INSERT INTO laptop_connectivity VALUES ('laptop_011','bt_5_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_012','usb_a_3_2',2);
INSERT INTO laptop_connectivity VALUES ('laptop_012','tb4',1);
INSERT INTO laptop_connectivity VALUES ('laptop_012','usb_c_3_2',1);
INSERT INTO laptop_connectivity VALUES ('laptop_012','hdmi_1_4',1);
INSERT INTO laptop_connectivity VALUES ('laptop_012','rj45_1g',1);
INSERT INTO laptop_connectivity VALUES ('laptop_012','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_012','wifi_6e',1);
INSERT INTO laptop_connectivity VALUES ('laptop_012','bt_5_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_013','usb4_40',2);
INSERT INTO laptop_connectivity VALUES ('laptop_013','usb_a_3_0',1);
INSERT INTO laptop_connectivity VALUES ('laptop_013','hdmi_2_0',1);
INSERT INTO laptop_connectivity VALUES ('laptop_013','surface_connect',1);
INSERT INTO laptop_connectivity VALUES ('laptop_013','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_013','wifi_7',1);
INSERT INTO laptop_connectivity VALUES ('laptop_013','bt_5_4',1);
INSERT INTO laptop_connectivity VALUES ('laptop_014','usb4_40',2);
INSERT INTO laptop_connectivity VALUES ('laptop_014','usb_a_3_2',1);
INSERT INTO laptop_connectivity VALUES ('laptop_014','hdmi_2_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_014','sd_uhs_i',1);
INSERT INTO laptop_connectivity VALUES ('laptop_014','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_014','wifi_7',1);
INSERT INTO laptop_connectivity VALUES ('laptop_014','bt_5_4',1);
INSERT INTO laptop_connectivity VALUES ('laptop_015','tb4',2);
INSERT INTO laptop_connectivity VALUES ('laptop_015','usb_c_3_2',1);
INSERT INTO laptop_connectivity VALUES ('laptop_015','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_015','wifi_6e',1);
INSERT INTO laptop_connectivity VALUES ('laptop_015','bt_5_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_016','tb4',2);
INSERT INTO laptop_connectivity VALUES ('laptop_016','usb_a_3_2',1);
INSERT INTO laptop_connectivity VALUES ('laptop_016','hdmi_2_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_016','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_016','wifi_6e',1);
INSERT INTO laptop_connectivity VALUES ('laptop_016','bt_5_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_017','usb4_40',2);
INSERT INTO laptop_connectivity VALUES ('laptop_017','usb_a_3_2',2);
INSERT INTO laptop_connectivity VALUES ('laptop_017','hdmi_2_0',1);
INSERT INTO laptop_connectivity VALUES ('laptop_017','rj45_1g',1);
INSERT INTO laptop_connectivity VALUES ('laptop_017','sd_uhs_i',1);
INSERT INTO laptop_connectivity VALUES ('laptop_017','nano_sim',1);
INSERT INTO laptop_connectivity VALUES ('laptop_017','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_017','wifi_6e',1);
INSERT INTO laptop_connectivity VALUES ('laptop_017','bt_5_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_018','tb4',2);
INSERT INTO laptop_connectivity VALUES ('laptop_018','usb_a_3_2',2);
INSERT INTO laptop_connectivity VALUES ('laptop_018','usb_c_3_2',1);
INSERT INTO laptop_connectivity VALUES ('laptop_018','hdmi_2_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_018','sd_uhs_i',1);
INSERT INTO laptop_connectivity VALUES ('laptop_018','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_018','wifi_6e',1);
INSERT INTO laptop_connectivity VALUES ('laptop_018','bt_5_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_019','usb_a_3_2',2);
INSERT INTO laptop_connectivity VALUES ('laptop_019','usb_c_3_2',1);
INSERT INTO laptop_connectivity VALUES ('laptop_019','hdmi_2_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_019','sd_uhs_i',1);
INSERT INTO laptop_connectivity VALUES ('laptop_019','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_019','wifi_6',1);
INSERT INTO laptop_connectivity VALUES ('laptop_019','bt_5_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_020','usb_a_3_2',3);
INSERT INTO laptop_connectivity VALUES ('laptop_020','usb_c_3_2',1);
INSERT INTO laptop_connectivity VALUES ('laptop_020','hdmi_2_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_020','sd_uhs_i',1);
INSERT INTO laptop_connectivity VALUES ('laptop_020','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_020','wifi_6e',1);
INSERT INTO laptop_connectivity VALUES ('laptop_020','bt_5_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_021','usb_a_3_0',2);
INSERT INTO laptop_connectivity VALUES ('laptop_021','usb_c_3_2',1);
INSERT INTO laptop_connectivity VALUES ('laptop_021','hdmi_2_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_021','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_021','wifi_6',1);
INSERT INTO laptop_connectivity VALUES ('laptop_021','bt_5_2',1);
INSERT INTO laptop_connectivity VALUES ('laptop_022','usb_a_3_2',3);
INSERT INTO laptop_connectivity VALUES ('laptop_022','tb4',1);
INSERT INTO laptop_connectivity VALUES ('laptop_022','hdmi_2_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_022','sd_uhs_i',1);
INSERT INTO laptop_connectivity VALUES ('laptop_022','rj45_1g',1);
INSERT INTO laptop_connectivity VALUES ('laptop_022','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_022','wifi_6e',1);
INSERT INTO laptop_connectivity VALUES ('laptop_022','bt_5_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_023','usb_a_3_2',3);
INSERT INTO laptop_connectivity VALUES ('laptop_023','usb_c_3_2',1);
INSERT INTO laptop_connectivity VALUES ('laptop_023','hdmi_2_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_023','sd_uhs_i',1);
INSERT INTO laptop_connectivity VALUES ('laptop_023','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_023','wifi_6e',1);
INSERT INTO laptop_connectivity VALUES ('laptop_023','bt_5_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_024','usb_a_3_2',2);
INSERT INTO laptop_connectivity VALUES ('laptop_024','usb_c_3_2',1);
INSERT INTO laptop_connectivity VALUES ('laptop_024','tb4',2);
INSERT INTO laptop_connectivity VALUES ('laptop_024','hdmi_2_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_024','sd_uhs_i',1);
INSERT INTO laptop_connectivity VALUES ('laptop_024','rj45_1g',1);
INSERT INTO laptop_connectivity VALUES ('laptop_024','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_024','wifi_6e',1);
INSERT INTO laptop_connectivity VALUES ('laptop_024','bt_5_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_025','tb4',2);
INSERT INTO laptop_connectivity VALUES ('laptop_025','usb_a_3_2',2);
INSERT INTO laptop_connectivity VALUES ('laptop_025','usb_c_3_2',1);
INSERT INTO laptop_connectivity VALUES ('laptop_025','hdmi_2_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_025','sd_uhs_i',1);
INSERT INTO laptop_connectivity VALUES ('laptop_025','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_025','wifi_7',1);
INSERT INTO laptop_connectivity VALUES ('laptop_025','bt_5_4',1);
INSERT INTO laptop_connectivity VALUES ('laptop_026','tb5',2);
INSERT INTO laptop_connectivity VALUES ('laptop_026','tb4',1);
INSERT INTO laptop_connectivity VALUES ('laptop_026','usb_a_3_2',2);
INSERT INTO laptop_connectivity VALUES ('laptop_026','hdmi_2_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_026','sd_uhs_i',1);
INSERT INTO laptop_connectivity VALUES ('laptop_026','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_026','wifi_7',1);
INSERT INTO laptop_connectivity VALUES ('laptop_026','bt_5_4',1);
INSERT INTO laptop_connectivity VALUES ('laptop_027','usb_a_3_2',3);
INSERT INTO laptop_connectivity VALUES ('laptop_027','tb4',3);
INSERT INTO laptop_connectivity VALUES ('laptop_027','hdmi_2_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_027','mini_dp_1_4',1);
INSERT INTO laptop_connectivity VALUES ('laptop_027','rj45_1g',1);
INSERT INTO laptop_connectivity VALUES ('laptop_027','sd_uhs_i',1);
INSERT INTO laptop_connectivity VALUES ('laptop_027','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_027','wifi_6e',1);
INSERT INTO laptop_connectivity VALUES ('laptop_027','bt_5_3',1);
INSERT INTO laptop_connectivity VALUES ('laptop_028','usb_a_3_2',3);
INSERT INTO laptop_connectivity VALUES ('laptop_028','tb5',2);
INSERT INTO laptop_connectivity VALUES ('laptop_028','tb4',1);
INSERT INTO laptop_connectivity VALUES ('laptop_028','hdmi_2_1',1);
INSERT INTO laptop_connectivity VALUES ('laptop_028','dp_1_4',1);
INSERT INTO laptop_connectivity VALUES ('laptop_028','rj45_1g',1);
INSERT INTO laptop_connectivity VALUES ('laptop_028','sd_uhs_i',1);
INSERT INTO laptop_connectivity VALUES ('laptop_028','audio_3_5mm',1);
INSERT INTO laptop_connectivity VALUES ('laptop_028','wifi_7',1);
INSERT INTO laptop_connectivity VALUES ('laptop_028','bt_5_4',1);

-- =============================================================================
-- laptop_use_cases
-- =============================================================================
INSERT INTO laptop_use_cases VALUES ('laptop_001','study');
INSERT INTO laptop_use_cases VALUES ('laptop_001','work');
INSERT INTO laptop_use_cases VALUES ('laptop_001','university');
INSERT INTO laptop_use_cases VALUES ('laptop_001','design');
INSERT INTO laptop_use_cases VALUES ('laptop_001','video_editing');
INSERT INTO laptop_use_cases VALUES ('laptop_001','programming');
INSERT INTO laptop_use_cases VALUES ('laptop_001','office');
INSERT INTO laptop_use_cases VALUES ('laptop_001','everyday');
INSERT INTO laptop_use_cases VALUES ('laptop_001','streaming');
INSERT INTO laptop_use_cases VALUES ('laptop_001','portability');
INSERT INTO laptop_use_cases VALUES ('laptop_002','study');
INSERT INTO laptop_use_cases VALUES ('laptop_002','work');
INSERT INTO laptop_use_cases VALUES ('laptop_002','university');
INSERT INTO laptop_use_cases VALUES ('laptop_002','design');
INSERT INTO laptop_use_cases VALUES ('laptop_002','video_editing');
INSERT INTO laptop_use_cases VALUES ('laptop_002','programming');
INSERT INTO laptop_use_cases VALUES ('laptop_002','office');
INSERT INTO laptop_use_cases VALUES ('laptop_002','everyday');
INSERT INTO laptop_use_cases VALUES ('laptop_002','streaming');
INSERT INTO laptop_use_cases VALUES ('laptop_003','work');
INSERT INTO laptop_use_cases VALUES ('laptop_003','university');
INSERT INTO laptop_use_cases VALUES ('laptop_003','design');
INSERT INTO laptop_use_cases VALUES ('laptop_003','video_editing');
INSERT INTO laptop_use_cases VALUES ('laptop_003','photo_editing');
INSERT INTO laptop_use_cases VALUES ('laptop_003','programming');
INSERT INTO laptop_use_cases VALUES ('laptop_003','3d_rendering');
INSERT INTO laptop_use_cases VALUES ('laptop_003','music_production');
INSERT INTO laptop_use_cases VALUES ('laptop_003','portability');
INSERT INTO laptop_use_cases VALUES ('laptop_004','work');
INSERT INTO laptop_use_cases VALUES ('laptop_004','design');
INSERT INTO laptop_use_cases VALUES ('laptop_004','video_editing');
INSERT INTO laptop_use_cases VALUES ('laptop_004','4k_editing');
INSERT INTO laptop_use_cases VALUES ('laptop_004','photo_editing');
INSERT INTO laptop_use_cases VALUES ('laptop_004','programming');
INSERT INTO laptop_use_cases VALUES ('laptop_004','3d_rendering');
INSERT INTO laptop_use_cases VALUES ('laptop_004','music_production');
INSERT INTO laptop_use_cases VALUES ('laptop_004','machine_learning');
INSERT INTO laptop_use_cases VALUES ('laptop_005','work');
INSERT INTO laptop_use_cases VALUES ('laptop_005','design');
INSERT INTO laptop_use_cases VALUES ('laptop_005','video_editing');
INSERT INTO laptop_use_cases VALUES ('laptop_005','4k_editing');
INSERT INTO laptop_use_cases VALUES ('laptop_005','photo_editing');
INSERT INTO laptop_use_cases VALUES ('laptop_005','programming');
INSERT INTO laptop_use_cases VALUES ('laptop_005','3d_rendering');
INSERT INTO laptop_use_cases VALUES ('laptop_005','music_production');
INSERT INTO laptop_use_cases VALUES ('laptop_005','machine_learning');
INSERT INTO laptop_use_cases VALUES ('laptop_006','work');
INSERT INTO laptop_use_cases VALUES ('laptop_006','design');
INSERT INTO laptop_use_cases VALUES ('laptop_006','video_editing');
INSERT INTO laptop_use_cases VALUES ('laptop_006','8k_editing');
INSERT INTO laptop_use_cases VALUES ('laptop_006','3d_rendering');
INSERT INTO laptop_use_cases VALUES ('laptop_006','machine_learning');
INSERT INTO laptop_use_cases VALUES ('laptop_006','music_production');
INSERT INTO laptop_use_cases VALUES ('laptop_006','vfx');
INSERT INTO laptop_use_cases VALUES ('laptop_007','study');
INSERT INTO laptop_use_cases VALUES ('laptop_007','university');
INSERT INTO laptop_use_cases VALUES ('laptop_007','browsing');
INSERT INTO laptop_use_cases VALUES ('laptop_007','streaming');
INSERT INTO laptop_use_cases VALUES ('laptop_007','everyday');
INSERT INTO laptop_use_cases VALUES ('laptop_007','office');
INSERT INTO laptop_use_cases VALUES ('laptop_007','working_from_home');
INSERT INTO laptop_use_cases VALUES ('laptop_008','study');
INSERT INTO laptop_use_cases VALUES ('laptop_008','university');
INSERT INTO laptop_use_cases VALUES ('laptop_008','browsing');
INSERT INTO laptop_use_cases VALUES ('laptop_008','streaming');
INSERT INTO laptop_use_cases VALUES ('laptop_008','everyday');
INSERT INTO laptop_use_cases VALUES ('laptop_008','office');
INSERT INTO laptop_use_cases VALUES ('laptop_009','study');
INSERT INTO laptop_use_cases VALUES ('laptop_009','university');
INSERT INTO laptop_use_cases VALUES ('laptop_009','browsing');
INSERT INTO laptop_use_cases VALUES ('laptop_009','streaming');
INSERT INTO laptop_use_cases VALUES ('laptop_009','everyday');
INSERT INTO laptop_use_cases VALUES ('laptop_009','office');
INSERT INTO laptop_use_cases VALUES ('laptop_009','working_from_home');
INSERT INTO laptop_use_cases VALUES ('laptop_010','study');
INSERT INTO laptop_use_cases VALUES ('laptop_010','university');
INSERT INTO laptop_use_cases VALUES ('laptop_010','browsing');
INSERT INTO laptop_use_cases VALUES ('laptop_010','streaming');
INSERT INTO laptop_use_cases VALUES ('laptop_010','everyday');
INSERT INTO laptop_use_cases VALUES ('laptop_010','office');
INSERT INTO laptop_use_cases VALUES ('laptop_010','design');
INSERT INTO laptop_use_cases VALUES ('laptop_010','photo_editing');
INSERT INTO laptop_use_cases VALUES ('laptop_011','study');
INSERT INTO laptop_use_cases VALUES ('laptop_011','university');
INSERT INTO laptop_use_cases VALUES ('laptop_011','browsing');
INSERT INTO laptop_use_cases VALUES ('laptop_011','streaming');
INSERT INTO laptop_use_cases VALUES ('laptop_011','everyday');
INSERT INTO laptop_use_cases VALUES ('laptop_011','office');
INSERT INTO laptop_use_cases VALUES ('laptop_011','working_from_home');
INSERT INTO laptop_use_cases VALUES ('laptop_012','work');
INSERT INTO laptop_use_cases VALUES ('laptop_012','office');
INSERT INTO laptop_use_cases VALUES ('laptop_012','university');
INSERT INTO laptop_use_cases VALUES ('laptop_012','programming');
INSERT INTO laptop_use_cases VALUES ('laptop_012','working_from_home');
INSERT INTO laptop_use_cases VALUES ('laptop_012','business');
INSERT INTO laptop_use_cases VALUES ('laptop_013','work');
INSERT INTO laptop_use_cases VALUES ('laptop_013','office');
INSERT INTO laptop_use_cases VALUES ('laptop_013','university');
INSERT INTO laptop_use_cases VALUES ('laptop_013','everyday');
INSERT INTO laptop_use_cases VALUES ('laptop_013','portability');
INSERT INTO laptop_use_cases VALUES ('laptop_013','video_calls');
INSERT INTO laptop_use_cases VALUES ('laptop_013','streaming');
INSERT INTO laptop_use_cases VALUES ('laptop_014','work');
INSERT INTO laptop_use_cases VALUES ('laptop_014','university');
INSERT INTO laptop_use_cases VALUES ('laptop_014','everyday');
INSERT INTO laptop_use_cases VALUES ('laptop_014','portability');
INSERT INTO laptop_use_cases VALUES ('laptop_014','design');
INSERT INTO laptop_use_cases VALUES ('laptop_014','photo_editing');
INSERT INTO laptop_use_cases VALUES ('laptop_014','streaming');
INSERT INTO laptop_use_cases VALUES ('laptop_014','programming');
INSERT INTO laptop_use_cases VALUES ('laptop_015','work');
INSERT INTO laptop_use_cases VALUES ('laptop_015','university');
INSERT INTO laptop_use_cases VALUES ('laptop_015','everyday');
INSERT INTO laptop_use_cases VALUES ('laptop_015','portability');
INSERT INTO laptop_use_cases VALUES ('laptop_015','office');
INSERT INTO laptop_use_cases VALUES ('laptop_015','programming');
INSERT INTO laptop_use_cases VALUES ('laptop_015','business');
INSERT INTO laptop_use_cases VALUES ('laptop_016','work');
INSERT INTO laptop_use_cases VALUES ('laptop_016','university');
INSERT INTO laptop_use_cases VALUES ('laptop_016','everyday');
INSERT INTO laptop_use_cases VALUES ('laptop_016','portability');
INSERT INTO laptop_use_cases VALUES ('laptop_016','office');
INSERT INTO laptop_use_cases VALUES ('laptop_016','note_taking');
INSERT INTO laptop_use_cases VALUES ('laptop_017','work');
INSERT INTO laptop_use_cases VALUES ('laptop_017','office');
INSERT INTO laptop_use_cases VALUES ('laptop_017','business');
INSERT INTO laptop_use_cases VALUES ('laptop_017','video_calls');
INSERT INTO laptop_use_cases VALUES ('laptop_017','working_from_home');
INSERT INTO laptop_use_cases VALUES ('laptop_017','travel');
INSERT INTO laptop_use_cases VALUES ('laptop_018','design');
INSERT INTO laptop_use_cases VALUES ('laptop_018','photo_editing');
INSERT INTO laptop_use_cases VALUES ('laptop_018','video_editing');
INSERT INTO laptop_use_cases VALUES ('laptop_018','3d_rendering');
INSERT INTO laptop_use_cases VALUES ('laptop_018','programming');
INSERT INTO laptop_use_cases VALUES ('laptop_018','work');
INSERT INTO laptop_use_cases VALUES ('laptop_018','university');
INSERT INTO laptop_use_cases VALUES ('laptop_019','gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_019','study');
INSERT INTO laptop_use_cases VALUES ('laptop_019','university');
INSERT INTO laptop_use_cases VALUES ('laptop_019','streaming');
INSERT INTO laptop_use_cases VALUES ('laptop_019','everyday');
INSERT INTO laptop_use_cases VALUES ('laptop_020','gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_020','heavy_gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_020','study');
INSERT INTO laptop_use_cases VALUES ('laptop_020','university');
INSERT INTO laptop_use_cases VALUES ('laptop_020','streaming');
INSERT INTO laptop_use_cases VALUES ('laptop_021','gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_021','heavy_gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_021','study');
INSERT INTO laptop_use_cases VALUES ('laptop_021','university');
INSERT INTO laptop_use_cases VALUES ('laptop_021','streaming');
INSERT INTO laptop_use_cases VALUES ('laptop_021','everyday');
INSERT INTO laptop_use_cases VALUES ('laptop_022','gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_022','heavy_gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_022','esports');
INSERT INTO laptop_use_cases VALUES ('laptop_022','streaming');
INSERT INTO laptop_use_cases VALUES ('laptop_022','study');
INSERT INTO laptop_use_cases VALUES ('laptop_023','gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_023','study');
INSERT INTO laptop_use_cases VALUES ('laptop_023','university');
INSERT INTO laptop_use_cases VALUES ('laptop_023','everyday');
INSERT INTO laptop_use_cases VALUES ('laptop_023','portability');
INSERT INTO laptop_use_cases VALUES ('laptop_024','gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_024','heavy_gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_024','esports');
INSERT INTO laptop_use_cases VALUES ('laptop_024','4k_gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_024','streaming');
INSERT INTO laptop_use_cases VALUES ('laptop_024','study');
INSERT INTO laptop_use_cases VALUES ('laptop_025','gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_025','heavy_gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_025','esports');
INSERT INTO laptop_use_cases VALUES ('laptop_025','4k_gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_025','streaming');
INSERT INTO laptop_use_cases VALUES ('laptop_025','design');
INSERT INTO laptop_use_cases VALUES ('laptop_025','video_editing');
INSERT INTO laptop_use_cases VALUES ('laptop_026','gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_026','heavy_gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_026','4k_gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_026','esports');
INSERT INTO laptop_use_cases VALUES ('laptop_026','design');
INSERT INTO laptop_use_cases VALUES ('laptop_026','video_editing');
INSERT INTO laptop_use_cases VALUES ('laptop_026','3d_rendering');
INSERT INTO laptop_use_cases VALUES ('laptop_026','streaming');
INSERT INTO laptop_use_cases VALUES ('laptop_027','gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_027','heavy_gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_027','4k_gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_027','3d_rendering');
INSERT INTO laptop_use_cases VALUES ('laptop_027','machine_learning');
INSERT INTO laptop_use_cases VALUES ('laptop_027','video_editing');
INSERT INTO laptop_use_cases VALUES ('laptop_027','vfx');
INSERT INTO laptop_use_cases VALUES ('laptop_028','gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_028','heavy_gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_028','4k_gaming');
INSERT INTO laptop_use_cases VALUES ('laptop_028','esports');
INSERT INTO laptop_use_cases VALUES ('laptop_028','3d_rendering');
INSERT INTO laptop_use_cases VALUES ('laptop_028','machine_learning');
INSERT INTO laptop_use_cases VALUES ('laptop_028','vfx');
INSERT INTO laptop_use_cases VALUES ('laptop_028','streaming');
