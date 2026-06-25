import type { components } from "@/lib/api-types";

import { getCsrfToken, setCsrfToken, clearAuth } from "@/lib/auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/v1";

interface FetchOptions extends RequestInit {
  token?: string;
  /** Number of retry attempts for transient failures (default: 2 for GET, 0 for mutations) */
  retries?: number;
  /** Request timeout in ms (default: 15000) */
  timeout?: number;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
    this.name = "ApiError";
  }
}

const _UNSAFE_METHODS = new Set(["POST", "PUT", "PATCH", "DELETE"]);
const _RETRYABLE_STATUSES = new Set([502, 503, 504, 408, 429]);
const _DEFAULT_TIMEOUT = 15_000;

/** Delay helper for exponential backoff */
function backoff(attempt: number): Promise<void> {
  const ms = Math.min(1000 * 2 ** attempt, 8000) + Math.random() * 500;
  return new Promise((r) => setTimeout(r, ms));
}

export async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { token, retries: userRetries, timeout: userTimeout, ...fetchOptions } = options;

  const method = (fetchOptions.method || "GET").toUpperCase();

  const headers: Record<string, string> = {
    // Only set Content-Type for methods that send a body (avoids unnecessary CORS preflights on GET)
    ...(!["GET", "HEAD"].includes(method) ? { "Content-Type": "application/json" } : {}),
    ...(options.headers as Record<string, string>),
  };

  // Legacy support: if an explicit token is passed (and it's a real JWT), use Authorization header
  if (token && token !== "cookie") {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Attach CSRF token for unsafe methods
  if (_UNSAFE_METHODS.has(method)) {
    const csrf = getCsrfToken();
    if (csrf) {
      headers["X-CSRF-Token"] = csrf;
    }
  }

  const url = `${API_BASE}${path}`;
  const maxRetries = userRetries ?? (_UNSAFE_METHODS.has(method) ? 0 : 2);
  const timeoutMs = userTimeout ?? _DEFAULT_TIMEOUT;

  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    if (attempt > 0) {
      await backoff(attempt - 1);
    }

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    let res: Response;
    try {
      res = await fetch(url, {
        ...fetchOptions,
        headers,
        credentials: "include",
        signal: controller.signal,
      });
    } catch (networkErr) {
      clearTimeout(timer);
      lastError = networkErr instanceof Error ? networkErr : new Error("Network error");
      if (attempt < maxRetries) {
        console.warn(`[apiFetch] Retry ${attempt + 1}/${maxRetries} for ${method} ${path}:`, lastError.message);
        continue;
      }
      const msg = controller.signal.aborted ? "Request timed out" : lastError.message;
      throw new ApiError(0, `Network error on ${method} ${path}: ${msg}`);
    } finally {
      clearTimeout(timer);
    }

    // Retry on transient server errors for safe methods
    if (_RETRYABLE_STATUSES.has(res.status) && attempt < maxRetries) {
      console.warn(`[apiFetch] Retry ${attempt + 1}/${maxRetries} for ${method} ${path}: HTTP ${res.status}`);
      continue;
    }

    // Capture CSRF token from response header (set on login/register/refresh)
    const csrfHeader = res.headers.get("X-CSRF-Token");
    if (csrfHeader) {
      setCsrfToken(csrfHeader);
    }

    // Auto-refresh on 401
    if (res.status === 401) {
      try {
        const refreshRes = await fetch(`${API_BASE}/auth/refresh`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
          credentials: "include",
        });
        if (refreshRes.ok) {
          const newCsrf = refreshRes.headers.get("X-CSRF-Token");
          if (newCsrf) setCsrfToken(newCsrf);

          if (_UNSAFE_METHODS.has(method)) {
            const csrf = getCsrfToken();
            if (csrf) headers["X-CSRF-Token"] = csrf;
          }

          const retryRes = await fetch(`${API_BASE}${path}`, {
            ...fetchOptions,
            headers,
            credentials: "include",
          });
          if (retryRes.ok) {
            if (retryRes.status === 204) return undefined as T;
            return retryRes.json();
          }
          const retryBody = await retryRes.json().catch(() => ({ detail: retryRes.statusText }));
          throw new ApiError(retryRes.status, retryBody.detail || retryRes.statusText);
        } else {
          clearAuth();
          throw new ApiError(401, "Session expired. Please log in again.");
        }
      } catch (refreshErr) {
        if (refreshErr instanceof ApiError) throw refreshErr;
        clearAuth();
        throw new ApiError(401, "Session expired. Please log in again.");
      }
    }

    if (!res.ok) {
      const body = await res.json().catch(() => ({ detail: res.statusText }));
      throw new ApiError(res.status, body.detail || res.statusText);
    }

    if (res.status === 204) return undefined as T;
    return res.json();
  }

  // Should not reach here, but satisfy TypeScript
  throw lastError ?? new ApiError(0, `Failed after ${maxRetries + 1} attempts: ${method} ${path}`);
}

// Paginated response envelope from the API
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// Auth
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export function register(data: {
  email: string;
  password: string;
  display_name: string;
  tenant_name: string;
}) {
  return apiFetch<TokenResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function login(email: string, password: string) {
  return apiFetch<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function refreshToken(refresh_token: string) {
  return apiFetch<TokenResponse>("/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token }),
  });
}

export function logout() {
  return apiFetch<{ message: string }>("/auth/logout", {
    method: "POST",
  });
}

export function getMe(token: string) {
  return apiFetch<{ id: string; email: string; display_name: string | null; role: string; tenant_id: string; is_platform_admin: boolean; is_support: boolean; layout_mode: string }>(
    "/auth/me",
    { token },
  );
}

// Tenant
export function getMyTenant(token: string) {
  return apiFetch<{ id: string; name: string; slug: string; plan: string }>(
    "/tenants/me",
    { token },
  );
}

export function updateMyTenant(token: string, data: { name?: string }) {
  return apiFetch<{ id: string; name: string; slug: string; plan: string }>(
    "/tenants/me",
    { method: "PATCH", body: JSON.stringify(data), token },
  );
}

// Tenant Members (Owner user management)
export interface TenantMember {
  id: string;
  email: string;
  display_name: string | null;
  role: string;
  email_verified: boolean;
  created_at: string;
}

export async function listTenantMembers(token: string) {
  const res = await apiFetch<PaginatedResponse<TenantMember>>("/tenants/members", { token });
  return res.items;
}

export function addTenantMember(token: string, data: { email: string; display_name?: string; password: string; role?: string }) {
  return apiFetch<TenantMember>("/tenants/members", { method: "POST", body: JSON.stringify(data), token });
}

export function updateMemberRole(token: string, memberId: string, role: string) {
  return apiFetch<TenantMember>(`/tenants/members/${memberId}`, { method: "PATCH", body: JSON.stringify({ role }), token });
}

export function removeTenantMember(token: string, memberId: string) {
  return apiFetch<void>(`/tenants/members/${memberId}`, { method: "DELETE", token });
}

// Profile
export function updateProfile(token: string, data: { display_name?: string; email?: string; layout_mode?: string; preferences?: Record<string, unknown> }) {
  return apiFetch<{ id: string; email: string; display_name: string | null; role: string; tenant_id: string; is_platform_admin: boolean; is_support: boolean; layout_mode: string; preferences: Record<string, unknown> }>(
    "/auth/profile",
    { method: "PATCH", body: JSON.stringify(data), token },
  );
}

export function changePassword(token: string, data: { current_password: string; new_password: string }) {
  return apiFetch<{ message: string }>("/auth/change-password", { method: "POST", body: JSON.stringify(data), token });
}

// Devices
export interface DeviceResponse {
  id: string;
  device_id: string;
  label: string | null;
  tent_id: string | null;
  status: string;
  last_seen: string | null;
  firmware_version: string | null;
}

export interface DeviceRegisterResponse extends DeviceResponse {
  psk: string;
}

export async function listDevices(token: string) {
  const res = await apiFetch<PaginatedResponse<DeviceResponse>>("/devices", { token });
  return res.items;
}

export function getDevice(token: string, deviceId: string) {
  return apiFetch<DeviceResponse>(`/devices/${deviceId}`, { token });
}

export function registerDevice(token: string, label?: string) {
  return apiFetch<DeviceRegisterResponse>("/devices/register", {
    method: "POST",
    body: JSON.stringify({ label }),
    token,
  });
}

export function pairDevice(token: string, data: { device_id: string; psk: string; tent_id?: string }) {
  return apiFetch<DeviceResponse>("/devices/pair", {
    method: "POST",
    body: JSON.stringify(data),
    token,
  });
}

export function updateDevice(token: string, deviceId: string, data: { label?: string; tent_id?: string; unassign_tent?: boolean }) {
  return apiFetch<DeviceResponse>(`/devices/${deviceId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
    token,
  });
}

export function revokeDevice(token: string, deviceId: string) {
  return apiFetch<DeviceResponse>(`/devices/${deviceId}/revoke`, {
    method: "POST",
    token,
  });
}

export function deleteDevice(token: string, deviceId: string) {
  return apiFetch<void>(`/devices/${deviceId}`, {
    method: "DELETE",
    token,
  });
}

export function getDeviceQrUrl(deviceId: string) {
  return `${API_BASE}/devices/${deviceId}/qr`;
}

// Grow Types
export interface GrowTypeSummary {
  id: string;
  name: string;
  category: string;
  description: string;
}

export function listGrowTypes(token: string) {
  return apiFetch<GrowTypeSummary[]>("/grow-types", { token });
}

export function getGrowType(token: string, id: string) {
  return apiFetch<Record<string, unknown>>(`/grow-types/${id}`, { token });
}

// Grow Type Configuration (stage-by-stage guides)
export interface RangeTarget {
  min: number;
  max: number;
  target?: number;
}

export interface StageEnvironment {
  temp_day_f: RangeTarget;
  temp_night_f: RangeTarget;
  humidity_pct: RangeTarget;
  vpd_kpa: RangeTarget | null;
  light_hours: number;
  light_ppfd: number | RangeTarget;
  light_dli: number | RangeTarget;
  notes: string;
}

export interface StageReservoir {
  ph: RangeTarget;
  ec: RangeTarget;
  ppm_500: RangeTarget;
  water_temp_f: RangeTarget;
  dissolved_oxygen_ppm: { min: number; target: number };
  change_interval_days: number | null;
  hydroguard_ml_per_gal: number;
  notes: string;
}

export interface StageSupplement {
  name: string;
  dose_ml_per_gal: number;
  purpose: string;
}

export interface StageNutrients {
  strength_pct: number;
  approach: string;
  flora_micro_ml_per_gal: number;
  flora_gro_ml_per_gal: number;
  flora_bloom_ml_per_gal: number;
  calmag_ml_per_gal: number;
  supplements: StageSupplement[];
}

export interface StageTask {
  name: string;
  description: string;
  interval_days: number | null;
  priority: string;
}

export interface StageProblem {
  issue: string;
  cause: string;
  solution: string;
}

export interface StageTraining {
  technique: string;
  when: string;
  description: string;
}

export interface GrowStageConfig {
  id: string;
  name: string;
  order: number;
  duration_days: { min: number; max: number; typical: number };
  description: string;
  environment: StageEnvironment;
  reservoir: StageReservoir | null;
  nutrients: StageNutrients | null;
  tasks: StageTask[];
  health_checks: string[];
  common_problems: StageProblem[];
  training: StageTraining[];
  transition_signals: string[];
  environment_variants?: {
    [env: string]: {
      environment_overrides?: Record<string, unknown>;
      reservoir_overrides?: Record<string, unknown>;
      extra_tasks?: StageTask[];
      extra_problems?: StageProblem[];
      notes?: string;
    };
  };
}

export interface EquipmentChecklistItem {
  name: string;
  category: string;
  description: string;
}

export interface TroubleshootingProblem {
  symptom: string;
  diagnosis: string;
  severity: string;
  causes: string[];
  solutions: string[];
}

export interface TroubleshootingCategory {
  category: string;
  problems: TroubleshootingProblem[];
}

export interface GrowTypeConfig {
  grow_type_id: string;
  version: string;
  stages: GrowStageConfig[];
  equipment: EquipmentChecklistItem[];
  quick_reference: Record<string, unknown>;
  troubleshooting: TroubleshootingCategory[];
  total_grow_days: { min: number; max: number; typical_photo: number; typical_auto: number; breakdown: string };
}

export function getGrowTypeConfig(token: string, growTypeId: string) {
  return apiFetch<GrowTypeConfig>(`/grow-types/${growTypeId}/config`, { token });
}

// Tents
export interface EquipmentItem {
  type: string;
  brand?: string;
  model?: string;
  specs?: string;
  quantity: number;
}

export interface TentResponse {
  id: string;
  name: string;
  environment_type: string;
  size: string | null;
  latitude: number | null;
  longitude: number | null;
  camera_url: string | null;
  equipment: EquipmentItem[] | null;
  notes: string | null;
}

export async function listTents(token: string) {
  const res = await apiFetch<PaginatedResponse<TentResponse>>("/tents", { token });
  return res.items;
}

export function getTent(token: string, id: string) {
  return apiFetch<TentResponse>(`/tents/${id}`, { token });
}

export function createTent(token: string, data: { name: string; environment_type?: string; size?: string; latitude?: number; longitude?: number; camera_url?: string; equipment?: EquipmentItem[]; notes?: string }) {
  return apiFetch<TentResponse>("/tents", { method: "POST", body: JSON.stringify(data), token });
}

export function updateTent(token: string, id: string, data: Partial<{ name: string; environment_type: string; size: string | null; latitude: number | null; longitude: number | null; camera_url: string | null; equipment: EquipmentItem[]; notes: string | null }>) {
  return apiFetch<TentResponse>(`/tents/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deleteTent(token: string, id: string) {
  return apiFetch<void>(`/tents/${id}`, { method: "DELETE", token });
}

// Tent Cameras
export interface CameraResponse {
  id: string;
  tent_id: string;
  label: string;
  camera_type: string;
  url: string;
  sort_order: number;
  is_primary: boolean;
  created_at: string;
}

export function listTentCameras(token: string, tentId: string) {
  return apiFetch<CameraResponse[]>(`/tents/${tentId}/cameras`, { token });
}

export function createTentCamera(token: string, tentId: string, data: { label: string; camera_type?: string; url: string; is_primary?: boolean }) {
  return apiFetch<CameraResponse>(`/tents/${tentId}/cameras`, { method: "POST", body: JSON.stringify(data), token });
}

export function updateTentCamera(token: string, tentId: string, cameraId: string, data: Partial<{ label: string; url: string; camera_type: string; is_primary: boolean }>) {
  return apiFetch<CameraResponse>(`/tents/${tentId}/cameras/${cameraId}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deleteTentCamera(token: string, tentId: string, cameraId: string) {
  return apiFetch<void>(`/tents/${tentId}/cameras/${cameraId}`, { method: "DELETE", token });
}

export function getCameraSnapshot(token: string, tentId: string, cameraId?: string) {
  const q = cameraId ? `?camera_id=${cameraId}` : "";
  return apiFetch<{ image_base64: string; timestamp: string }>(`/tents/${tentId}/camera-snapshot-b64${q}`, { token, retries: 0 });
}

// Grows
export interface GrowResponse {
  id: string;
  tent_id: string;
  name: string;
  grow_type: string;
  status: string;
  stage: string;
  started_at: string;
  ended_at: string | null;
  notes: string | null;
  milestones: Record<string, string> | null;
  settings: Record<string, unknown> | null;
  auto_health_check: boolean;
}

export async function listGrows(token: string, params?: { status?: string; tent_id?: string }) {
  const qs = new URLSearchParams();
  if (params?.status) qs.set("status", params.status);
  if (params?.tent_id) qs.set("tent_id", params.tent_id);
  const q = qs.toString();
  const res = await apiFetch<PaginatedResponse<GrowResponse>>(`/grows${q ? `?${q}` : ""}`, { token });
  return res.items;
}

export function createGrow(token: string, data: { tent_id: string; name: string; grow_type: string; stage?: string }) {
  return apiFetch<GrowResponse>("/grows", { method: "POST", body: JSON.stringify(data), token });
}

export function getGrow(token: string, id: string) {
  return apiFetch<GrowResponse>(`/grows/${id}`, { token });
}

export function updateGrow(token: string, id: string, data: Partial<{ name: string; stage: string; status: string; notes: string; started_at: string; milestones: Record<string, string>; settings: Record<string, unknown>; auto_health_check: boolean }>) {
  return apiFetch<GrowResponse>(`/grows/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deleteGrow(token: string, id: string) {
  return apiFetch<void>(`/grows/${id}`, { method: "DELETE", token });
}

// Buckets
export interface StrainSummary {
  id: string;
  name: string;
  breeder: string | null;
  genetics: string | null;
  flowering_days: number | null;
  thc_pct: number | null;
  cbd_pct: number | null;
  terpene_profile: Record<string, number> | null;
}

export interface BucketResponse {
  id: string;
  grow_cycle_id: string;
  position: number;
  label: string | null;
  strain_name: string | null;
  strain_id: string | null;
  strain: StrainSummary | null;
  growth_stage: string;
  status: string;
  volume_gallons: number | null;
  role: string;
  settings: Record<string, unknown> | null;
  last_water_change_at: string | null;
}

export async function listBuckets(token: string, growCycleId?: string) {
  const q = growCycleId ? `?grow_cycle_id=${growCycleId}` : "";
  const res = await apiFetch<PaginatedResponse<BucketResponse>>(`/buckets${q}`, { token });
  return res.items;
}

export function createBucket(token: string, data: { grow_cycle_id: string; label?: string; strain_name?: string; strain_id?: string; position?: number; volume_gallons?: number; role?: string }) {
  return apiFetch<BucketResponse>("/buckets", { method: "POST", body: JSON.stringify(data), token });
}

export function updateBucket(token: string, id: string, data: Partial<{ label: string; strain_name: string; strain_id: string; growth_stage: string; status: string; volume_gallons: number; role: string }>) {
  return apiFetch<BucketResponse>(`/buckets/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deleteBucket(token: string, id: string) {
  return apiFetch<void>(`/buckets/${id}`, { method: "DELETE", token });
}

// Sensors
export interface SensorReadingResponse {
  id: string;
  bucket_id: string;
  device_id: string | null;
  water_temp_f: number | null;
  ph: number | null;
  ec: number | null;
  ppm: number | null;
  water_level_pct: number | null;
  dissolved_oxygen: number | null;
  orp: number | null;
  salinity: number | null;
  specific_gravity: number | null;
  battery_pct: number | null;
  flow_rate: number | null;
  mist_pressure: number | null;
  soil_moisture: number | null;
  soil_temp: number | null;
  runoff_ph: number | null;
  runoff_ec: number | null;
  ambient_temp_f: number | null;
  ambient_humidity: number | null;
  recorded_at: string;
}

export async function listSensorReadings(token: string, bucketId?: string, limit?: number) {
  const qs = new URLSearchParams();
  if (bucketId) qs.set("bucket_id", bucketId);
  if (limit) qs.set("page_size", String(limit));
  const q = qs.toString();
  const res = await apiFetch<PaginatedResponse<SensorReadingResponse>>(`/sensors${q ? `?${q}` : ""}`, { token });
  return res.items;
}

export function getLatestReading(token: string, bucketId: string) {
  return apiFetch<SensorReadingResponse | null>(`/sensors/latest/${bucketId}`, { token });
}

export function getSensorDrift(token: string, bucketId: string, hours?: number) {
  const q = hours ? `?hours=${hours}` : "";
  return apiFetch<{ bucket_id: string; hours: number; ph: { min: number; max: number; first: number; last: number; delta: number; count: number } | null; ec: { min: number; max: number; first: number; last: number; delta: number; count: number } | null }>(`/sensors/drift/${bucketId}${q}`, { token });
}

export function createSensorReading(token: string, data: {
  bucket_id: string;
  ph?: number;
  ec?: number;
  ppm?: number;
  water_temp_f?: number;
  water_level_pct?: number;
  dissolved_oxygen?: number;
  orp?: number;
  salinity?: number;
  specific_gravity?: number;
  battery_pct?: number;
  flow_rate?: number;
  mist_pressure?: number;
  soil_moisture?: number;
  soil_temp?: number;
  runoff_ph?: number;
  runoff_ec?: number;
}) {
  return apiFetch<SensorReadingResponse>("/sensors", { method: "POST", body: JSON.stringify(data), token });
}

// Tent Sensor Readings (ambient temp & humidity — tent-level, shared across buckets)
export interface TentReadingResponse {
  id: string;
  tent_id: string;
  device_id: string | null;
  ambient_temp_f: number | null;
  ambient_humidity: number | null;
  recorded_at: string;
}

export async function listTentReadings(token: string, tentId?: string, limit?: number) {
  const qs = new URLSearchParams();
  if (tentId) qs.set("tent_id", tentId);
  if (limit) qs.set("limit", String(limit));
  const q = qs.toString();
  const res = await apiFetch<PaginatedResponse<TentReadingResponse>>(`/tent-sensors${q ? `?${q}` : ""}`, { token });
  return res.items;
}

export function getLatestTentReading(token: string, tentId: string) {
  return apiFetch<TentReadingResponse | null>(`/tent-sensors/latest/${tentId}`, { token });
}

export function createTentReading(token: string, data: {
  tent_id: string;
  ambient_temp_f?: number;
  ambient_humidity?: number;
}) {
  return apiFetch<TentReadingResponse>("/tent-sensors", { method: "POST", body: JSON.stringify(data), token });
}

// Feeding Schedules
export interface FeedingScheduleResponse {
  id: string;
  grow_cycle_id: string;
  name: string;
  stage: string;
  nutrients: { name: string; brand?: string; ml_per_gallon?: number; strength_pct?: number }[];
  target_ppm: number | null;
  target_ec: number | null;
  notes: string | null;
}

export async function listFeedingSchedules(token: string, growCycleId: string) {
  const res = await apiFetch<PaginatedResponse<FeedingScheduleResponse>>(`/feeding/feeding?grow_cycle_id=${growCycleId}`, { token });
  return res.items;
}

export function createFeedingSchedule(token: string, data: { grow_cycle_id: string; name: string; stage: string; nutrients: object[]; target_ppm?: number; target_ec?: number; notes?: string }) {
  return apiFetch<FeedingScheduleResponse>("/feeding/feeding", { method: "POST", body: JSON.stringify(data), token });
}

export function updateFeedingSchedule(token: string, id: string, data: Partial<{ name: string; stage: string; nutrients: object[]; target_ppm: number | null; target_ec: number | null; notes: string }>) {
  return apiFetch<FeedingScheduleResponse>(`/feeding/feeding/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deleteFeedingSchedule(token: string, id: string) {
  return apiFetch<void>(`/feeding/feeding/${id}`, { method: "DELETE", token });
}

// Feeding Advice (AI-powered)
export interface FeedingAdviceResponse {
  current_stage_advice: string | null;
  adjustments: { schedule_name: string; change: string; reason: string }[];
  alerts: { severity: string; message: string; type: string }[];
  next_transition: { stage: string; action: string; estimated_timing: string } | null;
  health_impact: string | null;
}

export function getFeedingAdvice(token: string, growId: string) {
  return apiFetch<FeedingAdviceResponse>(`/ai/feeding-advice/${growId}`, { token });
}

// Journal Entries
export interface JournalEntryResponse {
  id: string;
  bucket_id: string;
  event_type: string;
  content: string | null;
  payload: Record<string, unknown> | null;
  created_at: string;
}

export async function listJournalEntries(token: string, bucketId?: string, eventType?: string) {
  const qs = new URLSearchParams();
  if (bucketId) qs.set("bucket_id", bucketId);
  if (eventType) qs.set("event_type", eventType);
  const q = qs.toString();
  const res = await apiFetch<PaginatedResponse<JournalEntryResponse>>(`/journal${q ? `?${q}` : ""}`, { token });
  return res.items;
}

export async function listJournalReports(token: string, limit = 14) {
  return apiFetch<JournalEntryResponse[]>(`/journal/reports?limit=${limit}`, { token });
}

export function createJournalEntry(token: string, data: { bucket_id: string; event_type: string; content?: string; payload?: object }) {
  return apiFetch<JournalEntryResponse>("/journal", { method: "POST", body: JSON.stringify(data), token });
}

export function deleteJournalEntry(token: string, id: string) {
  return apiFetch<void>(`/journal/${id}`, { method: "DELETE", token });
}

export function updateJournalEntry(token: string, id: string, data: Partial<{ event_type: string; content: string; payload: object }>) {
  return apiFetch<JournalEntryResponse>(`/journal/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export interface QuickJournalCreate {
  bucket_id: string;
  event_type: string;
  content?: string;
  payload?: object;
  ph?: number;
  ec?: number;
  ppm?: number;
  water_temp_f?: number;
  volume_gallons?: number;
}

export interface QuickJournalResponse {
  journal: JournalEntryResponse;
  reading_id: string | null;
}

export function createQuickJournalEntry(token: string, data: QuickJournalCreate) {
  return apiFetch<QuickJournalResponse>("/journal/quick", { method: "POST", body: JSON.stringify(data), token });
}

// Strains
export interface StrainResponse {
  id: string;
  name: string;
  breeder: string | null;
  genetics: string | null;
  flowering_days: number | null;
  thc_pct: number | null;
  cbd_pct: number | null;
  terpene_profile: Record<string, number> | null;
  notes: string | null;
  is_global: boolean;
}

export async function listStrains(token: string) {
  const res = await apiFetch<PaginatedResponse<StrainResponse>>("/strains", { token });
  return res.items;
}

export function createStrain(token: string, data: { name: string; breeder?: string; genetics?: string; flowering_days?: number }) {
  return apiFetch<StrainResponse>("/strains", { method: "POST", body: JSON.stringify(data), token });
}

export function updateStrain(token: string, id: string, data: Partial<{ name: string; breeder: string; genetics: string }>) {
  return apiFetch<StrainResponse>(`/strains/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deleteStrain(token: string, id: string) {
  return apiFetch<void>(`/strains/${id}`, { method: "DELETE", token });
}

export interface FeedingSuggestion {
  stage: string;
  target_ec: number;
  target_ppm: number;
  notes: string;
}

export function getStrainFeedingSuggestions(token: string, strainId: string) {
  return apiFetch<FeedingSuggestion[]>(`/strains/${strainId}/feeding-suggestions`, { token });
}

export interface HarvestCountdownItem {
  grow_id: string;
  grow_name: string;
  bucket_id: string;
  bucket_label: string | null;
  strain_name: string | null;
  flowering_days: number;
  flowering_start: string;
  estimated_harvest: string;
  days_remaining: number;
}

export function getHarvestCountdown(token: string) {
  return apiFetch<HarvestCountdownItem[]>("/grows/harvest-countdown", { token });
}

export interface StrainGrowComparison {
  grow_id: string;
  grow_name: string;
  grow_type: string;
  bucket_count: number;
  avg_dry_weight_g: number | null;
  avg_quality: number | null;
  total_dry_weight_g: number | null;
  grow_duration_days: number | null;
}

export function getStrainComparison(token: string, strainId: string) {
  return apiFetch<StrainGrowComparison[]>(`/strains/${strainId}/comparison`, { token });
}

export function getStrainLeaderboard(token: string) {
  return apiFetch<{ strain_name: string; harvests: number; avg_dry_weight_g: number | null; avg_quality: number | null }[]>(
    "/strains/leaderboard",
    { token },
  );
}

// Yields
export interface YieldResponse {
  id: string;
  bucket_id: string;
  wet_weight_g: number | null;
  dry_weight_g: number | null;
  trim_weight_g: number | null;
  quality_rating: number | null;
  terpene_notes: string | null;
  harvest_date: string | null;
  dry_start: string | null;
  dry_end: string | null;
  cure_start: string | null;
  cure_end: string | null;
  dry_environment: Record<string, unknown> | null;
  notes: string | null;
}

export async function listYields(token: string, bucketId?: string) {
  const q = bucketId ? `?bucket_id=${bucketId}` : "";
  return apiFetch<YieldResponse[]>(`/yields${q}`, { token });
}

export function createYield(token: string, data: {
  bucket_id: string; wet_weight_g?: number; dry_weight_g?: number; trim_weight_g?: number;
  quality_rating?: number; terpene_notes?: string; harvest_date?: string;
  dry_start?: string; dry_end?: string; cure_start?: string; cure_end?: string;
  dry_environment?: Record<string, unknown>; notes?: string;
}) {
  return apiFetch<YieldResponse>("/yields", { method: "POST", body: JSON.stringify(data), token });
}

export function updateYield(token: string, id: string, data: Partial<{
  wet_weight_g: number; dry_weight_g: number; trim_weight_g: number;
  quality_rating: number; terpene_notes: string; harvest_date: string;
  dry_start: string; dry_end: string; cure_start: string; cure_end: string; notes: string;
}>) {
  return apiFetch<YieldResponse>(`/yields/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deleteYield(token: string, id: string) {
  return apiFetch<void>(`/yields/${id}`, { method: "DELETE", token });
}

// Weather
export function getCurrentWeather(token: string, tentId: string) {
  return apiFetch<{ current: Record<string, unknown>; alerts: unknown[] }>(`/weather/${tentId}/current`, { token });
}

export function getWeatherForecast(token: string, tentId: string) {
  return apiFetch<{ forecast: unknown[] }>(`/weather/${tentId}/forecast`, { token });
}

export function getWeatherHistory(token: string, tentId: string, limit?: number) {
  const q = limit ? `?limit=${limit}` : "";
  return apiFetch<Array<{ temperature_c: number; humidity_pct: number; precipitation_mm: number | null; wind_speed_kmh: number | null; uv_index: number | null; recorded_at: string }>>(
    `/weather/${tentId}/history${q}`, { token },
  );
}

// Photos
export interface PhotoResponse {
  id: string;
  bucket_id: string;
  url: string;
  caption: string | null;
  created_at: string;
}

export async function listPhotos(token: string, bucketId: string) {
  const res = await apiFetch<PaginatedResponse<PhotoResponse>>(`/photos?bucket_id=${bucketId}`, { token });
  return res.items;
}

export function createPhoto(token: string, data: { bucket_id: string; url: string; caption?: string }) {
  return apiFetch<PhotoResponse>("/photos", { method: "POST", body: JSON.stringify(data), token });
}

export function updatePhoto(token: string, id: string, data: Partial<{ caption: string }>) {
  return apiFetch<PhotoResponse>(`/photos/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deletePhoto(token: string, id: string) {
  return apiFetch<void>(`/photos/${id}`, { method: "DELETE", token });
}

// Grow Photos (S3 file uploads)
export interface GrowPhotoResponse {
  id: string;
  grow_cycle_id: string;
  bucket_id: string | null;
  source: string;
  caption: string | null;
  created_at: string;
  url: string | null;
}

export async function listGrowPhotos(token: string, growCycleId: string) {
  const res = await apiFetch<PaginatedResponse<GrowPhotoResponse>>(`/photos/grow?grow_cycle_id=${growCycleId}`, { token });
  return res.items;
}

export async function uploadGrowPhoto(
  token: string,
  file: File,
  growCycleId: string,
  bucketId?: string,
  caption?: string,
): Promise<GrowPhotoResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("grow_cycle_id", growCycleId);
  if (bucketId) form.append("bucket_id", bucketId);
  if (caption) form.append("caption", caption);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/v1";
  const headers: Record<string, string> = {};
  const csrf = getCsrfToken();
  if (csrf) headers["X-CSRF-Token"] = csrf;
  const res = await fetch(`${API_BASE_URL}/photos/grow`, {
    method: "POST",
    headers,
    credentials: "include",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export function growPhotoUrl(token: string, photoId: string) {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/v1";
  return `${API_BASE_URL}/photos/grow/file/${photoId}`;
}

export function updateGrowPhoto(token: string, id: string, data: Partial<{ caption: string }>) {
  return apiFetch<GrowPhotoResponse>(`/photos/grow/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deleteGrowPhoto(token: string, id: string) {
  return apiFetch<void>(`/photos/grow/${id}`, { method: "DELETE", token });
}

export function timelapseUrl(token: string, growCycleId: string) {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/v1";
  return `${API_BASE_URL}/photos/grow/timelapse/${growCycleId}`;
}

// Dose Profiles
export interface DoseProfileResponse {
  id: string;
  grow_cycle_id: string;
  name: string;
  dose_type: string;
  dose_ml: number;
  enabled: boolean;
  settings: Record<string, unknown> | null;
}

export async function listDoseProfiles(token: string, growCycleId: string) {
  const res = await apiFetch<PaginatedResponse<DoseProfileResponse>>(`/feeding/doses?grow_cycle_id=${growCycleId}`, { token });
  return res.items;
}

export function createDoseProfile(token: string, data: { grow_cycle_id: string; name: string; dose_type: string; dose_ml: number; enabled?: boolean }) {
  return apiFetch<DoseProfileResponse>("/feeding/doses", { method: "POST", body: JSON.stringify(data), token });
}

export function updateDoseProfile(token: string, id: string, data: Partial<{ name: string; dose_ml: number; enabled: boolean; settings: Record<string, unknown> }>) {
  return apiFetch<DoseProfileResponse>(`/feeding/doses/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deleteDoseProfile(token: string, id: string) {
  return apiFetch<void>(`/feeding/doses/${id}`, { method: "DELETE", token });
}

// Data Export
export function getExportUrl(token: string, bucketId: string) {
  return `${API_BASE}/data/export/bucket/${bucketId}?token=${encodeURIComponent(token)}`;
}

export function getGrowExportUrl(token: string, growId: string, sections?: string[]) {
  const params = new URLSearchParams({ token });
  if (sections) sections.forEach((s) => params.append("include", s));
  return `${API_BASE}/data/export/grow/${growId}?${params.toString()}`;
}

export function getAllExportUrl(token: string) {
  return `${API_BASE}/data/export/all?token=${encodeURIComponent(token)}`;
}

export function getBucketExportUrl(token: string, bucketId: string, start?: string, end?: string) {
  const params = new URLSearchParams({ token });
  if (start) params.set("start", start);
  if (end) params.set("end", end);
  return `${API_BASE}/data/export/bucket/${bucketId}?${params.toString()}`;
}

export function getGrowReportPdfUrl(token: string, growId: string) {
  return `${API_BASE}/data/export/grow/${growId}/report?token=${encodeURIComponent(token)}`;
}

// Notification Preferences
export interface NotificationPreference {
  id: string;
  channel_id: string;
  severity_filter: string;
  event_types: string;
  enabled: boolean;
}

export function listNotificationPreferences(token: string) {
  return apiFetch<NotificationPreference[]>("/notifications/preferences", { token });
}

export function createNotificationPreference(token: string, data: { channel_id: string; severity_filter?: string; event_types?: string }) {
  return apiFetch<NotificationPreference>("/notifications/preferences", { method: "POST", body: JSON.stringify(data), token });
}

export function deleteNotificationPreference(token: string, id: string) {
  return apiFetch<void>(`/notifications/preferences/${id}`, { method: "DELETE", token });
}

// Grow Cloning (client-side — no backend endpoint)
// Use createGrow + createBucket + createFeedingSchedule to clone

// Reference data
export function searchReferenceStrains(token: string, query: string) {
  return apiFetch<{ id: string; name: string; breeder: string | null; genetics: string | null }[]>(
    `/reference/strains?q=${encodeURIComponent(query)}`,
    { token },
  );
}

export function searchNutrients(token: string, query: string) {
  return apiFetch<{ id: string; barcode: string; name: string; brand: string | null; npk: string | null; nutrients: Record<string, unknown> | null }[]>(
    `/reference/nutrients?q=${encodeURIComponent(query)}`,
    { token },
  );
}

// AI
export function getAiChatWsUrl() {
  const base = API_BASE.replace(/^http/, "ws");
  return `${base}/ai/chat`;
}

export type AgentActionResponse = components["schemas"]["AgentActionResponse"];
export type AgentActionDetailResponse = components["schemas"]["AgentActionDetailResponse"];
export type PaginatedAgentActionResponse = components["schemas"]["PaginatedResponse_AgentActionResponse_"];

export interface HealthCheckResult {
  id: string | null;
  score: number | null;
  issues: string[];
  actions: string[];
  raw_analysis: string;
  source: string;
  photo_url: string | null;
  created_at: string | null;
}

export function runHealthCheck(token: string, data: { grow_id: string; observations: Record<string, string>; image_base64?: string; include_camera?: boolean }) {
  return apiFetch<HealthCheckResult>(
    "/ai/health-check",
    { method: "POST", body: JSON.stringify(data), token, timeout: 180_000 },
  );
}

export function getHealthCheckHistory(token: string, growId: string, limit = 10) {
  return apiFetch<{ items: HealthCheckResult[] }>(
    `/ai/health-check/${growId}/history?limit=${limit}`,
    { token },
  );
}

export function deleteHealthCheck(token: string, evalId: string) {
  return apiFetch<void>(`/ai/health-check/${evalId}`, { method: "DELETE", token });
}

export function listAiActions(
  token: string,
  params: {
    growCycleId?: string;
    status?: string;
    page?: number;
    pageSize?: number;
  } = {},
) {
  const search = new URLSearchParams();
  if (params.growCycleId) search.set("grow_cycle_id", params.growCycleId);
  if (params.status) search.set("status", params.status);
  if (params.page) search.set("page", String(params.page));
  if (params.pageSize) search.set("page_size", String(params.pageSize));

  const qs = search.toString();
  return apiFetch<PaginatedAgentActionResponse>(`/ai/actions${qs ? `?${qs}` : ""}`, { token });
}

export function approveAiAction(token: string, actionId: string, reason?: string) {
  return apiFetch<AgentActionDetailResponse>(`/ai/actions/${actionId}/approve`, {
    method: "POST",
    body: JSON.stringify({ reason: reason || null }),
    token,
  });
}

export function rejectAiAction(token: string, actionId: string, reason?: string) {
  return apiFetch<AgentActionDetailResponse>(`/ai/actions/${actionId}/reject`, {
    method: "POST",
    body: JSON.stringify({ reason: reason || null }),
    token,
  });
}

// ─── Conversations ─────────────────────────────────────────────────────────────

export interface ConversationResponse {
  id: string;
  grow_cycle_id: string | null;
  title: string | null;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface ConversationMessageResponse {
  id: string;
  role: string;
  content: string;
  metadata_json: Record<string, unknown> | null;
  created_at: string;
}

export interface ConversationDetailResponse extends ConversationResponse {
  messages: ConversationMessageResponse[];
}

export async function listConversations(token: string, growCycleId?: string) {
  const qs = growCycleId ? `?grow_cycle_id=${growCycleId}` : "";
  const res = await apiFetch<PaginatedResponse<ConversationResponse>>(`/conversations${qs}`, { token });
  return res.items;
}

export function getConversation(token: string, id: string) {
  return apiFetch<ConversationDetailResponse>(`/conversations/${id}`, { token });
}

export function createConversation(token: string, data: { grow_cycle_id?: string; title?: string }) {
  return apiFetch<ConversationResponse>("/conversations", { method: "POST", body: JSON.stringify(data), token });
}

export function updateConversation(token: string, id: string, data: { title?: string }) {
  return apiFetch<ConversationResponse>(`/conversations/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deleteConversation(token: string, id: string) {
  return apiFetch<void>(`/conversations/${id}`, { method: "DELETE", token });
}

// ─── Plant Photo Diagnosis ─────────────────────────────────────────────────────

export interface DiagnosisIssue {
  treatment_id: string;
  name: string;
  severity: "low" | "medium" | "high" | "critical";
  confidence: number;
  description: string;
  treatment: string;
}

export interface DiagnoseResult {
  overall_score: number;
  summary: string;
  issues: DiagnosisIssue[];
  actions: string[];
  grow_stage_assessment: string | null;
  model_used: string;
  health_eval_id: string | null;
}

export function diagnosePlant(token: string, data: { image_base64: string; grow_id?: string; observations?: string }) {
  return apiFetch<DiagnoseResult>(
    "/ai/diagnose",
    { method: "POST", body: JSON.stringify(data), token, timeout: 180_000 },
  );
}

// ─── Plant Identification ──────────────────────────────────────────────────────

export interface IdentifyResult {
  plant_type: string;
  confidence: number;
  species: string | null;
  strain_guess: string | null;
  strain_confidence: number | null;
  characteristics: string[];
  growth_stage: string | null;
  indica_sativa_ratio: string | null;
  notes: string;
}

export function identifyPlant(token: string, data: { image_base64: string }) {
  return apiFetch<IdentifyResult>(
    "/ai/identify",
    { method: "POST", body: JSON.stringify(data), token, timeout: 120_000 },
  );
}

// ─── Treatment Database ────────────────────────────────────────────────────────

export interface TreatmentSummary {
  id: string;
  category: string;
  name: string;
  summary: string;
}

export interface TreatmentDetail {
  id: string;
  category: string;
  name: string;
  aka: string[];
  summary: string;
  symptoms: string[];
  identification_tips: string[];
  causes: string[];
  severity_criteria: Record<string, string>;
  treatments: Record<string, string[]>;
  prevention: string[];
  recovery_time: string;
  commonly_confused_with: string[];
}

export function listTreatments(token: string, params?: { category?: string; query?: string }) {
  const searchParams = new URLSearchParams();
  if (params?.category) searchParams.set("category", params.category);
  if (params?.query) searchParams.set("query", params.query);
  const qs = searchParams.toString();
  return apiFetch<{ items: TreatmentSummary[]; total: number }>(
    `/ai/treatments${qs ? `?${qs}` : ""}`,
    { token },
  );
}

export function getTreatmentDetail(token: string, treatmentId: string, growType?: string) {
  const qs = growType ? `?grow_type=${growType}` : "";
  return apiFetch<TreatmentDetail>(
    `/ai/treatments/${treatmentId}${qs}`,
    { token },
  );
}

export function getCoachTip(token: string, growId: string) {
  return apiFetch<{ tip: string }>("/ai/coach-tip", {
    method: "POST",
    body: JSON.stringify({ grow_id: growId }),
    token,
    timeout: 180_000,
    retries: 2,
  });
}

export function getAiInsight(token: string, growId: string, insightType: string) {
  return apiFetch<{ insight_type: string; result: unknown }>("/ai/insights", {
    method: "POST",
    body: JSON.stringify({ grow_id: growId, insight_type: insightType }),
    token,
    timeout: 180_000,
    retries: 2,
  });
}

export function getGrowReportUrl(token: string, growId: string) {
  return `${API_BASE}/ai/report/${growId}`;
}

// Automation
export interface AutomationRuleResponse {
  id: string;
  grow_cycle_id: string | null;
  name: string;
  sensor: string;
  condition: string;
  threshold: number;
  action: string;
  cooldown_minutes: number;
  severity: string;
  enabled: boolean;
  last_triggered: string | null;
}

export async function listAutomationRules(token: string, growCycleId?: string) {
  const q = growCycleId ? `?grow_cycle_id=${growCycleId}` : "";
  const res = await apiFetch<PaginatedResponse<AutomationRuleResponse>>(`/automation/rules${q}`, { token });
  return res.items;
}

export function createAutomationRule(token: string, data: { name: string; sensor: string; condition: string; threshold: number; action: string; grow_cycle_id?: string; severity?: string }) {
  return apiFetch<AutomationRuleResponse>("/automation/rules", { method: "POST", body: JSON.stringify(data), token });
}

export function updateAutomationRule(token: string, id: string, data: Partial<{ name: string; threshold: number; enabled: boolean; severity: string }>) {
  return apiFetch<AutomationRuleResponse>(`/automation/rules/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deleteAutomationRule(token: string, id: string) {
  return apiFetch<void>(`/automation/rules/${id}`, { method: "DELETE", token });
}

export interface AlertResponse {
  id: string;
  alert_type: string;
  severity: string;
  message: string;
  sensor_value: number | null;
  acknowledged: boolean;
  created_at: string;
}

export async function listAlerts(token: string, limit?: number) {
  const q = limit ? `?limit=${limit}` : "";
  const res = await apiFetch<PaginatedResponse<AlertResponse>>(`/automation/alerts${q}`, { token });
  return res.items;
}

export function acknowledgeAlert(token: string, id: string) {
  return apiFetch<{ status: string }>(`/automation/alerts/${id}/acknowledge`, { method: "PATCH", token });
}

// Environment Schedules
export interface ScheduleResponse {
  id: string;
  tent_id: string;
  name: string;
  schedule_type: string;
  stage: string | null;
  on_time: string;
  off_time: string;
  settings: Record<string, unknown> | null;
  enabled: boolean;
}

export async function listSchedules(token: string, tentId?: string) {
  const q = tentId ? `?tent_id=${tentId}` : "";
  const res = await apiFetch<PaginatedResponse<ScheduleResponse>>(`/automation/schedules${q}`, { token });
  return res.items;
}

export function createSchedule(token: string, data: { tent_id: string; name: string; schedule_type: string; on_time: string; off_time: string; stage?: string }) {
  return apiFetch<ScheduleResponse>("/automation/schedules", { method: "POST", body: JSON.stringify(data), token });
}

export function updateSchedule(token: string, id: string, data: Partial<{ name: string; on_time: string; off_time: string; enabled: boolean }>) {
  return apiFetch<ScheduleResponse>(`/automation/schedules/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deleteSchedule(token: string, id: string) {
  return apiFetch<void>(`/automation/schedules/${id}`, { method: "DELETE", token });
}

// Notification Channels
export interface ChannelResponse {
  id: string;
  channel_type: string;
  name: string;
  config: Record<string, unknown>;
  enabled: boolean;
}

export async function listChannels(token: string) {
  const res = await apiFetch<PaginatedResponse<ChannelResponse>>("/notifications/channels", { token });
  return res.items;
}

export function createChannel(token: string, data: { channel_type: string; name: string; config: Record<string, string> }) {
  return apiFetch<ChannelResponse>("/notifications/channels", { method: "POST", body: JSON.stringify(data), token });
}

export function updateChannel(token: string, id: string, data: Partial<{ name: string; enabled: boolean; config: Record<string, string> }>) {
  return apiFetch<ChannelResponse>(`/notifications/channels/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deleteChannel(token: string, id: string) {
  return apiFetch<void>(`/notifications/channels/${id}`, { method: "DELETE", token });
}

export function testChannel(token: string, id: string) {
  return apiFetch<{ status: string }>(`/notifications/channels/${id}/test`, { method: "POST", token });
}

// Push subscriptions
export function pushSubscribe(token: string, data: { endpoint: string; p256dh: string; auth: string }) {
  return apiFetch<{ status: string }>("/notifications/push/subscribe", { method: "POST", body: JSON.stringify(data), token });
}

export function pushUnsubscribe(token: string) {
  return apiFetch<void>("/notifications/push/unsubscribe", { method: "DELETE", token });
}

// Billing
export interface BillingStatus {
  plan: string;
  plan_name: string;
  billing_model: string | null;
  stripe_customer_id: string | null;
  stripe_subscription_id: string | null;
  portal_url: string | null;
  supported_methods: string[] | null;
}

export function getBillingStatus(token: string) {
  return apiFetch<BillingStatus>("/billing/status", { token });
}

export function createCheckout(token: string, plan: string) {
  return apiFetch<{ checkout_url: string }>("/billing/checkout", { method: "POST", body: JSON.stringify({ plan }), token });
}

export function createPortalSession(token: string) {
  return apiFetch<{ portal_url: string }>("/billing/portal", { method: "POST", token });
}

// Custom Grow Types (Pro/Commercial)
export function listCustomGrowTypes(token: string) {
  return apiFetch<Array<{ id: string; slug: string; name: string; category: string; description: string; base_type: string | null; profile: Record<string, unknown>; submitted_for_review: boolean; approved: boolean }>>("/custom-grow-types", { token });
}
export function getCustomGrowType(id: string, token: string) {
  return apiFetch<{ id: string; slug: string; name: string; category: string; description: string; base_type: string | null; profile: Record<string, unknown>; submitted_for_review: boolean; approved: boolean }>(`/custom-grow-types/${id}`, { token });
}
export function createCustomGrowType(data: { name: string; slug: string; category: string; description: string; base_type?: string; profile: Record<string, unknown> }, token: string) {
  return apiFetch("/custom-grow-types", { method: "POST", body: JSON.stringify(data), token });
}
export function updateCustomGrowType(id: string, data: Record<string, unknown>, token: string) {
  return apiFetch(`/custom-grow-types/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}
export function deleteCustomGrowType(id: string, token: string) {
  return apiFetch(`/custom-grow-types/${id}`, { method: "DELETE", token });
}
export function submitGrowTypeForReview(id: string, token: string) {
  return apiFetch(`/custom-grow-types/${id}/submit`, { method: "POST", token });
}

// Tasks
export interface TaskItem {
  id: string;
  title: string;
  description: string | null;
  status: string;
  priority: string;
  category: string | null;
  source: string;
  assigned_to: string | null;
  created_by: string;
  grow_cycle_id: string | null;
  tent_id: string | null;
  bucket_id: string | null;
  due_date: string | null;
  completed_at: string | null;
  recurring: string | null;
  routine: string | null;
  estimated_minutes: number | null;
  created_at: string;
}

export async function listTasks(token: string, filters?: { status?: string; assigned_to?: string; category?: string; grow_cycle_id?: string; due_from?: string; due_to?: string }) {
  const params = new URLSearchParams();
  if (filters?.status) params.set("status", filters.status);
  if (filters?.assigned_to) params.set("assigned_to", filters.assigned_to);
  if (filters?.category) params.set("category", filters.category);
  if (filters?.grow_cycle_id) params.set("grow_cycle_id", filters.grow_cycle_id);
  if (filters?.due_from) params.set("due_from", filters.due_from);
  if (filters?.due_to) params.set("due_to", filters.due_to);
  const qs = params.toString();
  const res = await apiFetch<PaginatedResponse<TaskItem>>(`/tasks${qs ? `?${qs}` : ""}`, { token });
  return res.items;
}

export function getCalendarTasks(token: string, start: string, end: string) {
  return apiFetch<TaskItem[]>(`/tasks/calendar?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`, { token });
}

export function createTask(data: { title: string; description?: string; priority?: string; category?: string; assigned_to?: string; due_date?: string; recurring?: string; grow_cycle_id?: string; tent_id?: string; bucket_id?: string }, token: string) {
  return apiFetch<TaskItem>("/tasks", { method: "POST", body: JSON.stringify(data), token });
}
export function updateTask(id: string, data: Record<string, unknown>, token: string) {
  return apiFetch<TaskItem>(`/tasks/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}
export function completeTask(id: string, token: string) {
  return apiFetch<TaskItem>(`/tasks/${id}/complete`, { method: "POST", token });
}
export function deleteTask(id: string, token: string) {
  return apiFetch<void>(`/tasks/${id}`, { method: "DELETE", token });
}

// Audit Trail (Commercial)
export function listAuditLogs(token: string, filters?: { action?: string; resource_type?: string; user_id?: string; page?: number; page_size?: number }) {
  const params = new URLSearchParams();
  if (filters?.action) params.set("action", filters.action);
  if (filters?.resource_type) params.set("resource_type", filters.resource_type);
  if (filters?.user_id) params.set("user_id", filters.user_id);
  if (filters?.page) params.set("page", String(filters.page));
  if (filters?.page_size) params.set("page_size", String(filters.page_size));
  const qs = params.toString();
  return apiFetch<{ items: Array<{ id: string; user_id: string; action: string; resource_type: string; resource_id: string; before_value: Record<string, unknown> | null; after_value: Record<string, unknown> | null; ip_address: string | null; created_at: string }>; total: number; page: number; page_size: number }>(`/audit${qs ? `?${qs}` : ""}`, { token });
}

// API Keys (Commercial)
export function listApiKeys(token: string) {
  return apiFetch<Array<{ id: string; name: string; key_prefix: string; scopes: string; last_used: string | null; expires_at: string | null; revoked: boolean; created_at: string }>>("/api-keys", { token });
}
export function createApiKey(data: { name: string; scopes?: string; expires_in_days?: number }, token: string) {
  return apiFetch<{ id: string; name: string; key_prefix: string; scopes: string; key: string; last_used: string | null; expires_at: string | null; revoked: boolean; created_at: string }>("/api-keys", { method: "POST", body: JSON.stringify(data), token });
}
export function revokeApiKey(id: string, token: string) {
  return apiFetch(`/api-keys/${id}`, { method: "DELETE", token });
}
// Platform Admin
export interface AdminTenantSummary {
  id: string;
  name: string;
  slug: string;
  plan: string;
  user_count: number;
  created_at: string;
}

export interface AdminUserSummary {
  id: string;
  email: string;
  display_name: string | null;
  role: string;
  tenant_id: string;
  tenant_name: string;
  is_platform_admin: boolean;
  is_support: boolean;
  email_verified: boolean;
  created_at: string;
}

export async function adminListTenants(token: string) {
  const res = await apiFetch<{ items: AdminTenantSummary[]; total: number }>("/admin/tenants?page_size=200", { token });
  return res.items;
}

export interface AdminCreateTenantRequest {
  name: string;
  slug: string;
  plan?: string;
  owner_user_id?: string;
}

export function adminCreateTenant(token: string, data: AdminCreateTenantRequest) {
  return apiFetch<AdminTenantSummary>("/admin/tenants", { method: "POST", body: JSON.stringify(data), token });
}

export async function adminListUsers(token: string) {
  const res = await apiFetch<{ items: AdminUserSummary[]; total: number }>("/admin/users?page_size=200", { token });
  return res.items;
}

export function adminListTenantUsers(token: string, tenantId: string) {
  return apiFetch<AdminUserSummary[]>(`/admin/tenants/${tenantId}/users`, { token });
}

export function adminUpdateUserFlags(token: string, userId: string, data: { platform_role?: string }) {
  return apiFetch<AdminUserSummary>(`/admin/users/${userId}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function adminUpdateTenantPlan(token: string, tenantId: string, data: { plan: string }) {
  return apiFetch<AdminTenantSummary>(`/admin/tenants/${tenantId}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function adminGetStats(token: string) {
  return apiFetch<{ total_tenants: number; total_users: number; plans: Record<string, number> }>("/admin/stats", { token });
}

export function adminDeleteTenant(token: string, tenantId: string) {
  return apiFetch<{ status: string; message: string }>(`/admin/tenants/${tenantId}`, { method: "DELETE", token });
}

export function adminDeleteUser(token: string, userId: string) {
  return apiFetch<{ status: string; message: string }>(`/admin/users/${userId}`, { method: "DELETE", token });
}

// ── Outdoor Soil: Plot Grid ─────────────────────────────────────────

export interface PlotCellResponse {
  id: string;
  row: number;
  col: number;
  cell_type: string;
  bucket_id: string | null;
  companion_plant: string | null;
  device_id: string | null;
  irrigation_zone: string | null;
  sun_zone: string | null;
  notes: string | null;
}

export interface PlotGridResponse {
  id: string;
  grow_cycle_id: string;
  rows: number;
  cols: number;
  cell_size_inches: number;
  orientation: string;
  notes: string | null;
  cells: PlotCellResponse[];
  created_at: string;
  updated_at: string;
}

export function getPlotGrid(token: string, growId: string) {
  return apiFetch<PlotGridResponse>(`/grows/${growId}/plot`, { token });
}

export function upsertPlotGrid(token: string, growId: string, data: { rows: number; cols: number; cell_size_inches?: number; orientation?: string; notes?: string }) {
  return apiFetch<PlotGridResponse>(`/grows/${growId}/plot`, { method: "PUT", body: JSON.stringify(data), token });
}

export function batchUpdateCells(token: string, growId: string, cells: Array<{ row: number; col: number; cell_type: string; bucket_id?: string | null; companion_plant?: string | null; device_id?: string | null; irrigation_zone?: string | null; sun_zone?: string | null; notes?: string | null }>) {
  return apiFetch<PlotCellResponse[]>(`/grows/${growId}/plot/cells`, { method: "PATCH", body: JSON.stringify({ cells }), token });
}

export function deletePlotGrid(token: string, growId: string) {
  return apiFetch<void>(`/grows/${growId}/plot`, { method: "DELETE", token });
}

// ── Outdoor Soil: Soil Tests ────────────────────────────────────────

export interface SoilTestResponse {
  id: string;
  grow_cycle_id: string;
  tested_at: string;
  ph: number | null;
  nitrogen_ppm: number | null;
  phosphorus_ppm: number | null;
  potassium_ppm: number | null;
  organic_matter_pct: number | null;
  cec: number | null;
  calcium_ppm: number | null;
  magnesium_ppm: number | null;
  sulfur_ppm: number | null;
  source: string;
  notes: string | null;
}

export async function listSoilTests(token: string, growId: string) {
  const res = await apiFetch<PaginatedResponse<SoilTestResponse>>(`/grows/${growId}/soil-tests`, { token });
  return res.items;
}

export function createSoilTest(token: string, growId: string, data: Record<string, unknown>) {
  return apiFetch<SoilTestResponse>(`/grows/${growId}/soil-tests`, { method: "POST", body: JSON.stringify(data), token });
}

export function getLatestSoilTest(token: string, growId: string) {
  return apiFetch<SoilTestResponse>(`/grows/${growId}/soil-tests/latest`, { token });
}

export function deleteSoilTest(token: string, growId: string, testId: string) {
  return apiFetch<void>(`/grows/${growId}/soil-tests/${testId}`, { method: "DELETE", token });
}

// ── Outdoor Soil: Amendments ────────────────────────────────────────

export interface AmendmentResponse {
  id: string;
  grow_cycle_id: string;
  applied_at: string;
  amendment_type: string;
  product_name: string;
  quantity: string | null;
  area_applied: string | null;
  cost: number | null;
  notes: string | null;
}

export async function listAmendments(token: string, growId: string) {
  const res = await apiFetch<PaginatedResponse<AmendmentResponse>>(`/grows/${growId}/amendments`, { token });
  return res.items;
}

export function createAmendment(token: string, growId: string, data: Record<string, unknown>) {
  return apiFetch<AmendmentResponse>(`/grows/${growId}/amendments`, { method: "POST", body: JSON.stringify(data), token });
}

export function deleteAmendment(token: string, growId: string, amendmentId: string) {
  return apiFetch<void>(`/grows/${growId}/amendments/${amendmentId}`, { method: "DELETE", token });
}

// ── Outdoor Soil: Pest Scouting ─────────────────────────────────────

export interface PestScoutResponse {
  id: string;
  grow_cycle_id: string;
  scouted_at: string;
  pest_type: string;
  species: string;
  severity: string;
  grid_row: number | null;
  grid_col: number | null;
  photo_url: string | null;
  treatment_applied: string | null;
  treatment_type: string | null;
  notes: string | null;
}

export async function listPestScouts(token: string, growId: string, filters?: { pest_type?: string; severity?: string }) {
  const params = new URLSearchParams();
  if (filters?.pest_type) params.set("pest_type", filters.pest_type);
  if (filters?.severity) params.set("severity", filters.severity);
  const qs = params.toString();
  const res = await apiFetch<PaginatedResponse<PestScoutResponse>>(`/grows/${growId}/pest-scouts${qs ? `?${qs}` : ""}`, { token });
  return res.items;
}

export function createPestScout(token: string, growId: string, data: Record<string, unknown>) {
  return apiFetch<PestScoutResponse>(`/grows/${growId}/pest-scouts`, { method: "POST", body: JSON.stringify(data), token });
}

export function deletePestScout(token: string, growId: string, entryId: string) {
  return apiFetch<void>(`/grows/${growId}/pest-scouts/${entryId}`, { method: "DELETE", token });
}

// ── Outdoor Soil: Harvest Yields ────────────────────────────────────

export interface HarvestYieldResponse {
  id: string;
  grow_cycle_id: string;
  bucket_id: string;
  harvested_at: string;
  wet_weight_oz: number | null;
  dry_weight_oz: number | null;
  trim_weight_oz: number | null;
  quality_rating: number | null;
  trichome_stage: string | null;
  notes: string | null;
}

export interface YieldSummaryResponse {
  total_plants: number;
  plants_harvested: number;
  total_wet_oz: number;
  total_dry_oz: number;
  total_trim_oz: number;
  avg_dry_per_plant_oz: number;
  avg_quality: number | null;
  yield_per_sqft_oz: number | null;
}

export async function listHarvestYields(token: string, growId: string) {
  const res = await apiFetch<PaginatedResponse<HarvestYieldResponse>>(`/grows/${growId}/yields`, { token });
  return res.items;
}

export function createHarvestYield(token: string, growId: string, data: Record<string, unknown>) {
  return apiFetch<HarvestYieldResponse>(`/grows/${growId}/yields`, { method: "POST", body: JSON.stringify(data), token });
}

export function getYieldSummary(token: string, growId: string) {
  return apiFetch<YieldSummaryResponse>(`/grows/${growId}/yields/summary`, { token });
}

export function deleteHarvestYield(token: string, growId: string, yieldId: string) {
  return apiFetch<void>(`/grows/${growId}/yields/${yieldId}`, { method: "DELETE", token });
}

// ── Outdoor Soil: Companion Plants ──────────────────────────────────

export interface CompanionPlantEntry {
  plant: string;
  beneficial: string[];
  harmful: string[];
  notes: string;
}

export interface CompanionCheckResult {
  plant: string;
  neighbor: string;
  compatibility: "beneficial" | "harmful" | "neutral" | "unknown";
  reason: string;
}

export interface CompanionSuggestion {
  plant: string;
  suggestions: Array<{ plant: string; notes: string }>;
}

export function listCompanionPlants(token: string) {
  return apiFetch<CompanionPlantEntry[]>("/companion-plants", { token });
}

export function checkCompanionCompatibility(token: string, plant: string, neighbor: string) {
  return apiFetch<CompanionCheckResult>(`/companion-plants/check?plant=${encodeURIComponent(plant)}&neighbor=${encodeURIComponent(neighbor)}`, { token });
}

export function suggestCompanions(token: string, plant: string) {
  return apiFetch<CompanionSuggestion>(`/companion-plants/suggest?plant=${encodeURIComponent(plant)}`, { token });
}

// ── Outdoor Soil: Intelligence (GDD, Frost, Moon) ───────────────────

export interface GDDResponse {
  grow_id: string;
  accumulated_gdd: number;
  target_gdd: number | null;
  progress_pct: number | null;
  daily_log: Array<{ date: string; high_f: number; low_f: number; gdd: number; cumulative_gdd: number }>;
}

export interface FrostDatesResponse {
  tent_id: string;
  latitude: number;
  longitude: number;
  last_spring_frost: string;
  first_fall_frost: string;
  frost_free_days: number;
  hardiness_zone: string;
}

export interface MoonPhaseResponse {
  phase: string;
  illumination_pct: number;
  days_until_new: number;
  days_until_full: number;
  planting_recommendation: string;
}

export function getGDD(token: string, growId: string) {
  return apiFetch<GDDResponse>(`/outdoor/${growId}/gdd`, { token });
}

export function getFrostDates(token: string, tentId: string) {
  return apiFetch<FrostDatesResponse>(`/outdoor/${tentId}/frost-dates`, { token });
}

export function getMoonPhase(token: string, tentId: string) {
  return apiFetch<MoonPhaseResponse>(`/outdoor/${tentId}/moon`, { token });
}

export function logManualWeather(token: string, tentId: string, data: Record<string, unknown>) {
  return apiFetch<{ id: string; recorded_at: string }>(`/outdoor/${tentId}/manual`, { method: "POST", body: JSON.stringify(data), token });
}

// ── Outdoor Container: Container Profiles ───────────────────────────

export interface ContainerProfileResponse {
  id: string;
  grow_cycle_id: string;
  bucket_id: string;
  pot_size_gallons: number | null;
  media_type: string | null;
  pot_color: string | null;
  pot_material: string | null;
  has_saucer: boolean;
  is_mobile: boolean;
  sun_exposure: string | null;
  location_notes: string | null;
  created_at: string;
  updated_at: string;
}

export async function listContainerProfiles(token: string, growId: string) {
  const res = await apiFetch<PaginatedResponse<ContainerProfileResponse>>(`/grows/${growId}/containers`, { token });
  return res.items;
}

export function getContainerProfile(token: string, growId: string, bucketId: string) {
  return apiFetch<ContainerProfileResponse>(`/grows/${growId}/containers/${bucketId}`, { token });
}

export function upsertContainerProfile(token: string, growId: string, bucketId: string, data: Record<string, unknown>) {
  return apiFetch<ContainerProfileResponse>(`/grows/${growId}/containers/${bucketId}`, { method: "PUT", body: JSON.stringify(data), token });
}

export function deleteContainerProfile(token: string, growId: string, bucketId: string) {
  return apiFetch<void>(`/grows/${growId}/containers/${bucketId}`, { method: "DELETE", token });
}

// ── Outdoor Container: Runoff Readings ──────────────────────────────

export interface RunoffReadingResponse {
  id: string;
  grow_cycle_id: string;
  bucket_id: string;
  recorded_at: string;
  input_ph: number | null;
  input_ec: number | null;
  runoff_ph: number | null;
  runoff_ec: number | null;
  runoff_pct: number | null;
  notes: string | null;
}

export interface RunoffStatsResponse {
  bucket_id: string;
  reading_count: number;
  avg_input_ph: number | null;
  avg_input_ec: number | null;
  avg_runoff_ph: number | null;
  avg_runoff_ec: number | null;
  avg_ph_delta: number | null;
  avg_ec_delta: number | null;
  latest_input_ph: number | null;
  latest_input_ec: number | null;
  latest_runoff_ph: number | null;
  latest_runoff_ec: number | null;
}

export async function listRunoffReadings(token: string, growId: string, bucketId?: string) {
  const qs = bucketId ? `?bucket_id=${bucketId}` : "";
  const res = await apiFetch<PaginatedResponse<RunoffReadingResponse>>(`/grows/${growId}/runoff${qs}`, { token });
  return res.items;
}

export function createRunoffReading(token: string, growId: string, data: Record<string, unknown>) {
  return apiFetch<RunoffReadingResponse>(`/grows/${growId}/runoff`, { method: "POST", body: JSON.stringify(data), token });
}

export function getRunoffStats(token: string, growId: string) {
  return apiFetch<RunoffStatsResponse[]>(`/grows/${growId}/runoff/stats`, { token });
}

export function deleteRunoffReading(token: string, growId: string, readingId: string) {
  return apiFetch<void>(`/grows/${growId}/runoff/${readingId}`, { method: "DELETE", token });
}

// Quick-Log
export interface NutrientDose {
  product_id?: string;
  name: string;
  amount_ml: number;
}

export interface FeedingLogPayload {
  bucket_ids: string[];
  ph?: number;
  ec?: number;
  ppm?: number;
  water_temp_f?: number;
  volume_gal?: number;
  nutrients?: NutrientDose[];
  notes?: string;
  recorded_at?: string;
}

export interface ManualReadingPayload {
  tent_id: string;
  temp_f?: number;
  humidity?: number;
  vpd?: number;
}

export interface QuickNotePayload {
  bucket_id?: string;
  grow_cycle_id?: string;
  tags?: string[];
  content: string;
}

export interface BatchAction {
  type: "feeding" | "reading" | "note";
  data: Record<string, unknown>;
  client_timestamp: string;
}

export function quickLogFeeding(token: string, data: FeedingLogPayload) {
  return apiFetch<{ created: number; bucket_ids: string[] }>("/quick-log/feeding", { method: "POST", body: JSON.stringify(data), token });
}

export function quickLogReading(token: string, data: ManualReadingPayload) {
  return apiFetch<{ id: string }>("/quick-log/reading", { method: "POST", body: JSON.stringify(data), token });
}

export function quickLogNote(token: string, data: QuickNotePayload) {
  return apiFetch<{ id: string }>("/quick-log/note", { method: "POST", body: JSON.stringify(data), token });
}

export function quickLogBatch(token: string, actions: BatchAction[]) {
  return apiFetch<{ processed: number; succeeded: number; failed: number }>("/quick-log/batch", { method: "POST", body: JSON.stringify({ actions }), token });
}

// ─── Integrations ─────────────────────────────────────────────────────────────

export interface IntegrationResponse {
  id: string;
  type: string;
  name: string;
  config: Record<string, unknown>;
  webhook_secret: string;
  enabled: boolean;
  poll_interval_s: number | null;
  last_synced_at: string | null;
  error_count: number;
  created_at: string;
  updated_at: string;
}

export interface DeviceMapResponse {
  id: string;
  integration_id: string;
  external_id: string;
  external_name: string | null;
  tent_id: string | null;
  bucket_id: string | null;
  sensor_mapping: Record<string, string>;
  enabled: boolean;
  created_at: string;
}

export interface SyncLogResponse {
  id: string;
  integration_id: string;
  status: string;
  readings_count: number;
  error_message: string | null;
  raw_data: Record<string, unknown>[] | null;
  synced_at: string;
}

export interface DiscoveredDeviceResponse {
  external_id: string;
  name: string;
  device_type: string;
  latest_reading: Record<string, unknown> | null;
}

export async function listIntegrations(token: string, type?: string) {
  const q = type ? `?type=${encodeURIComponent(type)}` : "";
  const res = await apiFetch<PaginatedResponse<IntegrationResponse>>(`/integrations${q}`, { token });
  return res.items;
}

export function getIntegration(token: string, id: string) {
  return apiFetch<IntegrationResponse>(`/integrations/${id}`, { token });
}

export function createIntegration(token: string, data: { type: string; name: string; config: Record<string, unknown>; enabled?: boolean; poll_interval_s?: number }) {
  return apiFetch<IntegrationResponse>("/integrations", { method: "POST", body: JSON.stringify(data), token });
}

export function updateIntegration(token: string, id: string, data: { name?: string; config?: Record<string, unknown>; enabled?: boolean; poll_interval_s?: number }) {
  return apiFetch<IntegrationResponse>(`/integrations/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deleteIntegration(token: string, id: string) {
  return apiFetch<void>(`/integrations/${id}`, { method: "DELETE", token });
}

export async function listDeviceMaps(token: string, integrationId: string) {
  const res = await apiFetch<PaginatedResponse<DeviceMapResponse>>(`/integrations/${integrationId}/devices`, { token });
  return res.items;
}

export function createDeviceMap(token: string, integrationId: string, data: { external_id: string; external_name?: string; tent_id?: string; bucket_id?: string; sensor_mapping?: Record<string, string>; enabled?: boolean }) {
  return apiFetch<DeviceMapResponse>(`/integrations/${integrationId}/devices`, { method: "POST", body: JSON.stringify(data), token });
}

export function updateDeviceMap(token: string, integrationId: string, deviceId: string, data: { external_name?: string; tent_id?: string; bucket_id?: string; sensor_mapping?: Record<string, string>; enabled?: boolean }) {
  return apiFetch<DeviceMapResponse>(`/integrations/${integrationId}/devices/${deviceId}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deleteDeviceMap(token: string, integrationId: string, deviceId: string) {
  return apiFetch<void>(`/integrations/${integrationId}/devices/${deviceId}`, { method: "DELETE", token });
}

export async function listSyncLogs(token: string, integrationId: string) {
  const res = await apiFetch<PaginatedResponse<SyncLogResponse>>(`/integrations/${integrationId}/logs`, { token });
  return res.items;
}

export function triggerSync(token: string, integrationId: string) {
  return apiFetch<{ status: string; readings_count: number; error_message: string | null }>(`/integrations/${integrationId}/sync`, { method: "POST", token });
}

export function discoverDevices(token: string, integrationId: string) {
  return apiFetch<DiscoveredDeviceResponse[]>(`/integrations/${integrationId}/discover`, { method: "POST", token });
}

export function debugDeviceMapReadings(token: string, integrationId: string, deviceId: string) {
  return apiFetch<Record<string, unknown>>(`/integrations/${integrationId}/devices/${deviceId}/debug`, { token });
}

// ─── Missing CRUD Helpers ─────────────────────────────────────────────────────

export function deleteSensorReading(token: string, readingId: string) {
  return apiFetch<void>(`/sensors/${readingId}`, { method: "DELETE", token });
}

export function deleteTentReading(token: string, readingId: string) {
  return apiFetch<void>(`/tent-sensors/${readingId}`, { method: "DELETE", token });
}

export function getTentSensorTrends(token: string, tentId: string) {
  return apiFetch<{ timestamps: string[]; temps: (number | null)[]; humidities: (number | null)[] }>(`/tent-sensors/trends/${tentId}`, { token });
}

export function updateNotificationPreference(token: string, id: string, data: { severity_filter?: string; event_types?: string; enabled?: boolean }) {
  return apiFetch<NotificationPreference>(`/notifications/preferences/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function updateSoilTest(token: string, growId: string, testId: string, data: Record<string, unknown>) {
  return apiFetch<SoilTestResponse>(`/grows/${growId}/soil-tests/${testId}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function updateAmendment(token: string, growId: string, amendmentId: string, data: Record<string, unknown>) {
  return apiFetch<AmendmentResponse>(`/grows/${growId}/amendments/${amendmentId}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function updatePestScout(token: string, growId: string, entryId: string, data: Record<string, unknown>) {
  return apiFetch<PestScoutResponse>(`/grows/${growId}/pest-scouts/${entryId}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function updateHarvestYield(token: string, growId: string, yieldId: string, data: Record<string, unknown>) {
  return apiFetch<HarvestYieldResponse>(`/grows/${growId}/yields/${yieldId}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function updateRunoffReading(token: string, growId: string, readingId: string, data: Record<string, unknown>) {
  return apiFetch<RunoffReadingResponse>(`/grows/${growId}/runoff/${readingId}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function listGrowTypeReviewQueue(token: string) {
  return apiFetch<{ id: string; name: string; submitted_by: string; submitted_at: string; status: string }[]>("/custom-grow-types/review/queue", { token });
}

// ─── Support / Tickets ────────────────────────────────────────────────────────

export interface SupportTicket {
  id: string;
  subject: string;
  status: string;
  priority: string;
  category: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

export interface TicketMessage {
  id: string;
  author_id: string;
  body: string;
  is_internal: boolean;
  attachments: unknown[];
  created_at: string;
}

export interface TicketDetail extends SupportTicket {
  due_at: string | null;
  first_response_at: string | null;
  resolved_at: string | null;
  satisfaction_rating: number | null;
  tags: string[] | null;
  messages: TicketMessage[];
}

export function listMyTickets(token: string, params?: { status?: string; page?: number }) {
  const qs = new URLSearchParams();
  if (params?.status) qs.set("status", params.status);
  if (params?.page) qs.set("page", String(params.page));
  return apiFetch<{ tickets: SupportTicket[]; total: number; page: number }>(`/support/tickets?${qs}`, { token });
}

export function getTicket(token: string, ticketId: string) {
  return apiFetch<TicketDetail>(`/support/tickets/${ticketId}`, { token });
}

export function createTicket(token: string, data: { subject: string; body: string; category?: string; priority?: string }) {
  return apiFetch<SupportTicket>("/support/tickets", { method: "POST", body: JSON.stringify(data), token });
}

export function addTicketMessage(token: string, ticketId: string, body: string) {
  return apiFetch<TicketMessage>(`/support/tickets/${ticketId}/messages`, { method: "POST", body: JSON.stringify({ body }), token });
}

export function closeTicket(token: string, ticketId: string) {
  return apiFetch<{ status: string }>(`/support/tickets/${ticketId}/close`, { method: "POST", token });
}

export function rateTicket(token: string, ticketId: string, rating: number, comment?: string) {
  return apiFetch<{ rating: number }>(`/support/tickets/${ticketId}/rate`, { method: "POST", body: JSON.stringify({ rating, comment }), token });
}

// ─── Knowledge Base ───────────────────────────────────────────────────────────

export interface KBCategory {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  icon: string | null;
  article_count: number;
}

export interface KBArticle {
  id: string;
  title: string;
  slug: string;
  body_markdown?: string;
  tags: string[] | null;
  views: number;
  helpful_yes: number;
  helpful_no: number;
  created_at: string;
  updated_at?: string;
}

export function listKBCategories() {
  return apiFetch<KBCategory[]>("/support/kb/categories");
}

export function listKBArticles(params?: { category_slug?: string; page?: number }) {
  const qs = new URLSearchParams();
  if (params?.category_slug) qs.set("category_slug", params.category_slug);
  if (params?.page) qs.set("page", String(params.page));
  return apiFetch<{ articles: KBArticle[]; total: number; page: number }>(`/support/kb/articles?${qs}`);
}

export function searchKBArticles(q: string) {
  return apiFetch<KBArticle[]>(`/support/kb/articles/search?q=${encodeURIComponent(q)}`);
}

export function getKBArticle(slug: string) {
  return apiFetch<KBArticle>(`/support/kb/articles/${slug}`);
}

export function voteKBArticle(slug: string, helpful: boolean) {
  return apiFetch<{ helpful_yes: number; helpful_no: number }>(`/support/kb/articles/${slug}/vote?helpful=${helpful}`, { method: "POST" });
}

// ─── Forum ────────────────────────────────────────────────────────────────────

export interface ForumCategory {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  icon: string | null;
  thread_count: number;
  post_count: number;
}

export interface ForumThread {
  id: string;
  title: string;
  author_id: string;
  status: string;
  is_pinned: boolean;
  view_count: number;
  reply_count: number;
  upvotes: number;
  has_solution: boolean;
  last_activity_at: string;
  created_at: string;
}

export interface ForumPost {
  id: string;
  author_id: string;
  body: string;
  is_solution: boolean;
  upvotes: number;
  created_at: string;
}

export function listForumCategories() {
  return apiFetch<ForumCategory[]>("/support/forum/categories");
}

export function listForumThreads(params?: { category_slug?: string; page?: number }) {
  const qs = new URLSearchParams();
  if (params?.category_slug) qs.set("category_slug", params.category_slug);
  if (params?.page) qs.set("page", String(params.page));
  return apiFetch<{ threads: ForumThread[]; total: number; page: number }>(`/support/forum/threads?${qs}`);
}

export function getForumThread(threadId: string) {
  return apiFetch<ForumThread & { body: string; posts: ForumPost[] }>(`/support/forum/threads/${threadId}`);
}

export function createForumThread(token: string, data: { category_id: string; title: string; body: string }) {
  return apiFetch<{ id: string; title: string }>("/support/forum/threads", { method: "POST", body: JSON.stringify(data), token });
}

export function createForumPost(token: string, threadId: string, body: string) {
  return apiFetch<{ id: string }>(`/support/forum/threads/${threadId}/posts`, { method: "POST", body: JSON.stringify({ body }), token });
}

export function upvoteThread(token: string, threadId: string) {
  return apiFetch<{ upvotes: number }>(`/support/forum/threads/${threadId}/upvote`, { method: "POST", token });
}

export function upvotePost(token: string, postId: string) {
  return apiFetch<{ upvotes: number }>(`/support/forum/posts/${postId}/upvote`, { method: "POST", token });
}

// ─── Cost/ROI Tracking ─────────────────────────────────────────────────────────

export interface Expense {
  id: string;
  grow_cycle_id: string;
  category: string;
  amount_cents: number;
  currency: string;
  description: string | null;
  vendor: string | null;
  date: string;
  is_recurring: boolean;
  recurring_interval: string | null;
  notes: string | null;
  created_at: string;
}

export interface HarvestValueEntry {
  id: string;
  grow_cycle_id: string;
  grade: string;
  weight_g: number;
  price_per_gram_cents: number;
  notes: string | null;
  created_at: string;
}

export interface ROISummary {
  grow_cycle_id: string;
  grow_name: string;
  total_expenses_cents: number;
  total_harvest_value_cents: number;
  total_dry_weight_g: number;
  cost_per_gram_cents: number | null;
  roi_percentage: number | null;
  expense_breakdown: Record<string, number>;
}

export function listExpenses(token: string, growCycleId?: string, category?: string) {
  const params = new URLSearchParams();
  if (growCycleId) params.set("grow_cycle_id", growCycleId);
  if (category) params.set("category", category);
  const qs = params.toString();
  return apiFetch<Expense[]>(`/grows/expenses${qs ? `?${qs}` : ""}`, { token });
}

export function createExpense(token: string, data: { grow_cycle_id: string; category: string; amount_cents: number; currency?: string; description?: string; vendor?: string; date?: string; is_recurring?: boolean; recurring_interval?: string; notes?: string }) {
  return apiFetch<Expense>("/grows/expenses", { method: "POST", body: JSON.stringify(data), token });
}

export function updateExpense(token: string, expenseId: string, data: Record<string, unknown>) {
  return apiFetch<Expense>(`/grows/expenses/${expenseId}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deleteExpense(token: string, expenseId: string) {
  return apiFetch<void>(`/grows/expenses/${expenseId}`, { method: "DELETE", token });
}

export function listHarvestValues(token: string, growCycleId?: string) {
  const qs = growCycleId ? `?grow_cycle_id=${growCycleId}` : "";
  return apiFetch<HarvestValueEntry[]>(`/grows/harvest-values${qs}`, { token });
}

export function createHarvestValue(token: string, data: { grow_cycle_id: string; grade: string; weight_g: number; price_per_gram_cents: number; notes?: string }) {
  return apiFetch<HarvestValueEntry>("/grows/harvest-values", { method: "POST", body: JSON.stringify(data), token });
}

export function deleteHarvestValue(token: string, valueId: string) {
  return apiFetch<void>(`/grows/harvest-values/${valueId}`, { method: "DELETE", token });
}

export function getGrowROI(token: string, growCycleId: string) {
  return apiFetch<ROISummary>(`/grows/${growCycleId}/roi`, { token });
}

export function compareGrowsROI(token: string, growIds?: string[], limit?: number) {
  const params = new URLSearchParams();
  if (growIds?.length) growIds.forEach((id) => params.append("grow_ids", id));
  if (limit) params.set("limit", String(limit));
  const qs = params.toString();
  return apiFetch<{ grows: ROISummary[] }>(`/grows/roi-comparison${qs ? `?${qs}` : ""}`, { token });
}

// ─── Admin Billing Providers ───────────────────────────────────────────────────

export interface PaymentProviderSummary {
  id: string;
  provider_type: string;
  display_name: string;
  is_active: boolean;
  is_primary: boolean;
  supported_methods: string[] | null;
  created_at: string;
}

export function adminListProviders(token: string) {
  return apiFetch<PaymentProviderSummary[]>("/billing/providers", { token });
}

export function adminCreateProvider(token: string, data: { provider_type: string; display_name: string; config: Record<string, string>; webhook_secret?: string }) {
  return apiFetch<PaymentProviderSummary>("/billing/providers", { method: "POST", body: JSON.stringify(data), token });
}

export function adminUpdateProvider(token: string, providerId: string, data: Record<string, unknown>) {
  return apiFetch<PaymentProviderSummary>(`/billing/providers/${providerId}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function adminDeleteProvider(token: string, providerId: string) {
  return apiFetch<void>(`/billing/providers/${providerId}`, { method: "DELETE", token });
}

export function adminTestProvider(token: string, providerId: string) {
  return apiFetch<{ success: boolean; message: string }>(`/billing/providers/${providerId}/test`, { method: "POST", token });
}

// ─── Invoice History ────────────────────────────────────────────────────────────

export interface InvoiceEntry {
  id: string;
  date: string;
  amount: string;
  status: string;
  pdf_url: string | null;
  hosted_url: string | null;
  description: string | null;
}

export function listInvoices(token: string, limit?: number) {
  const qs = limit ? `?limit=${limit}` : "";
  return apiFetch<InvoiceEntry[]>(`/billing/invoices${qs}`, { token });
}

// ─── Cancellation Flow ──────────────────────────────────────────────────────────

export interface RetentionOffer {
  discount: string;
  offer_code: string;
  expires_at: string;
}

export interface CancelResponse {
  status: string;
  retention_offer: RetentionOffer | null;
  cancellation_date: string | null;
}

export function cancelSubscription(token: string, data: { reason?: string; feedback?: string; accept_retention_offer?: boolean }) {
  return apiFetch<CancelResponse>("/billing/cancel", { method: "POST", body: JSON.stringify(data), token });
}

// ─── Account Deletion ───────────────────────────────────────────────────────────

export interface DeletionStatus {
  deletion_scheduled: boolean;
  deletion_date: string | null;
  days_remaining: number | null;
}

export function requestAccountDeletion(token: string, confirmEmail: string) {
  return apiFetch<{ status: string; deletion_date: string | null; message: string }>("/account/delete", { method: "POST", body: JSON.stringify({ confirm_email: confirmEmail }), token });
}

export function cancelAccountDeletion(token: string) {
  return apiFetch<{ status: string; message: string }>("/account/delete", { method: "DELETE", token });
}

export function getAccountDeletionStatus(token: string) {
  return apiFetch<DeletionStatus>("/account/delete/status", { token });
}

// ─── Usage Alerts ───────────────────────────────────────────────────────────────

export interface UsageAlert {
  metric: string;
  current: number;
  limit: number;
  plan: string;
}

export function getUsageAlerts(token: string) {
  return apiFetch<{ alerts: UsageAlert[] }>("/billing/usage-alerts", { token });
}

// ─── Admin: Billing Plans ────────────────────────────────────────────────────────

export interface AdminBillingPlan {
  id: string;
  slug: string;
  name: string;
  description: string | null;
  is_active: boolean;
  is_public: boolean;
  sort_order: number;
  billing_model: string;
  base_price_cents: number;
  annual_price_cents: number | null;
  currency: string;
  max_grows: number | null;
  max_devices: number | null;
  max_team_members: number | null;
  max_ai_analyses_month: number | null;
  max_storage_gb: number | null;
  max_automations: number | null;
  max_integrations: number | null;
  max_journal_entries_month: number | null;
  data_retention_days: number | null;
  included_support_tier: string;
  features_json: Record<string, unknown>;
}

export function adminListPlans(token: string) {
  return apiFetch<AdminBillingPlan[]>("/billing/plans/", { token });
}

export function adminGetPlan(token: string, planId: string) {
  return apiFetch<AdminBillingPlan>(`/billing/plans/${planId}`, { token });
}

export function adminCreatePlan(token: string, data: Partial<AdminBillingPlan>) {
  return apiFetch<AdminBillingPlan>("/billing/plans/", { method: "POST", body: JSON.stringify(data), token });
}

export function adminUpdatePlan(token: string, planId: string, data: Partial<AdminBillingPlan>) {
  return apiFetch<AdminBillingPlan>(`/billing/plans/${planId}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function adminArchivePlan(token: string, planId: string) {
  return apiFetch<void>(`/billing/plans/${planId}`, { method: "DELETE", token });
}

export function adminSyncPlan(token: string, planId: string) {
  return apiFetch<{ status: string; external_price_id: string }>(`/billing/plans/${planId}/sync`, { method: "POST", token });
}

// ─── Public Plans (no auth) ─────────────────────────────────────────────────

export interface PublicBillingPlan {
  id: string;
  slug: string;
  name: string;
  description: string | null;
  is_public: boolean;
  sort_order: number;
  billing_model: string;
  base_price_cents: number;
  annual_price_cents: number | null;
  currency: string;
  max_grows: number | null;
  max_devices: number | null;
  max_team_members: number | null;
  max_ai_analyses_month: number | null;
  max_storage_gb: number | null;
  max_automations: number | null;
  max_integrations: number | null;
  max_journal_entries_month: number | null;
  included_support_tier: string;
  features_json: Record<string, unknown>;
}

export function getPublicPlans() {
  return apiFetch<PublicBillingPlan[]>("/billing/plans/public");
}

// ─── Config Management (Admin) ──────────────────────────────────────────────

export interface GrowTypeProfileSummary {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  sensor_kit: string | null;
  is_system: boolean;
}

export interface GrowTypeStageData {
  id: string;
  name: string;
  slug: string;
  order: number;
  duration_days_min: number | null;
  duration_days_max: number | null;
  description: string | null;
  environment: Record<string, number | null> | null;
  nutrients: Array<Record<string, unknown>>;
  watering: Record<string, unknown> | null;
}

export interface GrowTypeProfileFull extends GrowTypeProfileSummary {
  ai_context_prompt: string | null;
  stages: GrowTypeStageData[];
  equipment: Array<{ id: string; item_name: string; category: string | null; required: boolean; notes: string | null }>;
  troubleshooting: Array<{ id: string; symptom: string; cause: string | null; solution: string | null; severity: string | null }>;
}

export interface TaskTemplateSummary {
  id: string;
  name: string;
  description: string | null;
  category: string;
  grow_type_slugs: string[] | null;
  frequency_hours: number;
  stage_slug: string | null;
  priority: string;
  routine: string | null;
  estimated_minutes: number;
  is_system: boolean;
  steps: Array<{ id: string; order: number; instruction: string; duration_minutes: number | null; optional: boolean }>;
}

export function adminListGrowTypeProfiles(token: string) {
  return apiFetch<GrowTypeProfileSummary[]>("/admin/config/grow-types", { token });
}

export function adminGetGrowTypeProfile(token: string, slug: string) {
  return apiFetch<GrowTypeProfileFull>(`/admin/config/grow-types/${slug}`, { token });
}

export function adminCreateGrowTypeProfile(token: string, data: { name: string; slug: string; description?: string; sensor_kit?: string }) {
  return apiFetch<{ id: string; slug: string }>("/admin/config/grow-types", { method: "POST", body: JSON.stringify(data), token });
}

export function adminUpdateGrowTypeProfile(token: string, slug: string, data: Record<string, unknown>) {
  return apiFetch<{ id: string; slug: string }>(`/admin/config/grow-types/${slug}`, { method: "PUT", body: JSON.stringify(data), token });
}

export function adminDeleteGrowTypeProfile(token: string, slug: string) {
  return apiFetch<void>(`/admin/config/grow-types/${slug}`, { method: "DELETE", token });
}

export function adminListTaskTemplates(token: string, params?: { category?: string; grow_type?: string }) {
  const qs = new URLSearchParams();
  if (params?.category) qs.set("category", params.category);
  if (params?.grow_type) qs.set("grow_type", params.grow_type);
  const query = qs.toString();
  return apiFetch<TaskTemplateSummary[]>(`/admin/config/task-templates${query ? `?${query}` : ""}`, { token });
}

export function adminCreateTaskTemplate(token: string, data: Partial<TaskTemplateSummary>) {
  return apiFetch<{ id: string; name: string }>("/admin/config/task-templates", { method: "POST", body: JSON.stringify(data), token });
}

export function adminUpdateTaskTemplate(token: string, templateId: string, data: Record<string, unknown>) {
  return apiFetch<{ id: string }>(`/admin/config/task-templates/${templateId}`, { method: "PUT", body: JSON.stringify(data), token });
}

export function adminDeleteTaskTemplate(token: string, templateId: string) {
  return apiFetch<void>(`/admin/config/task-templates/${templateId}`, { method: "DELETE", token });
}

export function adminExportConfig(token: string, configType: string) {
  return apiFetch<{ type: string; count: number; data: unknown[] }>(`/admin/config/export/${configType}`, { token });
}

export function adminImportConfig(token: string, configType: string, payload: { data: unknown[] }) {
  return apiFetch<{ status: string; count: number }>(`/admin/config/import/${configType}`, { method: "POST", body: JSON.stringify(payload), token });
}

// Device Commands

export interface DeviceCommandResponse {
  id: string;
  device_id: string;
  command_type: string;
  payload: Record<string, unknown>;
  status: string;
  source: string;
  created_at: string;
  sent_at: string | null;
  acknowledged_at: string | null;
  error_message: string | null;
}

export interface CommandTypeInfo {
  type: string;
  description: string;
}

export function listDeviceCommands(token: string, deviceId?: string, status?: string) {
  const qs = new URLSearchParams();
  if (deviceId) qs.set("device_id", deviceId);
  if (status) qs.set("status", status);
  const q = qs.toString();
  return apiFetch<PaginatedResponse<DeviceCommandResponse>>(`/devices/commands${q ? `?${q}` : ""}`, { token }).then((r) => r.items);
}

export function createDeviceCommand(token: string, data: { device_id: string; command_type: string; payload?: Record<string, unknown>; expires_in_seconds?: number }) {
  return apiFetch<DeviceCommandResponse>("/devices/commands", { method: "POST", body: JSON.stringify(data), token });
}

export function getDeviceCommand(token: string, commandId: string) {
  return apiFetch<DeviceCommandResponse>(`/devices/commands/${commandId}`, { token });
}

export function listCommandTypes(token: string) {
  return apiFetch<CommandTypeInfo[]>("/devices/commands/types", { token });
}

// ── Equipment Control ─────────────────────────────────────────────────────────

export interface EquipmentResponse {
  id: string;
  tenant_id: string;
  tent_id: string | null;
  name: string;
  equipment_type: string;
  protocol: string;
  protocol_config: Record<string, unknown>;
  capabilities: string[];
  requested_state: Record<string, unknown>;
  confirmed_state: Record<string, unknown>;
  last_confirmed_at: string | null;
  max_on_minutes: number | null;
  cooldown_minutes: number;
  conflicts_with: string[];
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface EquipmentCommandResponse {
  equipment_id: string;
  action: string;
  success: boolean;
  requested_state: Record<string, unknown>;
  message: string | null;
}

export interface EquipmentStateLogResponse {
  id: string;
  equipment_id: string;
  action: string;
  source: string;
  state_before: Record<string, unknown> | null;
  state_after: Record<string, unknown> | null;
  metadata_: Record<string, unknown> | null;
  created_at: string;
}

export interface TestConnectionResponse {
  reachable: boolean;
  protocol: string;
  message: string;
  device_info: Record<string, unknown> | null;
}

export function listEquipment(token: string, tentId?: string, enabled?: boolean) {
  const qs = new URLSearchParams();
  if (tentId) qs.set("tent_id", tentId);
  if (enabled !== undefined) qs.set("enabled", String(enabled));
  const q = qs.toString();
  return apiFetch<PaginatedResponse<EquipmentResponse>>(`/equipment/${q ? `?${q}` : ""}`, { token });
}

export function getEquipment(token: string, id: string) {
  return apiFetch<EquipmentResponse>(`/equipment/${id}`, { token });
}

export function createEquipment(token: string, data: {
  name: string;
  equipment_type: string;
  protocol: string;
  protocol_config: Record<string, unknown>;
  capabilities?: string[];
  tent_id?: string;
  max_on_minutes?: number | null;
  cooldown_minutes?: number;
  conflicts_with?: string[];
}) {
  return apiFetch<EquipmentResponse>("/equipment/", { method: "POST", body: JSON.stringify(data), token });
}

export function updateEquipment(token: string, id: string, data: Partial<{
  name: string;
  equipment_type: string;
  protocol: string;
  protocol_config: Record<string, unknown>;
  capabilities: string[];
  tent_id: string | null;
  max_on_minutes: number | null;
  cooldown_minutes: number;
  conflicts_with: string[];
  enabled: boolean;
}>) {
  return apiFetch<EquipmentResponse>(`/equipment/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deleteEquipment(token: string, id: string) {
  return apiFetch<void>(`/equipment/${id}`, { method: "DELETE", token });
}

export function sendEquipmentCommand(token: string, id: string, data: { action: string; value?: number }) {
  return apiFetch<EquipmentCommandResponse>(`/equipment/${id}/command`, { method: "POST", body: JSON.stringify(data), token });
}

export function getEquipmentHistory(token: string, id: string, source?: string) {
  const qs = new URLSearchParams();
  if (source) qs.set("source", source);
  const q = qs.toString();
  return apiFetch<PaginatedResponse<EquipmentStateLogResponse>>(`/equipment/${id}/history${q ? `?${q}` : ""}`, { token });
}

export function testEquipmentConnection(token: string, id: string) {
  return apiFetch<TestConnectionResponse>(`/equipment/${id}/test`, { method: "POST", token });
}
