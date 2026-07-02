"use client";

import Link from "next/link";

const TIERS = [
  {
    name: "Seedling",
    price: "Free",
    description: "Get started with basic grow tracking.",
    features: [
      "1 grow, 2 devices",
      "50 journal entries/mo",
      "10 AI analyses/mo",
      "1 GB storage",
      "Community support",
    ],
    cta: "Get Started",
    href: "/register",
    highlighted: false,
  },
  {
    name: "Hobby",
    price: "$9.99",
    period: "/mo",
    description: "For hobbyist growers with IoT and automation.",
    features: [
      "5 grows, 10 devices",
      "Unlimited journal entries",
      "50 AI analyses/mo",
      "10 GB storage",
      "5 automations",
      "3 integrations",
      "Email support",
    ],
    cta: "Start Free Trial",
    href: "/register?plan=hobby",
    highlighted: false,
  },
  {
    name: "Pro",
    price: "$29.99",
    period: "/mo",
    description: "Advanced AI and analytics for serious cultivators.",
    features: [
      "25 grows, 50 devices",
      "500 AI analyses/mo",
      "100 GB storage",
      "Unlimited automations",
      "10 integrations",
      "Priority support",
      "Weather automation",
    ],
    cta: "Start Free Trial",
    href: "/register?plan=pro",
    highlighted: true,
  },
  {
    name: "Commercial",
    price: "$79.99",
    period: "/mo",
    description: "Teams, audit trails, API access, and compliance.",
    features: [
      "100 grows, 200 devices",
      "5 team members",
      "Unlimited AI & storage",
      "API key access",
      "Audit trail logging",
      "Custom grow types",
      "Task management",
    ],
    cta: "Start Free Trial",
    href: "/register?plan=commercial",
    highlighted: false,
  },
  {
    name: "Enterprise",
    price: "$249.99",
    period: "/mo",
    description: "Large operations with white-label and SLA.",
    features: [
      "Unlimited everything",
      "25 team members",
      "White-label branding",
      "SSO/SAML",
      "Custom domain",
      "Dedicated support",
      "SLA guarantee",
    ],
    cta: "Contact Sales",
    href: "/register?plan=enterprise",
    highlighted: false,
  },
  {
    name: "Dedicated",
    price: "Custom",
    description: "Your own servers, your own domain, unlimited.",
    features: [
      "Dedicated infrastructure",
      "Custom domain & branding",
      "Unlimited everything",
      "Priority SLA",
      "Custom integrations",
      "On-premise option",
    ],
    cta: "Contact Sales",
    href: "mailto:info@tendrilgrow.com",
    highlighted: false,
  },
];

const FEATURES = [
  {
    icon: "🌱",
    title: "12 Grow Types",
    description: "DWC, RDWC, NFT, Aeroponics, Soil, and more — each with tailored sensors, terminology, and AI context.",
  },
  {
    icon: "🤖",
    title: "AI-Powered Insights",
    description: "Chat with your AI grow assistant, get health checks, harvest predictions, and nutrient advice.",
  },
  {
    icon: "📡",
    title: "IoT Sensor Integration",
    description: "Connect ESP32 sensors via MQTT for real-time pH, EC, temperature, and humidity monitoring.",
  },
  {
    icon: "⚡",
    title: "Smart Automation",
    description: "Set threshold-based rules that trigger alerts and actions when sensors drift out of range.",
  },
  {
    icon: "🌦️",
    title: "Weather Integration",
    description: "Outdoor and greenhouse grows get automatic weather monitoring with frost and heat alerts.",
  },
  {
    icon: "📊",
    title: "Analytics & Reports",
    description: "Track trends, compare grows, and generate PDF reports with sensor data and photos.",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      {/* Nav */}
      <nav className="border-b border-neutral-800 bg-neutral-900/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <span className="text-xl font-bold text-green-500">🌿 Tendril</span>
          <div className="flex gap-4">
            <Link href="/login" className="rounded px-4 py-2 text-sm text-neutral-300 hover:text-white">
              Log In
            </Link>
            <Link
              href="/register"
              className="rounded bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700"
            >
              Sign Up Free
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="mx-auto max-w-4xl px-4 py-24 text-center">
        <h1 className="mb-6 text-5xl font-bold leading-tight tracking-tight">
          Grow Smarter with{" "}
          <span className="text-green-500">AI-Powered</span> Cultivation
        </h1>
        <p className="mx-auto mb-8 max-w-2xl text-lg text-neutral-400">
          Tendril is the dynamic grow assistant that combines IoT sensors, automation rules,
          and AI insights to help you achieve better harvests — from hobby to commercial scale.
        </p>
        <div className="flex justify-center gap-4">
          <Link
            href="/register"
            className="rounded-lg bg-green-600 px-8 py-3 text-lg font-semibold text-white hover:bg-green-700"
          >
            Start Growing Free
          </Link>
          <a
            href="#features"
            className="rounded-lg border border-neutral-700 px-8 py-3 text-lg text-neutral-300 hover:border-neutral-500"
          >
            Learn More
          </a>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="border-t border-neutral-800 bg-neutral-900/50 py-20">
        <div className="mx-auto max-w-6xl px-4">
          <h2 className="mb-12 text-center text-3xl font-bold">Everything You Need to Grow</h2>
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map((f) => (
              <div key={f.title} className="rounded-lg border border-neutral-800 bg-neutral-900 p-6">
                <span className="mb-3 block text-3xl">{f.icon}</span>
                <h3 className="mb-2 text-lg font-semibold text-white">{f.title}</h3>
                <p className="text-sm text-neutral-400">{f.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="border-t border-neutral-800 py-20">
        <div className="mx-auto max-w-6xl px-4">
          <h2 className="mb-4 text-center text-3xl font-bold">Simple, Transparent Pricing</h2>
          <p className="mb-12 text-center text-neutral-400">Start free, upgrade when you need more.</p>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {TIERS.map((tier) => (
              <div
                key={tier.name}
                className={`flex flex-col rounded-lg border p-6 ${
                  tier.highlighted
                    ? "border-green-600 bg-green-900/10"
                    : "border-neutral-800 bg-neutral-900"
                }`}
              >
                {tier.highlighted && (
                  <span className="mb-2 inline-block self-start rounded bg-green-600 px-2 py-0.5 text-xs font-medium text-white">
                    Most Popular
                  </span>
                )}
                <h3 className="text-xl font-bold text-white">{tier.name}</h3>
                <div className="mt-2 mb-4">
                  <span className="text-3xl font-bold text-white">{tier.price}</span>
                  {tier.period && <span className="text-neutral-400">{tier.period}</span>}
                </div>
                <p className="mb-4 text-sm text-neutral-400">{tier.description}</p>
                <ul className="mb-6 flex-1 space-y-2">
                  {tier.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm text-neutral-300">
                      <span className="mt-0.5 text-green-500">✓</span>
                      {f}
                    </li>
                  ))}
                </ul>
                <Link
                  href={tier.href}
                  className={`block rounded-lg py-2 text-center text-sm font-medium ${
                    tier.highlighted
                      ? "bg-green-600 text-white hover:bg-green-700"
                      : "border border-neutral-700 text-neutral-300 hover:border-neutral-500"
                  }`}
                >
                  {tier.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-neutral-800 py-8">
        <div className="mx-auto max-w-6xl px-4 text-center text-sm text-neutral-500">
          <p className="mb-2">© {new Date().getFullYear()} Tendril — Built for growers, by growers.</p>
          <p className="flex items-center justify-center gap-4">
            <Link href="/terms" className="hover:text-neutral-300">Terms of Service</Link>
            <span>·</span>
            <Link href="/privacy" className="hover:text-neutral-300">Privacy Policy</Link>
            <span>·</span>
            <a href="mailto:info@tendrilgrow.com" className="hover:text-neutral-300">Contact</a>
          </p>
          <p className="mt-2 text-neutral-600">Powered by <a href="https://www.trector.com" target="_blank" rel="noopener noreferrer" className="hover:text-neutral-300">Trec-Tor Consulting</a></p>
        </div>
      </footer>
    </div>
  );
}
