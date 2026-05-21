import Link from "next/link";

export const metadata = {
  title: "Privacy Policy — Tendril",
  description: "Privacy Policy for the Tendril grow monitoring platform",
};

export default function PrivacyPolicyPage() {
  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      {/* Nav */}
      <nav className="border-b border-neutral-800 bg-neutral-900/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <Link href="/" className="text-xl font-bold text-green-500">🌿 Tendril</Link>
          <div className="flex gap-4">
            <Link href="/login" className="rounded px-4 py-2 text-sm text-neutral-300 hover:text-white">Log In</Link>
            <Link href="/register" className="rounded bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700">Sign Up Free</Link>
          </div>
        </div>
      </nav>

      <article className="mx-auto max-w-3xl px-4 py-16 prose prose-invert prose-neutral">
        <h1>Privacy Policy</h1>
        <p className="text-neutral-400"><strong>Last updated:</strong> May 6, 2026</p>

        <p><strong>Geek Info LLC</strong> (managed by Trec-Tor Consulting, &ldquo;we&rdquo;, &ldquo;us&rdquo;, &ldquo;our&rdquo;) operates the Tendril platform at tendril.trector.com. This Privacy Policy explains how we collect, use, and protect your information.</p>

        <h2>1. Information We Collect</h2>

        <h3>1.1 Account Information</h3>
        <ul>
          <li>Email address and display name</li>
          <li>Authentication credentials (hashed passwords, OAuth tokens)</li>
          <li>Billing information (processed and stored by Stripe; we do not store card numbers)</li>
        </ul>

        <h3>1.2 Grow Data</h3>
        <ul>
          <li>Grow cycle information (types, stages, dates, notes)</li>
          <li>Sensor readings (pH, EC, temperature, humidity)</li>
          <li>Photos uploaded for health analysis</li>
          <li>Journal entries and feeding logs</li>
          <li>Expense and ROI tracking data</li>
          <li>Automation rules and notification preferences</li>
        </ul>

        <h3>1.3 Device Information</h3>
        <ul>
          <li>ESP32 device identifiers and configuration</li>
          <li>MQTT connection metadata</li>
          <li>IP addresses for security and rate limiting</li>
        </ul>

        <h3>1.4 Usage Data</h3>
        <ul>
          <li>Pages visited and features used (for product improvement)</li>
          <li>API request logs (retained 30 days for debugging)</li>
          <li>Error reports and performance metrics</li>
        </ul>

        <h2>2. How We Use Your Information</h2>
        <ul>
          <li><strong>Provide the Service:</strong> Store and display your grow data, process sensor readings, generate AI insights</li>
          <li><strong>Billing:</strong> Process subscription payments via Stripe, calculate usage metering</li>
          <li><strong>Communication:</strong> Send transactional emails (billing receipts, alerts, password resets)</li>
          <li><strong>Security:</strong> Detect abuse, prevent fraud, enforce rate limits</li>
          <li><strong>Improvement:</strong> Anonymized, aggregated usage patterns to improve the product</li>
        </ul>

        <h2>3. What We Do NOT Do</h2>
        <ul>
          <li>We do <strong>not</strong> sell your personal data to third parties</li>
          <li>We do <strong>not</strong> use your grow data for advertising</li>
          <li>We do <strong>not</strong> share identifiable data with other users (multi-tenant isolation via Row Level Security)</li>
          <li>We do <strong>not</strong> train AI models on your private data without explicit consent</li>
        </ul>

        <h2>4. Data Storage & Security</h2>
        <ul>
          <li>Data is stored in PostgreSQL with Row Level Security (RLS) ensuring tenant isolation</li>
          <li>All connections are encrypted in transit (TLS 1.3)</li>
          <li>Sensitive fields (payment credentials, integration secrets) are encrypted at rest (AES-256)</li>
          <li>Authentication uses httpOnly, secure cookies with CSRF protection</li>
          <li>Infrastructure is hosted on private Kubernetes clusters in the United States</li>
        </ul>

        <h2>5. Third-Party Services</h2>
        <p>We use the following third-party services that may process your data:</p>
        <table className="text-sm">
          <thead>
            <tr><th>Service</th><th>Purpose</th><th>Data Shared</th></tr>
          </thead>
          <tbody>
            <tr><td>Stripe</td><td>Payment processing</td><td>Email, billing address</td></tr>
            <tr><td>Google (Gemini)</td><td>AI health analysis</td><td>Plant photos (ephemeral, not stored by Google)</td></tr>
            <tr><td>Resend</td><td>Transactional email</td><td>Email address, notification content</td></tr>
            <tr><td>OpenWeather</td><td>Weather data</td><td>Location coordinates (if outdoor grows)</td></tr>
          </tbody>
        </table>

        <h2>6. Data Retention</h2>
        <ul>
          <li><strong>Active accounts:</strong> Data retained for the life of the account</li>
          <li><strong>Cancelled subscriptions:</strong> Data retained indefinitely on Free tier</li>
          <li><strong>Deleted accounts:</strong> Data retained 30 days (recovery window), then permanently purged</li>
          <li><strong>API logs:</strong> Retained 30 days</li>
          <li><strong>Sensor data:</strong> Retention varies by plan (Free: 90 days, Paid: unlimited)</li>
        </ul>

        <h2>7. Your Rights (GDPR/CCPA)</h2>
        <p>Regardless of your location, we provide these rights to all users:</p>
        <ul>
          <li><strong>Access:</strong> Export all your data from Account Settings</li>
          <li><strong>Rectification:</strong> Update your information from your profile</li>
          <li><strong>Deletion:</strong> Request account deletion from Account Settings (30-day processing)</li>
          <li><strong>Portability:</strong> Export data in JSON format via the API or dashboard</li>
          <li><strong>Objection:</strong> Opt out of non-essential communications from notification preferences</li>
        </ul>
        <p>To exercise these rights, use the in-app tools or contact <a href="mailto:privacy@tendrilgrow.com" className="text-green-500">privacy@tendrilgrow.com</a>.</p>

        <h2>8. Cookies</h2>
        <ul>
          <li><strong>access_token:</strong> httpOnly session cookie for authentication (15-minute expiry)</li>
          <li><strong>refresh_token:</strong> httpOnly cookie for session renewal (7-day expiry)</li>
          <li><strong>csrf_token:</strong> JavaScript-readable CSRF protection token</li>
        </ul>
        <p>We do not use tracking cookies, advertising cookies, or third-party analytics cookies.</p>

        <h2>9. Children&rsquo;s Privacy</h2>
        <p>The Service is not intended for users under 18. We do not knowingly collect information from minors.</p>

        <h2>10. International Data Transfers</h2>
        <p>Data is stored and processed in the United States. By using the Service, you consent to the transfer of your data to the US. We implement appropriate safeguards in compliance with applicable data protection laws.</p>

        <h2>11. Changes to This Policy</h2>
        <p>We may update this Privacy Policy periodically. Material changes will be communicated via email at least 30 days before taking effect. The &ldquo;Last updated&rdquo; date will be revised accordingly.</p>

        <h2>12. Contact</h2>
        <p>For privacy-related questions or data requests:</p>
        <ul>
          <li>Email: <a href="mailto:privacy@tendrilgrow.com" className="text-green-500">privacy@tendrilgrow.com</a></li>
          <li>Entity: Geek Info LLC, New Jersey, USA</li>
        </ul>

        <div className="mt-12 border-t border-neutral-800 pt-6 text-sm text-neutral-500">
          <p>Powered by <a href="https://www.trector.com" target="_blank" rel="noopener noreferrer" className="hover:text-neutral-300">Trec-Tor Consulting</a></p>
        </div>
      </article>
    </div>
  );
}
