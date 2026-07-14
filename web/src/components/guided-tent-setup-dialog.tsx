"use client";

import { useEffect, useMemo, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  createDeviceMap,
  createIntegration,
  discoverDevices,
  listTents,
  triggerSync,
  type DiscoveredDeviceResponse,
  type TentResponse,
} from "@/lib/api";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";

type BrandKey = "vivosun" | "ac_infinity" | "mars_hydro" | "spider_farmer" | "other";
type SkillPreset = "starter" | "intermediate" | "pro";
type ControlStack = "brand_app" | "tuya" | "home_assistant" | "mqtt" | "manual";
type ConnectorType = "vivosun" | "tuya" | "home_assistant" | "mqtt_generic" | "generic_webhook";
type GuidedDetailTab = "devices" | "logs";

interface GuidedSetupResult {
  integrationId?: string;
  mappedCount?: number;
  discoveredCount?: number;
  openTab?: GuidedDetailTab;
}

const BRAND_OPTIONS: { value: BrandKey; label: string }[] = [
  { value: "vivosun", label: "Vivosun" },
  { value: "ac_infinity", label: "AC Infinity" },
  { value: "mars_hydro", label: "Mars Hydro" },
  { value: "spider_farmer", label: "Spider Farmer" },
  { value: "other", label: "Other / Mixed" },
];

const SKILL_PRESETS: Record<SkillPreset, { label: string; pollIntervalS: number; guidance: string }> = {
  starter: {
    label: "Starter",
    pollIntervalS: 300,
    guidance: "Lower API load and fewer moving parts while you learn the system.",
  },
  intermediate: {
    label: "Intermediate",
    pollIntervalS: 180,
    guidance: "Balanced cadence for better responsiveness without noisy sync loops.",
  },
  pro: {
    label: "Pro",
    pollIntervalS: 120,
    guidance: "Faster updates for tighter operations and active environment tuning.",
  },
};

const CONTROL_STACK_OPTIONS: { value: ControlStack; label: string; description: string }[] = [
  {
    value: "brand_app",
    label: "Brand app / native controller",
    description: "Use the vendor app and bundled controller as your primary source.",
  },
  {
    value: "tuya",
    label: "Tuya / Smart Life",
    description: "Devices are linked to Tuya Cloud or Smart Life.",
  },
  {
    value: "home_assistant",
    label: "Home Assistant",
    description: "You centralize devices in Home Assistant.",
  },
  {
    value: "mqtt",
    label: "MQTT",
    description: "Telemetry is available on an MQTT broker.",
  },
  {
    value: "manual",
    label: "Manual / unknown",
    description: "No cloud connector yet. Start with a webhook/manual fallback.",
  },
];

const DEFAULT_COMPONENTS = {
  inline_fan: true,
  oscillating_fan: true,
  grow_light: true,
  humidifier: false,
  heater: false,
};

function resolveConnectorType(brand: BrandKey, controlStack: ControlStack): ConnectorType {
  if (brand === "vivosun" && controlStack === "brand_app") return "vivosun";
  if (controlStack === "tuya") return "tuya";
  if (controlStack === "home_assistant") return "home_assistant";
  if (controlStack === "mqtt") return "mqtt_generic";
  if (brand === "vivosun") return "vivosun";
  return "generic_webhook";
}

function defaultNameFromBrand(brand: BrandKey): string {
  const label = BRAND_OPTIONS.find((b) => b.value === brand)?.label ?? "Tent";
  return `${label} Tent Controller`;
}

function authHintForConnector(connector: ConnectorType): string {
  if (connector === "vivosun") {
    return "If login fails, verify this is your Vivosun app password. Reset it in the Vivosun app, then retry.";
  }
  if (connector === "tuya") {
    return "Use your Tuya Cloud project Access ID and Access Secret, plus the app user UID if available.";
  }
  if (connector === "home_assistant") {
    return "Use your Home Assistant base URL and a long-lived access token.";
  }
  if (connector === "mqtt_generic") {
    return "MQTT generic mode starts as monitoring-first. You can refine topic mappings afterward.";
  }
  return "Generic webhook mode is a safe fallback when no direct cloud connector is available.";
}

interface GuidedTentSetupDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCompleted?: (result?: GuidedSetupResult) => void;
  source?: "integrations" | "onboarding";
}

const BRAND_MODEL_OPTIONS: Record<BrandKey, string[]> = {
  vivosun: ["GrowHub E25", "GrowHub E42", "GrowHub E42A", "GrowHub E42A+", "GrowHub X42", "VGrow"],
  ac_infinity: ["Controller 69", "Controller 69 PRO", "Controller AI+", "UIS-compatible setup"],
  mars_hydro: ["iConnect controller", "FC/TS smart dimmer setup", "App bridge setup"],
  spider_farmer: ["GGS Controller Kit", "SE/SF dimmer + timer setup", "App bridge setup"],
  other: ["Custom / mixed"],
};

function brandHint(brand: BrandKey): string {
  if (brand === "vivosun") {
    return "Common kits include E42A+ controllers with inline fan, oscillating fan, and light bundles.";
  }
  if (brand === "ac_infinity") {
    return "Most kits center around UIS controllers and mixed device chains; map each device explicitly.";
  }
  if (brand === "mars_hydro") {
    return "Controller and app support varies by lineup. If direct integration fails, use Home Assistant or MQTT bridge.";
  }
  if (brand === "spider_farmer") {
    return "Smart control support is improving but can differ by region/model. Keep fallback connectors available.";
  }
  return "Mixed ecosystems work best with per-device confirmation and conservative polling defaults.";
}

function buildSetupMetadata({
  brand,
  controlStack,
  controllerModel,
  kitLevel,
  components,
  skillPreset,
}: {
  brand: BrandKey;
  controlStack: ControlStack;
  controllerModel: string;
  kitLevel: "entry" | "pro";
  components: typeof DEFAULT_COMPONENTS;
  skillPreset: SkillPreset;
}) {
  return {
    guided_setup: true,
    brand,
    control_stack: controlStack,
    controller_model: controllerModel.trim() || null,
    kit_level: kitLevel,
    components,
    skill_preset: skillPreset,
    setup_version: "2026-07-guided-v1",
  };
}

function confidenceForDevice({
  device,
  brand,
  controllerModel,
}: {
  device: DiscoveredDeviceResponse;
  brand: BrandKey;
  controllerModel: string;
}): "high" | "medium" | "low" {
  const type = (device.device_type || "").toLowerCase();
  const name = (device.name || "").toLowerCase();
  const model = controllerModel.toLowerCase();

  const hasExpectedType =
    type.includes("growhub") ||
    type.includes("fan") ||
    type.includes("humidifier") ||
    type.includes("heater") ||
    type.includes("light") ||
    type.includes("camera");

  const matchesBrandKeyword =
    (brand === "vivosun" && (name.includes("vivosun") || name.includes("growhub") || type.includes("growhub"))) ||
    (brand === "ac_infinity" && (name.includes("ac infinity") || name.includes("uis"))) ||
    (brand === "mars_hydro" && name.includes("mars")) ||
    (brand === "spider_farmer" && (name.includes("spider") || name.includes("farmer")));

  const matchesControllerModel = !!model && (name.includes(model) || type.includes(model));

  if (matchesBrandKeyword && (hasExpectedType || matchesControllerModel)) return "high";
  if (hasExpectedType || matchesBrandKeyword || matchesControllerModel) return "medium";
  return "low";
}

function confidenceBadgeVariant(level: "high" | "medium" | "low"): "default" | "secondary" | "destructive" {
  if (level === "high") return "default";
  if (level === "medium") return "secondary";
  return "destructive";
}

export function GuidedTentSetupDialog({
  open,
  onOpenChange,
  onCompleted,
  source = "integrations",
}: GuidedTentSetupDialogProps) {
  const [step, setStep] = useState(0);
  const [loadingTents, setLoadingTents] = useState(false);
  const [tents, setTents] = useState<TentResponse[]>([]);

  const [brand, setBrand] = useState<BrandKey>("vivosun");
  const [controlStack, setControlStack] = useState<ControlStack>("brand_app");
  const [controllerModel, setControllerModel] = useState("");
  const [kitLevel, setKitLevel] = useState<"entry" | "pro">("entry");
  const [components, setComponents] = useState(DEFAULT_COMPONENTS);
  const [skillPreset, setSkillPreset] = useState<SkillPreset>("intermediate");

  const [integrationName, setIntegrationName] = useState(defaultNameFromBrand("vivosun"));
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [tuyaAccessId, setTuyaAccessId] = useState("");
  const [tuyaAccessSecret, setTuyaAccessSecret] = useState("");
  const [tuyaRegion, setTuyaRegion] = useState("us");
  const [tuyaUid, setTuyaUid] = useState("");
  const [haUrl, setHaUrl] = useState("");
  const [haToken, setHaToken] = useState("");
  const [mqttDescription, setMqttDescription] = useState("");

  const [saving, setSaving] = useState(false);
  const [integrationId, setIntegrationId] = useState<string | null>(null);
  const [discovered, setDiscovered] = useState<DiscoveredDeviceResponse[]>([]);
  const [discovering, setDiscovering] = useState(false);
  const [mapping, setMapping] = useState(false);
  const [finalSummary, setFinalSummary] = useState<{
    integrationId: string;
    mappedCount: number;
    discoveredCount: number;
    syncAttempted: boolean;
  } | null>(null);

  const [mapEnabled, setMapEnabled] = useState<Record<string, boolean>>({});
  const [mapTent, setMapTent] = useState<Record<string, string>>({});
  const [lowConfidenceConfirmed, setLowConfidenceConfirmed] = useState<Record<string, boolean>>({});

  const connectorType = useMemo(
    () => resolveConnectorType(brand, controlStack),
    [brand, controlStack],
  );

  const unconfirmedLowConfidenceCount = useMemo(() => {
    let count = 0;
    for (const device of discovered) {
      if (!mapEnabled[device.external_id]) continue;
      const confidence = confidenceForDevice({ device, brand, controllerModel });
      if (confidence === "low" && !lowConfidenceConfirmed[device.external_id]) {
        count += 1;
      }
    }
    return count;
  }, [discovered, mapEnabled, brand, controllerModel, lowConfidenceConfirmed]);

  useEffect(() => {
    if (open) {
      const suggested = defaultNameFromBrand(brand);
      setIntegrationName((cur) => (cur.trim() ? cur : suggested));
      void loadTents();
    }
  }, [open, brand]);

  useEffect(() => {
    setIntegrationName(defaultNameFromBrand(brand));
  }, [brand]);

  async function loadTents() {
    const token = getAccessToken();
    if (!token) return;
    setLoadingTents(true);
    try {
      const rows = await listTents(token);
      setTents(rows);
    } catch {
      setTents([]);
    } finally {
      setLoadingTents(false);
    }
  }

  function resetDialog() {
    setStep(0);
    setBrand("vivosun");
    setControlStack("brand_app");
    setControllerModel("");
    setKitLevel("entry");
    setComponents(DEFAULT_COMPONENTS);
    setSkillPreset("intermediate");
    setIntegrationName(defaultNameFromBrand("vivosun"));
    setEmail("");
    setPassword("");
    setTuyaAccessId("");
    setTuyaAccessSecret("");
    setTuyaRegion("us");
    setTuyaUid("");
    setHaUrl("");
    setHaToken("");
    setMqttDescription("");
    setSaving(false);
    setIntegrationId(null);
    setDiscovered([]);
    setDiscovering(false);
    setMapping(false);
    setFinalSummary(null);
    setMapEnabled({});
    setMapTent({});
    setLowConfidenceConfirmed({});
  }

  function closeDialog() {
    onOpenChange(false);
    resetDialog();
  }

  function buildConfig(): Record<string, unknown> {
    const setupMetadata = buildSetupMetadata({
      brand,
      controlStack,
      controllerModel,
      kitLevel,
      components,
      skillPreset,
    });

    if (connectorType === "vivosun") {
      return { email: email.trim(), password, setup_metadata: setupMetadata };
    }
    if (connectorType === "tuya") {
      return {
        access_id: tuyaAccessId.trim(),
        access_secret: tuyaAccessSecret,
        region: tuyaRegion.trim() || "us",
        uid: tuyaUid.trim() || undefined,
        setup_metadata: setupMetadata,
      };
    }
    if (connectorType === "home_assistant") {
      return { url: haUrl.trim(), token: haToken, setup_metadata: setupMetadata };
    }
    if (connectorType === "mqtt_generic") {
      return {
        description: mqttDescription.trim() || `${integrationName} (MQTT generic setup)`,
        setup_metadata: setupMetadata,
      };
    }
    return {
      brand,
      controller_model: controllerModel.trim() || null,
      kit_level: kitLevel,
      components,
      skill_preset: skillPreset,
      setup_metadata: setupMetadata,
      notes: "Generated from guided tent setup wizard",
    };
  }

  function canProceedFromAuth() {
    if (connectorType === "vivosun") return !!email.trim() && !!password;
    if (connectorType === "tuya") return !!tuyaAccessId.trim() && !!tuyaAccessSecret;
    if (connectorType === "home_assistant") return !!haUrl.trim() && !!haToken;
    return true;
  }

  async function handleCreateIntegration() {
    const token = getAccessToken();
    if (!token) return;
    if (!integrationName.trim()) {
      toast.error("Please enter an integration name.");
      return;
    }
    if (!canProceedFromAuth()) {
      toast.error("Please complete required credentials.");
      return;
    }

    setSaving(true);
    try {
      const created = await createIntegration(token, {
        type: connectorType,
        name: integrationName.trim(),
        config: buildConfig(),
        poll_interval_s: SKILL_PRESETS[skillPreset].pollIntervalS,
      });
      setIntegrationId(created.id);
      toast.success("Integration created. Running discovery...");
      setStep(3);
      await runDiscovery(created.id);
      onCompleted?.({ integrationId: created.id });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to create integration";
      toast.error(message);
    } finally {
      setSaving(false);
    }
  }

  async function runDiscovery(id: string) {
    const token = getAccessToken();
    if (!token) return;
    setDiscovering(true);
    try {
      const devices = await discoverDevices(token, id);
      setDiscovered(devices);
      const enabledState: Record<string, boolean> = {};
      const tentState: Record<string, string> = {};
      const lowConfidenceState: Record<string, boolean> = {};
      for (const d of devices) {
        enabledState[d.external_id] = false;
        tentState[d.external_id] = "";
        lowConfidenceState[d.external_id] = false;
      }
      setMapEnabled(enabledState);
      setMapTent(tentState);
      setLowConfidenceConfirmed(lowConfidenceState);
      if (devices.length === 0) {
        toast.info("No devices were discovered. You can map devices manually later.");
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Discovery failed";
      toast.error(message);
    } finally {
      setDiscovering(false);
    }
  }

  async function handleConfirmMappings() {
    if (!integrationId) {
      closeDialog();
      return;
    }
    const token = getAccessToken();
    if (!token) return;

    const selected = discovered.filter((d) => mapEnabled[d.external_id]);
    if (selected.length === 0) {
      toast.info("No devices selected. You can map them later from Integrations.");
      closeDialog();
      return;
    }

    const unconfirmedLowConfidence = selected.filter((d) => {
      const confidence = confidenceForDevice({ device: d, brand, controllerModel });
      return confidence === "low" && !lowConfidenceConfirmed[d.external_id];
    });
    if (unconfirmedLowConfidence.length > 0) {
      toast.error("Confirm each low-confidence device match before mapping.");
      return;
    }

    const needsTent = selected.some((d) => tents.length > 0 && !mapTent[d.external_id]);
    if (needsTent) {
      toast.error("Select a target tent for each confirmed device.");
      return;
    }

    setMapping(true);
    let createdCount = 0;
    let syncAttempted = false;
    try {
      for (const d of selected) {
        await createDeviceMap(token, integrationId, {
          external_id: d.external_id,
          external_name: d.name,
          tent_id: mapTent[d.external_id] || undefined,
          enabled: true,
        });
        createdCount += 1;
      }
      syncAttempted = true;
      await triggerSync(token, integrationId).catch(() => null);
      setFinalSummary({
        integrationId,
        mappedCount: createdCount,
        discoveredCount: discovered.length,
        syncAttempted,
      });
      setStep(4);
      onCompleted?.({ integrationId, mappedCount: createdCount, discoveredCount: discovered.length });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed while creating device mappings";
      toast.error(message);
    } finally {
      setMapping(false);
    }
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        if (!next) {
          closeDialog();
          return;
        }
        onOpenChange(next);
      }}
    >
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Guided Tent Setup</DialogTitle>
          <p className="text-sm text-muted-foreground">
            Adaptive setup for controller-based tent kits. Monitoring and mapping first, with per-device confirmation.
          </p>
        </DialogHeader>

        <div className="grid gap-4 py-2">
          <div className="flex items-center gap-2">
            {[0, 1, 2, 3, 4].map((idx) => (
              <div
                key={idx}
                className={`h-1.5 flex-1 rounded ${idx <= step ? "bg-primary" : "bg-muted"}`}
              />
            ))}
          </div>

          {step === 0 && (
            <Card>
              <CardContent className="grid gap-4 p-4">
                <div className="grid gap-2">
                  <Label>Brand / ecosystem</Label>
                  <Select value={brand} onValueChange={(v) => setBrand((v as BrandKey) ?? "vivosun")}>
                    <SelectTrigger>
                      <span>{BRAND_OPTIONS.find((b) => b.value === brand)?.label ?? "Select brand"}</span>
                    </SelectTrigger>
                    <SelectContent>
                      {BRAND_OPTIONS.map((b) => (
                        <SelectItem key={b.value} value={b.value}>
                          {b.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-2">
                  <Label>Control stack</Label>
                  <Select
                    value={controlStack}
                    onValueChange={(v) => setControlStack((v as ControlStack) ?? "brand_app")}
                  >
                    <SelectTrigger>
                      <span>
                        {CONTROL_STACK_OPTIONS.find((c) => c.value === controlStack)?.label ?? "Select stack"}
                      </span>
                    </SelectTrigger>
                    <SelectContent>
                      {CONTROL_STACK_OPTIONS.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground">
                    {CONTROL_STACK_OPTIONS.find((c) => c.value === controlStack)?.description}
                  </p>
                </div>

                <p className="text-xs text-muted-foreground">{brandHint(brand)}</p>

                <div className="grid gap-2 sm:grid-cols-2">
                  <div className="grid gap-2">
                    <Label>Controller model</Label>
                    <Select
                      value={controllerModel || "__custom__"}
                      onValueChange={(v) => {
                        if (v === "__custom__") {
                          setControllerModel("");
                          return;
                        }
                        setControllerModel(v ?? "");
                      }}
                    >
                      <SelectTrigger>
                        <span>{controllerModel || "Select model"}</span>
                      </SelectTrigger>
                      <SelectContent>
                        {BRAND_MODEL_OPTIONS[brand].map((model) => (
                          <SelectItem key={model} value={model}>
                            {model}
                          </SelectItem>
                        ))}
                        <SelectItem value="__custom__">Custom model...</SelectItem>
                      </SelectContent>
                    </Select>
                    <Input
                      value={controllerModel}
                      onChange={(e) => setControllerModel(e.target.value)}
                      placeholder="Type model if not listed"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label>Kit level</Label>
                    <Select
                      value={kitLevel}
                      onValueChange={(v) => setKitLevel((v as "entry" | "pro") ?? "entry")}
                    >
                      <SelectTrigger>
                        <span>{kitLevel === "pro" ? "Higher end" : "Entry / mid"}</span>
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="entry">Entry / mid</SelectItem>
                        <SelectItem value="pro">Higher end</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {step === 1 && (
            <Card>
              <CardContent className="grid gap-4 p-4">
                <div className="grid gap-2">
                  <Label>Included equipment</Label>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <EquipmentToggle
                      label="Inline fan"
                      checked={components.inline_fan}
                      onCheckedChange={(v) => setComponents((c) => ({ ...c, inline_fan: v }))}
                    />
                    <EquipmentToggle
                      label="Oscillating fan"
                      checked={components.oscillating_fan}
                      onCheckedChange={(v) => setComponents((c) => ({ ...c, oscillating_fan: v }))}
                    />
                    <EquipmentToggle
                      label="Grow light"
                      checked={components.grow_light}
                      onCheckedChange={(v) => setComponents((c) => ({ ...c, grow_light: v }))}
                    />
                    <EquipmentToggle
                      label="Humidifier"
                      checked={components.humidifier}
                      onCheckedChange={(v) => setComponents((c) => ({ ...c, humidifier: v }))}
                    />
                    <EquipmentToggle
                      label="Heater"
                      checked={components.heater}
                      onCheckedChange={(v) => setComponents((c) => ({ ...c, heater: v }))}
                    />
                  </div>
                </div>

                <div className="grid gap-2">
                  <Label>Skill preset</Label>
                  <Select
                    value={skillPreset}
                    onValueChange={(v) => setSkillPreset((v as SkillPreset) ?? "intermediate")}
                  >
                    <SelectTrigger>
                      <span>{SKILL_PRESETS[skillPreset].label}</span>
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="starter">Starter</SelectItem>
                      <SelectItem value="intermediate">Intermediate</SelectItem>
                      <SelectItem value="pro">Pro</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground">{SKILL_PRESETS[skillPreset].guidance}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {step === 2 && (
            <Card>
              <CardContent className="grid gap-4 p-4">
                <div className="flex items-center gap-2">
                  <Badge variant="secondary">Connector</Badge>
                  <p className="text-sm capitalize">{connectorType.replace(/_/g, " ")}</p>
                </div>

                <div className="grid gap-2">
                  <Label>Integration name</Label>
                  <Input
                    value={integrationName}
                    onChange={(e) => setIntegrationName(e.target.value)}
                    placeholder="My Tent Controller"
                  />
                </div>

                {connectorType === "vivosun" && (
                  <>
                    <div className="grid gap-2">
                      <Label>Vivosun email</Label>
                      <Input
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="you@example.com"
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label>Vivosun password</Label>
                      <Input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="App password"
                      />
                    </div>
                  </>
                )}

                {connectorType === "tuya" && (
                  <>
                    <div className="grid gap-2 sm:grid-cols-2">
                      <div className="grid gap-2">
                        <Label>Access ID</Label>
                        <Input
                          value={tuyaAccessId}
                          onChange={(e) => setTuyaAccessId(e.target.value)}
                          placeholder="Tuya Cloud Access ID"
                        />
                      </div>
                      <div className="grid gap-2">
                        <Label>Access Secret</Label>
                        <Input
                          type="password"
                          value={tuyaAccessSecret}
                          onChange={(e) => setTuyaAccessSecret(e.target.value)}
                          placeholder="Tuya Cloud Access Secret"
                        />
                      </div>
                    </div>
                    <div className="grid gap-2 sm:grid-cols-2">
                      <div className="grid gap-2">
                        <Label>Region</Label>
                        <Input
                          value={tuyaRegion}
                          onChange={(e) => setTuyaRegion(e.target.value)}
                          placeholder="us"
                        />
                      </div>
                      <div className="grid gap-2">
                        <Label>App user UID (optional)</Label>
                        <Input
                          value={tuyaUid}
                          onChange={(e) => setTuyaUid(e.target.value)}
                          placeholder="Linked user UID"
                        />
                      </div>
                    </div>
                  </>
                )}

                {connectorType === "home_assistant" && (
                  <>
                    <div className="grid gap-2">
                      <Label>Home Assistant URL</Label>
                      <Input
                        value={haUrl}
                        onChange={(e) => setHaUrl(e.target.value)}
                        placeholder="http://homeassistant.local:8123"
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label>Long-lived token</Label>
                      <Input
                        type="password"
                        value={haToken}
                        onChange={(e) => setHaToken(e.target.value)}
                        placeholder="Home Assistant token"
                      />
                    </div>
                  </>
                )}

                {connectorType === "mqtt_generic" && (
                  <div className="grid gap-2">
                    <Label>MQTT source notes (optional)</Label>
                    <Input
                      value={mqttDescription}
                      onChange={(e) => setMqttDescription(e.target.value)}
                      placeholder="e.g. Zigbee2MQTT tent telemetry"
                    />
                  </div>
                )}

                <p className="text-xs text-muted-foreground">{authHintForConnector(connectorType)}</p>
              </CardContent>
            </Card>
          )}

          {step === 3 && (
            <Card>
              <CardContent className="grid gap-4 p-4">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-medium">Discovery and mapping confirmation</p>
                    <p className="text-xs text-muted-foreground">
                      Confirm each discovered device before it is mapped to a tent.
                    </p>
                  </div>
                  {integrationId && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => runDiscovery(integrationId)}
                      disabled={discovering}
                    >
                      {discovering ? "Discovering..." : "Re-run discovery"}
                    </Button>
                  )}
                </div>

                {loadingTents ? (
                  <p className="text-xs text-muted-foreground">Loading tents...</p>
                ) : tents.length === 0 ? (
                  <p className="text-xs text-muted-foreground">
                    No tents found yet. You can still confirm devices now and assign tents later.
                  </p>
                ) : (
                  <p className="text-xs text-muted-foreground">{tents.length} tent(s) available for mapping.</p>
                )}

                {unconfirmedLowConfidenceCount > 0 && (
                  <div className="rounded border border-destructive/40 bg-destructive/5 p-3 text-xs text-muted-foreground">
                    {unconfirmedLowConfidenceCount} low-confidence device
                    {unconfirmedLowConfidenceCount === 1 ? " is" : "s are"} selected but not confirmed yet.
                    Confirm each one before continuing.
                  </div>
                )}

                {discovered.length === 0 ? (
                  <p className="rounded border border-dashed p-3 text-sm text-muted-foreground">
                    No devices discovered yet. You can finish setup and map devices manually later in Integrations.
                  </p>
                ) : (
                  <div className="grid gap-3">
                    {discovered.map((device) => {
                      const confidence = confidenceForDevice({ device, brand, controllerModel });
                      const selectedTentName = tents.find((t) => t.id === mapTent[device.external_id])?.name;
                      return (
                        <div key={device.external_id} className="rounded-lg border p-3">
                          <div className="flex flex-wrap items-center justify-between gap-3">
                            <div>
                              <p className="text-sm font-medium">{device.name}</p>
                              <p className="text-xs text-muted-foreground">
                                {device.device_type} · {device.external_id}
                              </p>
                              <div className="mt-1">
                                <Badge variant={confidenceBadgeVariant(confidence)} className="text-[10px] uppercase">
                                  {confidence} confidence
                                </Badge>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <Label className="text-xs text-muted-foreground">Map this device</Label>
                              <Switch
                                checked={!!mapEnabled[device.external_id]}
                                onCheckedChange={(checked) => {
                                  setMapEnabled((cur) => ({ ...cur, [device.external_id]: checked }));
                                  if (!checked) {
                                    setLowConfidenceConfirmed((cur) => ({
                                      ...cur,
                                      [device.external_id]: false,
                                    }));
                                  }
                                }}
                              />
                            </div>
                          </div>

                          {mapEnabled[device.external_id] && confidence === "low" && (
                            <div className="mt-3 rounded border border-destructive/30 bg-destructive/5 p-3">
                              <p className="text-xs text-muted-foreground">
                                This device is a low-confidence match. Confirm explicitly before mapping.
                              </p>
                              <Button
                                type="button"
                                size="sm"
                                variant={lowConfidenceConfirmed[device.external_id] ? "secondary" : "outline"}
                                className="mt-2"
                                onClick={() =>
                                  setLowConfidenceConfirmed((cur) => ({
                                    ...cur,
                                    [device.external_id]: !cur[device.external_id],
                                  }))
                                }
                              >
                                {lowConfidenceConfirmed[device.external_id]
                                  ? "Low-confidence match confirmed"
                                  : "Confirm low-confidence match"}
                              </Button>
                            </div>
                          )}

                          {mapEnabled[device.external_id] && tents.length > 0 && (
                            <div className="mt-3 grid gap-2">
                              <Label>Target tent</Label>
                              <Select
                                value={mapTent[device.external_id] || ""}
                                onValueChange={(value) =>
                                  setMapTent((cur) => ({ ...cur, [device.external_id]: value ?? "" }))
                                }
                              >
                                <SelectTrigger>
                                  <span>{selectedTentName ?? "Choose tent"}</span>
                                </SelectTrigger>
                                <SelectContent>
                                  {tents.map((tent) => (
                                    <SelectItem key={tent.id} value={tent.id}>
                                      {tent.name}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {step === 4 && finalSummary && (
            <Card>
              <CardContent className="grid gap-4 p-4">
                <div>
                  <p className="text-sm font-semibold">Setup complete</p>
                  <p className="text-xs text-muted-foreground">
                    Review what was configured and what to do next.
                  </p>
                </div>

                <div className="grid gap-2">
                  <ChecklistRow
                    label="Integration created"
                    value={integrationName}
                    ok={!!finalSummary.integrationId}
                  />
                  <ChecklistRow
                    label="Devices discovered"
                    value={`${finalSummary.discoveredCount}`}
                    ok={finalSummary.discoveredCount > 0}
                  />
                  <ChecklistRow
                    label="Devices mapped"
                    value={`${finalSummary.mappedCount}`}
                    ok={finalSummary.mappedCount > 0}
                  />
                  <ChecklistRow
                    label="Initial sync triggered"
                    value={finalSummary.syncAttempted ? "Yes" : "No"}
                    ok={finalSummary.syncAttempted}
                  />
                </div>

                <div className="rounded border bg-muted/30 p-3 text-xs text-muted-foreground">
                  Next best action: open Integrations and verify live readings on each mapped device.
                </div>

                {source === "integrations" && (
                  <div className="flex flex-wrap gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        onCompleted?.({
                          integrationId: finalSummary.integrationId,
                          mappedCount: finalSummary.mappedCount,
                          discoveredCount: finalSummary.discoveredCount,
                          openTab: "devices",
                        });
                        closeDialog();
                      }}
                    >
                      Open Device Mappings
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        onCompleted?.({
                          integrationId: finalSummary.integrationId,
                          mappedCount: finalSummary.mappedCount,
                          discoveredCount: finalSummary.discoveredCount,
                          openTab: "logs",
                        });
                        closeDialog();
                      }}
                    >
                      Open Sync Logs
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        <DialogFooter className="flex flex-wrap gap-2">
          {step > 0 ? (
            <Button variant="outline" onClick={() => setStep((s) => s - 1)}>
              Back
            </Button>
          ) : (
            <Button variant="outline" onClick={closeDialog}>
              Cancel
            </Button>
          )}

          {step < 2 && (
            <Button onClick={() => setStep((s) => s + 1)}>Next</Button>
          )}

          {step === 2 && (
            <Button onClick={handleCreateIntegration} disabled={saving || !integrationName.trim()}>
              {saving ? "Creating..." : "Create Integration"}
            </Button>
          )}

          {step === 3 && (
            <>
              <Button variant="outline" onClick={closeDialog} disabled={mapping}>
                Finish Later
              </Button>
              <Button onClick={handleConfirmMappings} disabled={mapping || discovering}>
                {mapping
                  ? "Saving mappings..."
                  : unconfirmedLowConfidenceCount > 0
                    ? `Confirm Mappings (${unconfirmedLowConfidenceCount} pending)`
                    : "Confirm Mappings"}
              </Button>
            </>
          )}

          {step === 4 && (
            <Button
              onClick={() => {
                toast.success("Guided setup complete.");
                closeDialog();
              }}
            >
              Done
            </Button>
          )}
        </DialogFooter>

        {source === "onboarding" && (
          <p className="text-xs text-muted-foreground">
            This setup is optional during onboarding. You can return to Integrations any time.
          </p>
        )}
      </DialogContent>
    </Dialog>
  );
}

function ChecklistRow({ label, value, ok }: { label: string; value: string; ok: boolean }) {
  return (
    <div className="flex items-center justify-between rounded border p-2">
      <div>
        <p className="text-xs font-medium">{label}</p>
        <p className="text-xs text-muted-foreground">{value}</p>
      </div>
      <Badge variant={ok ? "default" : "secondary"}>{ok ? "Done" : "Needs review"}</Badge>
    </div>
  );
}

function EquipmentToggle({
  label,
  checked,
  onCheckedChange,
}: {
  label: string;
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between rounded-lg border p-3">
      <Label>{label}</Label>
      <Switch checked={checked} onCheckedChange={onCheckedChange} />
    </div>
  );
}
