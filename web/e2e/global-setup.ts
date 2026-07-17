/**
 * Global setup: Seeds the database with test data via API.
 * Runs once before all tests.
 * Uses native fetch to avoid Playwright request API CSRF issues.
 */

const API_URL = process.env.E2E_API_URL || "http://localhost:8000";

const TEST_USERS = [
  {
    email: "qa-user@example.com",
    password: "QaTestPass2026!",
    display_name: "QA Standard User",
    tenant_name: "QA Test Org",
  },
  {
    email: "qa-admin@example.com",
    password: "QaAdminPass2026!",
    display_name: "QA Admin User",
    tenant_name: "QA Admin Org",
  },
  {
    email: "qa-team@example.com",
    password: "QaTeamPass2026!",
    display_name: "QA Team Member",
    tenant_name: "QA Team Org",
  },
];

const GROW_TYPES = [
  "DWC",
  "Recirculating DWC",
  "NFT",
  "Ebb & Flow",
  "Aeroponics",
  "Kratky",
  "Coco Coir",
  "Soil",
  "Drip / Top Feed",
  "Rockwool",
  "Outdoor Soil",
  "Outdoor Container",
  "Aquaponics",
  "Living Soil / No-Till",
  "Dutch Bucket (Bato)",
  "Vertical / Tower Garden",
  "Wicking Bed",
];

const TENT_CONFIGS = [
  { name: "Indoor Veg Tent", environment_type: "indoor", size: "4x4" },
  { name: "Indoor Flower Room", environment_type: "indoor", size: "4x8" },
  { name: "Greenhouse Bay", environment_type: "greenhouse", size: "10x10" },
  { name: "Outdoor Plot A", environment_type: "outdoor", size: "8x8" },
  { name: "Small Closet", environment_type: "indoor", size: "2x2" },
  { name: "Outdoor Containers", environment_type: "outdoor", size: "5x5" },
  { name: "NFT System Tent", environment_type: "indoor", size: "3x3" },
  { name: "Aero Chamber", environment_type: "indoor", size: "5x5" },
];

async function globalSetup() {
  console.log("🌱 Tendril QA: Seeding test data...\n");

  // Register test users using native fetch (avoids Playwright request API quirks)
  for (const user of TEST_USERS) {
    try {
      const resp = await fetch(`${API_URL}/v1/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(user),
      });
      if (resp.ok) {
        console.log(`  ✓ Registered: ${user.email}`);
      } else {
        const body = await resp.text();
        if (body.includes("already") || resp.status === 409) {
          console.log(`  ○ Already exists: ${user.email}`);
        } else {
          console.log(`  ✗ Failed to register ${user.email}: ${resp.status} ${body}`);
        }
      }
    } catch {
      console.log(`  ✗ Error registering ${user.email}: ${e}`);
    }
  }

  // Login as admin user to upgrade tenant plan
  const adminLoginResp = await fetch(`${API_URL}/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: TEST_USERS[1].email,
      password: TEST_USERS[1].password,
    }),
  });

  if (adminLoginResp.ok) {
    const adminData = await adminLoginResp.json();
    const adminCookieHeader = adminLoginResp.headers.get("set-cookie") || "";
    const adminCsrfMatch = adminCookieHeader.match(/csrf_token=([^;]+)/);
    const adminCsrf = adminCsrfMatch ? adminCsrfMatch[1] : "";
    const adminHeaders: Record<string, string> = {
      Authorization: `Bearer ${adminData.access_token}`,
      "Content-Type": "application/json",
    };
    if (adminCsrf) {
      adminHeaders["X-CSRF-Token"] = adminCsrf;
      adminHeaders["Cookie"] = `csrf_token=${adminCsrf}`;
    }

    // Get tenant ID from standard user login, then upgrade via admin endpoint
    const stdLoginResp = await fetch(`${API_URL}/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: TEST_USERS[0].email, password: TEST_USERS[0].password }),
    });
    if (stdLoginResp.ok) {
      const stdData = await stdLoginResp.json();
      // Decode JWT to get tenant_id
      const payload = JSON.parse(Buffer.from(stdData.access_token.split(".")[1], "base64url").toString());
      const tenantId = payload.tid;
      if (tenantId) {
        const upgradeResp = await fetch(`${API_URL}/v1/admin/tenants/${tenantId}`, {
          method: "PATCH",
          headers: adminHeaders,
          body: JSON.stringify({ plan: "commercial" }),
        });
        if (upgradeResp.ok) {
          console.log("  ✓ Upgraded QA Org to commercial plan");
        } else {
          console.log(`  ○ Plan upgrade: ${upgradeResp.status} (may already be set)`);
        }
      }
    }
  }

  // Login as the standard user to seed grow data
  const loginResp = await fetch(`${API_URL}/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: TEST_USERS[0].email,
      password: TEST_USERS[0].password,
    }),
  });

  if (!loginResp.ok) {
    console.log(`\n  ✗ Could not login as standard user (${loginResp.status}). Skipping data seed.`);
    return;
  }

  const loginData = await loginResp.json();
  const access_token = loginData.access_token;
  // Get CSRF token from login response cookies
  const setCookieHeader = loginResp.headers.get("set-cookie") || "";
  const csrfMatch = setCookieHeader.match(/csrf_token=([^;]+)/);
  const csrfToken = csrfMatch ? csrfMatch[1] : "";

  const authHeaders: Record<string, string> = {
    Authorization: `Bearer ${access_token}`,
    "Content-Type": "application/json",
  };
  if (csrfToken) {
    authHeaders["X-CSRF-Token"] = csrfToken;
    authHeaders["Cookie"] = `csrf_token=${csrfToken}`;
  }

  // Create tents/grow spaces
  const tentIds: string[] = [];
  for (const tent of TENT_CONFIGS) {
    try {
      const resp = await fetch(`${API_URL}/v1/tents`, {
        method: "POST",
        headers: authHeaders,
        body: JSON.stringify(tent),
      });
      if (resp.ok) {
        const data = await resp.json();
        tentIds.push(data.id);
        console.log(`  ✓ Created tent: ${tent.name}`);
      } else {
        const body = await resp.text();
        if (body.includes("already") || resp.status === 409) {
          console.log(`  ○ Tent exists: ${tent.name}`);
        } else {
          console.log(`  ✗ Tent creation failed: ${tent.name} - ${resp.status} ${body.slice(0, 80)}`);
        }
      }
    } catch {
      console.log(`  ✗ Error creating tent ${tent.name}: ${e}`);
    }
  }

  // Create one grow per grow type (if tents were created)
  if (tentIds.length > 0) {
    for (let i = 0; i < GROW_TYPES.length; i++) {
      const growType = GROW_TYPES[i];
      const tentId = tentIds[i % tentIds.length];
      try {
        const resp = await fetch(`${API_URL}/v1/grows`, {
          method: "POST",
          headers: authHeaders,
          body: JSON.stringify({
            name: `QA ${growType} Grow`,
            tent_id: tentId,
            grow_type: growType,
          }),
        });
        if (resp.ok) {
          console.log(`  ✓ Created grow: QA ${growType} Grow`);
        } else {
          const body = await resp.text();
          console.log(`  ○ Grow: ${growType} - ${resp.status} ${body.slice(0, 80)}`);
        }
      } catch {
        console.log(`  ✗ Error creating grow ${growType}: ${e}`);
      }
    }
  }

  // Create a strain for reference
  try {
    const resp = await fetch(`${API_URL}/v1/strains`, {
      method: "POST",
      headers: authHeaders,
      body: JSON.stringify({
        name: "QA Test Strain",
        breeder: "QA Genetics",
        type: "Hybrid",
        flowering_weeks_min: 8,
        flowering_weeks_max: 10,
      }),
    });
    if (resp.ok) {
      console.log("  ✓ Created strain: QA Test Strain");
    }
  } catch {
    // non-critical
  }

  console.log("\n🌱 Tendril QA: Seed complete.\n");
}

export default globalSetup;
