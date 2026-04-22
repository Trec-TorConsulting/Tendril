import { getRefreshToken, setTokens, clearTokens } from "@/lib/auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/v1";

interface FetchOptions extends RequestInit {
  token?: string;
}

class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
    this.name = "ApiError";
  }
}

async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { token, ...fetchOptions } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const url = `${API_BASE}${path}`;
  let res: Response;
  try {
    res = await fetch(url, {
      ...fetchOptions,
      headers,
    });
  } catch (networkErr) {
    console.error("[apiFetch] Network error:", url, fetchOptions.method || "GET", networkErr);
    const msg = networkErr instanceof Error ? networkErr.message : "Network error";
    throw new ApiError(0, `Network error on ${fetchOptions.method || "GET"} ${path}: ${msg}`);
  }

  // Auto-refresh on 401 if we have a refresh token
  if (res.status === 401 && token) {
    const rt = getRefreshToken();
    if (rt) {
      try {
        const refreshRes = await fetch(`${API_BASE}/auth/refresh`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: rt }),
        });
        if (refreshRes.ok) {
          const tokens = await refreshRes.json();
          setTokens(tokens.access_token, tokens.refresh_token);
          headers["Authorization"] = `Bearer ${tokens.access_token}`;
          const retryRes = await fetch(`${API_BASE}${path}`, {
            ...fetchOptions,
            headers,
          });
          if (retryRes.ok) {
            if (retryRes.status === 204) return undefined as T;
            return retryRes.json();
          }
          const retryBody = await retryRes.json().catch(() => ({ detail: retryRes.statusText }));
          throw new ApiError(retryRes.status, retryBody.detail || retryRes.statusText);
        } else {
          clearTokens();
          throw new ApiError(401, "Session expired. Please log in again.");
        }
      } catch (refreshErr) {
        if (refreshErr instanceof ApiError) throw refreshErr;
        clearTokens();
        throw new ApiError(401, "Session expired. Please log in again.");
      }
    }
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail || res.statusText);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
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

export function getMe(token: string) {
  return apiFetch<{ id: string; email: string; display_name: string | null; role: string; tenant_id: string; is_platform_admin: boolean; is_support: boolean }>(
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

export function listTenantMembers(token: string) {
  return apiFetch<TenantMember[]>("/tenants/members", { token });
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
export function updateProfile(token: string, data: { display_name?: string; email?: string }) {
  return apiFetch<{ id: string; email: string; display_name: string | null; role: string; tenant_id: string; is_platform_admin: boolean; is_support: boolean }>(
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

export function listDevices(token: string) {
  return apiFetch<DeviceResponse[]>("/devices", { token });
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

export function updateDevice(token: string, deviceId: string, data: { label?: string; tent_id?: string }) {
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

// Tents
export interface TentResponse {
  id: string;
  name: string;
  environment_type: string;
  latitude: number | null;
  longitude: number | null;
  camera_url: string | null;
  settings: Record<string, unknown> | null;
}

export function listTents(token: string) {
  return apiFetch<TentResponse[]>("/tents", { token });
}

export function getTent(token: string, id: string) {
  return apiFetch<TentResponse>(`/tents/${id}`, { token });
}

export function createTent(token: string, data: { name: string; environment_type?: string; latitude?: number; longitude?: number; camera_url?: string }) {
  return apiFetch<TentResponse>("/tents", { method: "POST", body: JSON.stringify(data), token });
}

export function updateTent(token: string, id: string, data: Partial<{ name: string; environment_type: string; latitude: number | null; longitude: number | null; camera_url: string | null }>) {
  return apiFetch<TentResponse>(`/tents/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deleteTent(token: string, id: string) {
  return apiFetch<void>(`/tents/${id}`, { method: "DELETE", token });
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

export function listGrows(token: string, params?: { status?: string; tent_id?: string }) {
  const qs = new URLSearchParams();
  if (params?.status) qs.set("status", params.status);
  if (params?.tent_id) qs.set("tent_id", params.tent_id);
  const q = qs.toString();
  return apiFetch<GrowResponse[]>(`/grows${q ? `?${q}` : ""}`, { token });
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
  settings: Record<string, unknown> | null;
}

export function listBuckets(token: string, growCycleId?: string) {
  const q = growCycleId ? `?grow_cycle_id=${growCycleId}` : "";
  return apiFetch<BucketResponse[]>(`/buckets${q}`, { token });
}

export function createBucket(token: string, data: { grow_cycle_id: string; label?: string; strain_name?: string; strain_id?: string; position?: number; volume_gallons?: number }) {
  return apiFetch<BucketResponse>("/buckets", { method: "POST", body: JSON.stringify(data), token });
}

export function updateBucket(token: string, id: string, data: Partial<{ label: string; strain_name: string; strain_id: string; growth_stage: string; status: string; volume_gallons: number }>) {
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

export function listSensorReadings(token: string, bucketId?: string, limit?: number) {
  const qs = new URLSearchParams();
  if (bucketId) qs.set("bucket_id", bucketId);
  if (limit) qs.set("limit", String(limit));
  const q = qs.toString();
  return apiFetch<SensorReadingResponse[]>(`/sensors${q ? `?${q}` : ""}`, { token });
}

export function getLatestReading(token: string, bucketId: string) {
  return apiFetch<SensorReadingResponse | null>(`/sensors/latest/${bucketId}`, { token });
}

export function getSensorDrift(token: string, bucketId: string, hours?: number) {
  const q = hours ? `?hours=${hours}` : "";
  return apiFetch<{ ph: unknown; ec: unknown }>(`/sensors/drift/${bucketId}${q}`, { token });
}

export function createSensorReading(token: string, data: {
  bucket_id: string;
  ph?: number;
  ec?: number;
  ppm?: number;
  water_temp_f?: number;
  water_level_pct?: number;
  dissolved_oxygen?: number;
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

export function listTentReadings(token: string, tentId?: string, limit?: number) {
  const qs = new URLSearchParams();
  if (tentId) qs.set("tent_id", tentId);
  if (limit) qs.set("limit", String(limit));
  const q = qs.toString();
  return apiFetch<TentReadingResponse[]>(`/tent-sensors${q ? `?${q}` : ""}`, { token });
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

export function listFeedingSchedules(token: string, growCycleId: string) {
  return apiFetch<FeedingScheduleResponse[]>(`/feeding/feeding?grow_cycle_id=${growCycleId}`, { token });
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

// Journal Entries
export interface JournalEntryResponse {
  id: string;
  bucket_id: string;
  event_type: string;
  content: string | null;
  payload: Record<string, unknown> | null;
  created_at: string;
}

export function listJournalEntries(token: string, bucketId?: string) {
  const q = bucketId ? `?bucket_id=${bucketId}` : "";
  return apiFetch<JournalEntryResponse[]>(`/journal${q}`, { token });
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

export function listStrains(token: string) {
  return apiFetch<StrainResponse[]>("/strains", { token });
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

export function listYields(token: string, bucketId?: string) {
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

export function listPhotos(token: string, bucketId: string) {
  return apiFetch<PhotoResponse[]>(`/photos?bucket_id=${bucketId}`, { token });
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
}

export function listGrowPhotos(token: string, growCycleId: string) {
  return apiFetch<GrowPhotoResponse[]>(`/photos/grow?grow_cycle_id=${growCycleId}`, { token });
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
  const res = await fetch(`${API_BASE_URL}/photos/grow`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
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
  return `${API_BASE_URL}/photos/grow/file/${photoId}?token=${encodeURIComponent(token)}`;
}

export function updateGrowPhoto(token: string, id: string, data: Partial<{ caption: string }>) {
  return apiFetch<GrowPhotoResponse>(`/photos/grow/${id}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function deleteGrowPhoto(token: string, id: string) {
  return apiFetch<void>(`/photos/grow/${id}`, { method: "DELETE", token });
}

export function timelapseUrl(token: string, growCycleId: string) {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/v1";
  return `${API_BASE_URL}/photos/grow/timelapse/${growCycleId}?token=${encodeURIComponent(token)}`;
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

export function listDoseProfiles(token: string, growCycleId: string) {
  return apiFetch<DoseProfileResponse[]>(`/feeding/doses?grow_cycle_id=${growCycleId}`, { token });
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
  return apiFetch<{ id: string; barcode: string; name: string; brand: string | null; npk: string | null }[]>(
    `/reference/nutrients?q=${encodeURIComponent(query)}`,
    { token },
  );
}

// AI
export function getAiChatWsUrl() {
  const base = API_BASE.replace(/^http/, "ws");
  return `${base}/ai/chat`;
}

export interface HealthCheckResult {
  id: string | null;
  score: number | null;
  issues: string[];
  actions: string[];
  raw_analysis: string;
  source: string;
  created_at: string | null;
}

export function runHealthCheck(token: string, data: { grow_id: string; observations: Record<string, string>; image_base64?: string; include_camera?: boolean }) {
  return apiFetch<HealthCheckResult>(
    "/ai/health-check",
    { method: "POST", body: JSON.stringify(data), token },
  );
}

export function getHealthCheckHistory(token: string, growId: string, limit = 10) {
  return apiFetch<{ items: HealthCheckResult[] }>(
    `/ai/health-check/${growId}/history?limit=${limit}`,
    { token },
  );
}

export function getCoachTip(token: string, growId: string) {
  return apiFetch<{ tip: string }>("/ai/coach-tip", {
    method: "POST",
    body: JSON.stringify({ grow_id: growId }),
    token,
  });
}

export function getAiInsight(token: string, growId: string, insightType: string) {
  return apiFetch<{ insight_type: string; result: unknown }>("/ai/insights", {
    method: "POST",
    body: JSON.stringify({ grow_id: growId, insight_type: insightType }),
    token,
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

export function listAutomationRules(token: string, growCycleId?: string) {
  const q = growCycleId ? `?grow_cycle_id=${growCycleId}` : "";
  return apiFetch<AutomationRuleResponse[]>(`/automation/rules${q}`, { token });
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

export function listAlerts(token: string, limit?: number) {
  const q = limit ? `?limit=${limit}` : "";
  return apiFetch<AlertResponse[]>(`/automation/alerts${q}`, { token });
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

export function listSchedules(token: string, tentId?: string) {
  const q = tentId ? `?tent_id=${tentId}` : "";
  return apiFetch<ScheduleResponse[]>(`/automation/schedules${q}`, { token });
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

export function listChannels(token: string) {
  return apiFetch<ChannelResponse[]>("/notifications/channels", { token });
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
  stripe_customer_id: string | null;
  stripe_subscription_id: string | null;
  portal_url: string | null;
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
  created_at: string;
}

export function listTasks(token: string, filters?: { status?: string; assigned_to?: string; category?: string; grow_cycle_id?: string; due_from?: string; due_to?: string }) {
  const params = new URLSearchParams();
  if (filters?.status) params.set("status", filters.status);
  if (filters?.assigned_to) params.set("assigned_to", filters.assigned_to);
  if (filters?.category) params.set("category", filters.category);
  if (filters?.grow_cycle_id) params.set("grow_cycle_id", filters.grow_cycle_id);
  if (filters?.due_from) params.set("due_from", filters.due_from);
  if (filters?.due_to) params.set("due_to", filters.due_to);
  const qs = params.toString();
  return apiFetch<TaskItem[]>(`/tasks${qs ? `?${qs}` : ""}`, { token });
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

export function adminListTenants(token: string) {
  return apiFetch<AdminTenantSummary[]>("/admin/tenants", { token });
}

export function adminListUsers(token: string) {
  return apiFetch<AdminUserSummary[]>("/admin/users", { token });
}

export function adminListTenantUsers(token: string, tenantId: string) {
  return apiFetch<AdminUserSummary[]>(`/admin/tenants/${tenantId}/users`, { token });
}

export function adminUpdateUserFlags(token: string, userId: string, data: { is_platform_admin?: boolean; is_support?: boolean; role?: string }) {
  return apiFetch<AdminUserSummary>(`/admin/users/${userId}`, { method: "PATCH", body: JSON.stringify(data), token });
}

export function adminGetStats(token: string) {
  return apiFetch<{ total_tenants: number; total_users: number; plans: Record<string, number> }>("/admin/stats", { token });
}

export { apiFetch, ApiError };
