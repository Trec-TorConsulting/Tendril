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
        <p className="text-neutral-400"><strong>Effective Date:</strong> June 11, 2026 &nbsp;|&nbsp; <strong>Last Updated:</strong> June 11, 2026</p>

        <p><strong>Geek Info LLC</strong>, a New Jersey limited liability company managed by Trec-Tor Consulting (&ldquo;Company,&rdquo; &ldquo;we,&rdquo; &ldquo;us,&rdquo; or &ldquo;our&rdquo;), operates the Tendril platform at tendrilgrow.com and related services. This Privacy Policy describes how we collect, use, disclose, retain, and protect your personal information when you access or use the Tendril platform, website, mobile applications, APIs, hardware, and related services (collectively, the &ldquo;Service&rdquo;).</p>

        <p><strong>BY CREATING AN ACCOUNT OR USING THE SERVICE, YOU ACKNOWLEDGE THAT YOU HAVE READ, UNDERSTOOD, AND CONSENT TO THE PRACTICES DESCRIBED IN THIS PRIVACY POLICY. IF YOU DO NOT AGREE, DO NOT USE THE SERVICE.</strong></p>

        <p>This Privacy Policy is designed to comply with the European Union General Data Protection Regulation (GDPR), the California Consumer Privacy Act as amended by the California Privacy Rights Act (CCPA/CPRA), the New Jersey Data Privacy Act (NJDPA), the Virginia Consumer Data Protection Act (VCDPA), the Colorado Privacy Act (CPA), the Connecticut Data Privacy Act (CTDPA), and other applicable data protection laws.</p>

        {/* ===== SECTION 1-6: Collection, Use, Sharing ===== */}

        <h2>1. Information We Collect</h2>
        <p>We collect information in the following categories:</p>

        <h3>1.1 Information You Provide Directly</h3>
        <table className="text-sm">
          <thead>
            <tr><th>Category</th><th>Data Elements</th><th>Purpose</th></tr>
          </thead>
          <tbody>
            <tr><td>Account Information</td><td>Email address, display name, organization name, password (hashed with bcrypt, never stored in plaintext)</td><td>Account creation, authentication, communication</td></tr>
            <tr><td>Billing Information</td><td>Name, billing address, payment method (processed and stored exclusively by Stripe; we never receive or store full card numbers, CVVs, or bank account details)</td><td>Payment processing, tax compliance</td></tr>
            <tr><td>Grow Data</td><td>Grow cycle information, plant types, growth stages, dates, notes, strain information, yield records</td><td>Core service functionality</td></tr>
            <tr><td>Journal Content</td><td>Text entries, feeding logs, observations, expense records</td><td>Grow journaling features</td></tr>
            <tr><td>Photos &amp; Media</td><td>Plant photos, environment images, documents</td><td>Health analysis, grow records, AI features</td></tr>
            <tr><td>Automation Configuration</td><td>Rules, schedules, thresholds, notification preferences</td><td>Automation and alerting features</td></tr>
            <tr><td>Support Communications</td><td>Emails, chat messages, feedback submitted to us</td><td>Customer support, product improvement</td></tr>
          </tbody>
        </table>

        <h3>1.2 Information Collected Automatically</h3>
        <table className="text-sm">
          <thead>
            <tr><th>Category</th><th>Data Elements</th><th>Purpose</th></tr>
          </thead>
          <tbody>
            <tr><td>Sensor/Telemetry Data</td><td>Temperature, humidity, soil moisture, pH, EC/TDS, dissolved oxygen, water level, VPD, CO2, light intensity, and other environmental measurements from connected IoT devices</td><td>Environmental monitoring, alerting, AI analysis</td></tr>
            <tr><td>Device Information</td><td>ESP32 device identifiers, MAC addresses, firmware versions, hardware configuration, MQTT connection metadata</td><td>Device management, troubleshooting</td></tr>
            <tr><td>Network Information</td><td>IP addresses, request headers, TLS fingerprints</td><td>Security, rate limiting, fraud prevention</td></tr>
            <tr><td>Usage Data</td><td>Pages visited, features used, click patterns, session duration, referral source</td><td>Product improvement, analytics</td></tr>
            <tr><td>Technical Data</td><td>Browser type, operating system, screen resolution, device type, timezone</td><td>Compatibility, debugging</td></tr>
            <tr><td>API Logs</td><td>Request paths, response codes, timestamps, latency</td><td>Debugging, performance monitoring, security</td></tr>
            <tr><td>Error Data</td><td>Error messages, stack traces, application state at time of error</td><td>Bug fixing, stability improvement</td></tr>
          </tbody>
        </table>

        <h3>1.3 Information from Third Parties</h3>
        <table className="text-sm">
          <thead>
            <tr><th>Source</th><th>Data</th><th>Purpose</th></tr>
          </thead>
          <tbody>
            <tr><td>OAuth Providers (Google, GitHub)</td><td>Email, name, profile picture (only if you choose OAuth login)</td><td>Account authentication</td></tr>
            <tr><td>Stripe</td><td>Payment status, subscription state, invoice history</td><td>Billing management</td></tr>
            <tr><td>Weather Services (OpenWeather, Open-Meteo, Ecowitt)</td><td>Weather data associated with your configured locations</td><td>Environmental context for grows</td></tr>
            <tr><td>Integration Connectors (Pulse Grow, Ecowitt)</td><td>Device data, sensor readings from connected third-party systems</td><td>Unified monitoring dashboard</td></tr>
          </tbody>
        </table>

        <h3>1.4 Sensitive Information</h3>
        <p>We do <strong>not</strong> intentionally collect sensitive personal information such as racial or ethnic origin, political opinions, religious beliefs, health data, sexual orientation, genetic data, or biometric data. If you voluntarily include such information in journal entries, photos, or other Content, you do so at your own discretion.</p>

        <h2>2. Legal Bases for Processing (GDPR)</h2>
        <p>For users in the European Economic Area (EEA), United Kingdom, and Switzerland, we process your personal data under the following legal bases:</p>
        <table className="text-sm">
          <thead>
            <tr><th>Processing Activity</th><th>Legal Basis</th></tr>
          </thead>
          <tbody>
            <tr><td>Providing the Service, processing sensor data, storing Content</td><td>Performance of contract (Art. 6(1)(b) GDPR)</td></tr>
            <tr><td>Processing payments, tax compliance</td><td>Performance of contract &amp; legal obligation (Art. 6(1)(b), (c))</td></tr>
            <tr><td>Security monitoring, fraud prevention, rate limiting</td><td>Legitimate interest (Art. 6(1)(f)) — security of Service</td></tr>
            <tr><td>Product improvement via anonymized analytics</td><td>Legitimate interest (Art. 6(1)(f)) — improving the Service</td></tr>
            <tr><td>Sending transactional emails (alerts, receipts, security notices)</td><td>Performance of contract (Art. 6(1)(b))</td></tr>
            <tr><td>Sending optional product updates or newsletters</td><td>Consent (Art. 6(1)(a)) — opt-in only</td></tr>
            <tr><td>AI analysis of photos and grow data</td><td>Performance of contract (Art. 6(1)(b)) — you request analysis</td></tr>
            <tr><td>Responding to legal requests, law enforcement</td><td>Legal obligation (Art. 6(1)(c))</td></tr>
            <tr><td>Retaining billing records</td><td>Legal obligation (Art. 6(1)(c)) — tax law</td></tr>
          </tbody>
        </table>

        <h2>3. How We Use Your Information</h2>
        <p>We use collected information for the following purposes:</p>
        <ul>
          <li><strong>Service Delivery:</strong> Store, process, display, and transmit your grow data; process sensor readings; execute automations; deliver alerts and notifications;</li>
          <li><strong>AI Features:</strong> Provide AI-powered grow recommendations, plant health analysis, and insights based on your data (only when you actively use AI features);</li>
          <li><strong>Billing &amp; Payments:</strong> Process subscriptions, calculate usage, collect taxes, issue invoices and receipts via Stripe;</li>
          <li><strong>Communication:</strong> Send transactional messages (account verification, password resets, billing receipts, security alerts, threshold notifications);</li>
          <li><strong>Security &amp; Integrity:</strong> Detect and prevent fraud, abuse, unauthorized access, and DDoS attacks; enforce rate limits; maintain audit logs;</li>
          <li><strong>Debugging &amp; Support:</strong> Diagnose and fix technical issues, respond to support requests;</li>
          <li><strong>Product Improvement:</strong> Analyze anonymized, aggregated usage patterns to improve features, performance, and reliability;</li>
          <li><strong>Legal Compliance:</strong> Comply with applicable laws, regulations, legal processes, and governmental requests;</li>
          <li><strong>Safety:</strong> Protect the rights, property, or safety of our users, the public, or ourselves.</li>
        </ul>

        <h2>4. What We Do NOT Do</h2>
        <p>We make the following commitments regarding your data:</p>
        <ul>
          <li>We do <strong>NOT</strong> sell, rent, lease, or trade your personal information to any third party for monetary or other valuable consideration;</li>
          <li>We do <strong>NOT</strong> share your personal information for cross-context behavioral advertising;</li>
          <li>We do <strong>NOT</strong> use your grow data, sensor readings, photos, or journal entries for advertising or marketing purposes;</li>
          <li>We do <strong>NOT</strong> share identifiable data with other tenants or users (multi-tenant isolation is enforced via PostgreSQL Row Level Security);</li>
          <li>We do <strong>NOT</strong> train AI/ML models on your private data without your explicit, informed, opt-in consent;</li>
          <li>We do <strong>NOT</strong> use tracking pixels, advertising beacons, or third-party analytics cookies;</li>
          <li>We do <strong>NOT</strong> fingerprint your browser or device for tracking purposes;</li>
          <li>We do <strong>NOT</strong> build behavioral profiles of you for sale to data brokers;</li>
          <li>We do <strong>NOT</strong> monetize your data in any way other than providing the Service to you.</li>
        </ul>

        <h2>5. Disclosure of Information</h2>
        <p>We may disclose your information only in the following limited circumstances:</p>

        <h3>5.1 Service Providers (Data Processors)</h3>
        <p>We share data with third-party service providers who process it on our behalf under written data processing agreements:</p>
        <table className="text-sm">
          <thead>
            <tr><th>Provider</th><th>Purpose</th><th>Data Shared</th><th>Location</th></tr>
          </thead>
          <tbody>
            <tr><td>Stripe, Inc.</td><td>Payment processing, billing, tax calculation</td><td>Email, name, billing address, payment method tokens</td><td>United States</td></tr>
            <tr><td>Google LLC (Gemini AI)</td><td>AI plant health analysis</td><td>Plant photos submitted for analysis (ephemeral — not retained by Google per our DPA)</td><td>United States</td></tr>
            <tr><td>Resend</td><td>Transactional email delivery</td><td>Email address, notification content</td><td>United States</td></tr>
            <tr><td>OpenWeather Ltd.</td><td>Weather data retrieval</td><td>Geographic coordinates (if you configure outdoor grows)</td><td>United Kingdom</td></tr>
            <tr><td>Open-Meteo</td><td>Weather data (free baseline)</td><td>Geographic coordinates</td><td>Germany</td></tr>
            <tr><td>Infrastructure provider (Kubernetes)</td><td>Hosting, compute, storage</td><td>All Service data (encrypted at rest and in transit)</td><td>United States</td></tr>
          </tbody>
        </table>
        <p>All service providers are contractually bound to process data only as instructed by us and to implement appropriate security measures.</p>

        <h3>5.2 Legal Requirements</h3>
        <p>We may disclose your information if required to do so by law or if we believe in good faith that disclosure is necessary to:</p>
        <ul>
          <li>Comply with a legal obligation, court order, subpoena, or valid legal process;</li>
          <li>Protect and defend our rights, property, or safety;</li>
          <li>Protect the personal safety of users or the public;</li>
          <li>Prevent or investigate possible wrongdoing in connection with the Service;</li>
          <li>Cooperate with law enforcement investigations.</li>
        </ul>
        <p>Where legally permitted, we will attempt to notify you of such requests before disclosing your data.</p>

        <h3>5.3 Business Transfers</h3>
        <p>In the event of a merger, acquisition, reorganization, bankruptcy, asset sale, or similar business transaction, your information may be transferred as a business asset. We will notify you via email and/or prominent notice on the Service before your information becomes subject to a different privacy policy.</p>

        <h3>5.4 With Your Consent</h3>
        <p>We may share your information with third parties when you provide explicit consent to do so (e.g., connecting a third-party integration).</p>

        <h3>5.5 Aggregated/De-identified Data</h3>
        <p>We may share aggregated, anonymized, or de-identified data that cannot reasonably be used to identify you. Such data is not subject to this Privacy Policy.</p>

        <h2>6. Data Storage, Security, and Retention</h2>

        <h3>6.1 Storage Location</h3>
        <p>Your data is stored and processed in the <strong>United States</strong> on private Kubernetes clusters. We do not store data on shared/public cloud infrastructure.</p>

        <h3>6.2 Security Measures</h3>
        <p>We implement industry-standard technical and organizational security measures including:</p>
        <ul>
          <li><strong>Encryption in transit:</strong> All connections use TLS 1.3. No unencrypted connections are accepted.</li>
          <li><strong>Encryption at rest:</strong> Sensitive fields (API keys, integration secrets, payment credentials) are encrypted with AES-256-GCM.</li>
          <li><strong>Database isolation:</strong> Multi-tenant data isolation enforced at the database level via PostgreSQL Row Level Security (RLS).</li>
          <li><strong>Authentication security:</strong> Passwords hashed with bcrypt (cost factor 12). httpOnly, Secure, SameSite cookies. CSRF protection on all state-changing requests.</li>
          <li><strong>Access controls:</strong> Role-based access control (RBAC). Principle of least privilege for all internal systems.</li>
          <li><strong>Audit logging:</strong> All administrative actions and data access are logged with immutable audit trails.</li>
          <li><strong>Infrastructure security:</strong> Network policies, pod security standards, automated vulnerability scanning, regular security updates.</li>
          <li><strong>Incident response:</strong> Documented incident response procedures with defined notification timelines (see Section 6.5).</li>
        </ul>

        <h3>6.3 Data Retention Schedule</h3>
        <table className="text-sm">
          <thead>
            <tr><th>Data Type</th><th>Retention Period</th><th>Justification</th></tr>
          </thead>
          <tbody>
            <tr><td>Active account data</td><td>Life of account</td><td>Contract performance</td></tr>
            <tr><td>Sensor data (Free plan)</td><td>90 days</td><td>Plan limitation</td></tr>
            <tr><td>Sensor data (Paid plans)</td><td>Unlimited (life of account)</td><td>Contract performance</td></tr>
            <tr><td>API/access logs</td><td>30 days</td><td>Security, debugging</td></tr>
            <tr><td>Audit logs</td><td>7 years</td><td>Legal compliance, security</td></tr>
            <tr><td>Billing records</td><td>7 years after last transaction</td><td>Tax law (IRS, state requirements)</td></tr>
            <tr><td>Deleted account data</td><td>30 days (recovery) + 60 days (purge from backups)</td><td>Recovery window, then permanent deletion</td></tr>
            <tr><td>Support communications</td><td>3 years</td><td>Legitimate interest (dispute resolution)</td></tr>
            <tr><td>Anonymized analytics</td><td>Indefinite</td><td>Not personal data after de-identification</td></tr>
          </tbody>
        </table>

        <h3>6.4 Data Minimization</h3>
        <p>We collect only data that is necessary for the stated purposes. We periodically review our data collection practices and delete data that is no longer necessary.</p>

        <h3>6.5 Breach Notification</h3>
        <p>In the event of a data breach that poses a risk to your rights and freedoms:</p>
        <ul>
          <li>We will notify affected users via email within <strong>72 hours</strong> of confirming the breach (as required by GDPR Art. 33);</li>
          <li>We will notify the relevant supervisory authority within 72 hours where required;</li>
          <li>We will notify the California Attorney General if the breach affects more than 500 California residents;</li>
          <li>Notification will include: nature of the breach, categories of data affected, likely consequences, and measures taken or proposed.</li>
        </ul>

        {/* ===== SECTION 7-12: Rights, GDPR, CCPA ===== */}

        <h2>7. Your Privacy Rights</h2>
        <p>We provide the following rights to <strong>all users regardless of location</strong>. Additional jurisdiction-specific rights are detailed in subsequent sections.</p>

        <h3>7.1 Universal Rights</h3>
        <table className="text-sm">
          <thead>
            <tr><th>Right</th><th>Description</th><th>How to Exercise</th></tr>
          </thead>
          <tbody>
            <tr><td><strong>Access</strong></td><td>Obtain a copy of all personal data we hold about you</td><td>Account Settings → Export Data, or email privacy@tendrilgrow.com</td></tr>
            <tr><td><strong>Rectification</strong></td><td>Correct inaccurate or incomplete personal data</td><td>Edit your profile, or email us for data we cannot edit in-app</td></tr>
            <tr><td><strong>Deletion</strong></td><td>Request permanent deletion of your account and data</td><td>Account Settings → Delete Account, or email privacy@tendrilgrow.com</td></tr>
            <tr><td><strong>Portability</strong></td><td>Receive your data in a structured, machine-readable format (JSON)</td><td>Account Settings → Export Data, or via API</td></tr>
            <tr><td><strong>Restriction</strong></td><td>Request that we limit processing of your data</td><td>Email privacy@tendrilgrow.com</td></tr>
            <tr><td><strong>Objection</strong></td><td>Object to processing based on legitimate interests</td><td>Email privacy@tendrilgrow.com</td></tr>
            <tr><td><strong>Withdraw Consent</strong></td><td>Withdraw previously given consent at any time</td><td>Notification preferences, or email privacy@tendrilgrow.com</td></tr>
          </tbody>
        </table>

        <h3>7.2 Response Timeline</h3>
        <ul>
          <li>We will acknowledge your request within <strong>3 business days</strong>.</li>
          <li>We will fulfill verified requests within <strong>30 days</strong> (extendable to 45 days for complex requests with notice).</li>
          <li>We will not charge a fee for exercising your rights unless requests are manifestly unfounded or excessive.</li>
        </ul>

        <h3>7.3 Verification</h3>
        <p>To protect your privacy, we may need to verify your identity before fulfilling requests. Verification methods include confirming account ownership via email confirmation or providing account-specific details.</p>

        <h3>7.4 Non-Discrimination</h3>
        <p>We will not discriminate against you for exercising any of your privacy rights. You will not receive different pricing, a different quality of service, or be denied service for making privacy requests.</p>

        <h2>8. GDPR-Specific Provisions (EEA, UK, Switzerland)</h2>
        <p>If you are located in the European Economic Area, United Kingdom, or Switzerland, the following additional provisions apply:</p>

        <h3>8.1 Data Controller</h3>
        <p>Geek Info LLC is the data controller for your personal data. Contact: privacy@tendrilgrow.com.</p>

        <h3>8.2 Data Protection Officer</h3>
        <p>For GDPR-related inquiries, contact our designated privacy representative at: <a href="mailto:dpo@tendrilgrow.com" className="text-green-500">dpo@tendrilgrow.com</a></p>

        <h3>8.3 International Data Transfers</h3>
        <p>Your data is transferred to and processed in the United States. We rely on the following transfer mechanisms:</p>
        <ul>
          <li>EU-U.S. Data Privacy Framework (where applicable);</li>
          <li>Standard Contractual Clauses (SCCs) approved by the European Commission (Commission Implementing Decision (EU) 2021/914);</li>
          <li>Supplementary measures including encryption, access controls, and contractual commitments.</li>
        </ul>
        <p>You may request a copy of our Standard Contractual Clauses by emailing privacy@tendrilgrow.com.</p>

        <h3>8.4 Right to Lodge a Complaint</h3>
        <p>You have the right to lodge a complaint with your local data protection supervisory authority if you believe our processing of your personal data violates the GDPR.</p>

        <h3>8.5 Automated Decision-Making</h3>
        <p>We do not make decisions that produce legal or similarly significant effects based solely on automated processing. AI recommendations are informational only and do not result in automated decisions affecting your legal rights.</p>

        <h2>9. CCPA/CPRA-Specific Provisions (California Residents)</h2>
        <p>If you are a California resident, the following additional disclosures and rights apply under the California Consumer Privacy Act as amended by the California Privacy Rights Act (Cal. Civ. Code &sect; 1798.100 et seq.):</p>

        <h3>9.1 Categories of Personal Information Collected</h3>
        <p>In the preceding 12 months, we have collected the following categories of personal information as defined by the CCPA:</p>
        <table className="text-sm">
          <thead>
            <tr><th>CCPA Category</th><th>Examples</th><th>Collected?</th><th>Sold?</th><th>Shared for Cross-Context Behavioral Advertising?</th></tr>
          </thead>
          <tbody>
            <tr><td>A. Identifiers</td><td>Email, name, IP address, device IDs</td><td>Yes</td><td>No</td><td>No</td></tr>
            <tr><td>B. Personal information (Cal. Civ. Code &sect; 1798.80(e))</td><td>Name, address (billing only via Stripe)</td><td>Yes</td><td>No</td><td>No</td></tr>
            <tr><td>D. Commercial information</td><td>Subscription history, transaction records</td><td>Yes</td><td>No</td><td>No</td></tr>
            <tr><td>F. Internet/network activity</td><td>Browsing history on Service, API logs</td><td>Yes</td><td>No</td><td>No</td></tr>
            <tr><td>G. Geolocation data</td><td>Approximate location (if outdoor grows configured)</td><td>Yes (optional)</td><td>No</td><td>No</td></tr>
            <tr><td>H. Sensory data</td><td>Photos uploaded for AI analysis</td><td>Yes</td><td>No</td><td>No</td></tr>
            <tr><td>K. Inferences</td><td>AI-generated grow recommendations</td><td>Yes</td><td>No</td><td>No</td></tr>
          </tbody>
        </table>

        <h3>9.2 Sale and Sharing</h3>
        <p><strong>We do NOT sell your personal information.</strong> We have not sold personal information in the preceding 12 months. We do NOT share personal information for cross-context behavioral advertising.</p>

        <h3>9.3 California-Specific Rights</h3>
        <ul>
          <li><strong>Right to Know:</strong> You may request disclosure of the categories and specific pieces of personal information we have collected, the purposes, and the third parties with whom we share it.</li>
          <li><strong>Right to Delete:</strong> You may request deletion of your personal information, subject to legal exceptions.</li>
          <li><strong>Right to Correct:</strong> You may request correction of inaccurate personal information.</li>
          <li><strong>Right to Opt-Out of Sale/Sharing:</strong> Not applicable — we do not sell or share your data. However, we honor Global Privacy Control (GPC) signals.</li>
          <li><strong>Right to Limit Use of Sensitive Personal Information:</strong> We do not use sensitive personal information for purposes beyond what is necessary to provide the Service.</li>
          <li><strong>Right to Non-Discrimination:</strong> We will not discriminate against you for exercising CCPA rights.</li>
        </ul>

        <h3>9.4 Authorized Agents</h3>
        <p>You may designate an authorized agent to submit requests on your behalf. We require written authorization and may verify your identity directly.</p>

        <h3>9.5 &ldquo;Do Not Sell or Share My Personal Information&rdquo;</h3>
        <p>We do not sell or share personal information. We honor GPC browser signals as a valid opt-out mechanism. No &ldquo;Do Not Sell&rdquo; link is required because we do not engage in selling or sharing.</p>

        <h3>9.6 Financial Incentives</h3>
        <p>We do not offer financial incentives for the collection, sale, or deletion of personal information.</p>

        <h2>10. Additional U.S. State Privacy Rights</h2>

        <h3>10.1 New Jersey Data Privacy Act (NJDPA)</h3>
        <p>New Jersey residents have the right to: access, correct, delete, and obtain a portable copy of their personal data; opt out of targeted advertising, sale, and profiling. We do not engage in targeted advertising, sale, or profiling. To exercise rights, contact privacy@tendrilgrow.com. We will respond within 45 days.</p>

        <h3>10.2 Virginia (VCDPA), Colorado (CPA), Connecticut (CTDPA)</h3>
        <p>Residents of Virginia, Colorado, and Connecticut have similar rights including: access, correction, deletion, portability, and opt-out of targeted advertising/sale/profiling. We provide these rights universally. Appeals may be submitted to privacy@tendrilgrow.com and will be resolved within 60 days.</p>

        <h3>10.3 Appeal Process</h3>
        <p>If we decline a privacy request, you may appeal by emailing privacy@tendrilgrow.com with &ldquo;Privacy Appeal&rdquo; in the subject line. We will respond to appeals within the timeframes required by applicable law (typically 45-60 days). If unsatisfied, you may contact your state&rsquo;s Attorney General.</p>

        <h2>11. Cookies, Tracking, and Similar Technologies</h2>

        <h3>11.1 Cookies We Use</h3>
        <table className="text-sm">
          <thead>
            <tr><th>Cookie Name</th><th>Type</th><th>Purpose</th><th>Duration</th><th>Party</th></tr>
          </thead>
          <tbody>
            <tr><td>access_token</td><td>Strictly Necessary</td><td>Authentication session</td><td>15 minutes</td><td>First-party</td></tr>
            <tr><td>refresh_token</td><td>Strictly Necessary</td><td>Session renewal</td><td>7 days</td><td>First-party</td></tr>
            <tr><td>csrf_token</td><td>Strictly Necessary</td><td>CSRF protection</td><td>Session</td><td>First-party</td></tr>
            <tr><td>tos_accepted</td><td>Strictly Necessary</td><td>Record of Terms acceptance</td><td>Persistent</td><td>First-party</td></tr>
          </tbody>
        </table>

        <h3>11.2 What We Do NOT Use</h3>
        <ul>
          <li>No third-party analytics cookies (no Google Analytics, no Mixpanel, no Amplitude);</li>
          <li>No advertising cookies or pixels (no Meta Pixel, no Google Ads, no TikTok Pixel);</li>
          <li>No cross-site tracking technologies;</li>
          <li>No browser fingerprinting;</li>
          <li>No invisible tracking pixels in emails (we do not track email opens).</li>
        </ul>

        <h3>11.3 Do Not Track / Global Privacy Control</h3>
        <p>We honor the Global Privacy Control (GPC) signal. Since we do not engage in tracking, selling, or sharing personal data for advertising, the practical effect is already built into our architecture. We also respect Do Not Track (DNT) browser headers.</p>

        <h2>12. AI-Specific Privacy Disclosures</h2>

        <h3>12.1 How AI Processes Your Data</h3>
        <p>When you use AI features (grow assistant, plant health analysis), the following occurs:</p>
        <ul>
          <li>Your query, relevant sensor data, and/or photos are sent to the AI model provider (Google Gemini or local Ollama instance);</li>
          <li>For Google Gemini: data is processed under our API agreement which prohibits Google from using your data for model training;</li>
          <li>For local Ollama: data never leaves your server (self-hosted only);</li>
          <li>AI responses are generated and stored in your conversation history;</li>
          <li>We do NOT use your private conversations or data to train or fine-tune any AI model without explicit opt-in consent.</li>
        </ul>

        <h3>12.2 AI Data Retention</h3>
        <ul>
          <li>AI conversation history is retained as part of your account data;</li>
          <li>Photos sent to Google Gemini for analysis are processed ephemerally and not retained by Google;</li>
          <li>You may delete your AI conversation history at any time from the AI assistant interface.</li>
        </ul>

        <h3>12.3 Opting Out of AI Features</h3>
        <p>AI features are opt-in. You are never required to use AI features and can use the full Platform without engaging any AI functionality.</p>

        {/* ===== SECTION 13-18: Cookies, International, Contact ===== */}

        <h2>13. Children&rsquo;s Privacy</h2>
        <p>The Service is not directed to and is not intended for individuals under the age of eighteen (18). We do not knowingly collect personal information from children under 18. If we discover that we have collected personal information from a child under 18, we will promptly delete that information. If you believe a child has provided us with personal information, please contact privacy@tendrilgrow.com.</p>

        <h2>14. International Data Transfers</h2>
        <p>The Service is operated from and data is stored in the <strong>United States</strong>. If you access the Service from outside the United States, your data will be transferred to, stored in, and processed in the United States.</p>
        <p>For transfers from the EEA/UK, see Section 8.3. For all other international users, by using the Service you consent to such transfer and processing. We implement the following safeguards:</p>
        <ul>
          <li>Encryption of all data in transit (TLS 1.3) and sensitive data at rest (AES-256-GCM);</li>
          <li>Contractual data protection commitments with all service providers;</li>
          <li>Access controls limiting who can access personal data;</li>
          <li>Regular security assessments and penetration testing.</li>
        </ul>

        <h2>15. Third-Party Links and Integrations</h2>
        <p>The Service may contain links to third-party websites or integrate with third-party services. This Privacy Policy applies only to the Tendril Service. We are not responsible for the privacy practices of third-party websites or services. We encourage you to review the privacy policies of any third-party service you connect to the Platform.</p>

        <h2>16. Data Processing for Self-Hosted Instances</h2>
        <p>If you self-host Tendril using our open-source software:</p>
        <ul>
          <li>We do NOT receive, process, or store any data from your self-hosted instance;</li>
          <li>YOU are the data controller for all data in your self-hosted instance;</li>
          <li>You are solely responsible for your own privacy compliance, data security, backup, and breach notification;</li>
          <li>This Privacy Policy does not apply to self-hosted instances except where you voluntarily connect to our hosted services (e.g., telemetry opt-in, marketplace, or support channels).</li>
        </ul>

        <h2>17. Changes to This Privacy Policy</h2>
        <p>We may update this Privacy Policy periodically to reflect changes in our practices, legal requirements, or the Service. When we make changes:</p>
        <ul>
          <li><strong>Material changes:</strong> We will notify you via email and/or prominent in-app notification at least <strong>30 days</strong> before the effective date;</li>
          <li><strong>Non-material changes:</strong> We will update the &ldquo;Last Updated&rdquo; date at the top of this page;</li>
          <li>Your continued use of the Service after the effective date constitutes acceptance of the updated policy;</li>
          <li>If you do not agree to any update, your sole remedy is to delete your account before the effective date.</li>
        </ul>

        <h2>18. Contact Information</h2>
        <p>For all privacy-related questions, data requests, complaints, or concerns:</p>
        <table className="text-sm">
          <thead>
            <tr><th>Contact</th><th>Details</th></tr>
          </thead>
          <tbody>
            <tr><td>Privacy inquiries</td><td><a href="mailto:privacy@tendrilgrow.com" className="text-green-500">privacy@tendrilgrow.com</a></td></tr>
            <tr><td>Data Protection Officer (GDPR)</td><td><a href="mailto:dpo@tendrilgrow.com" className="text-green-500">dpo@tendrilgrow.com</a></td></tr>
            <tr><td>Legal inquiries</td><td><a href="mailto:legal@tendrilgrow.com" className="text-green-500">legal@tendrilgrow.com</a></td></tr>
            <tr><td>Entity</td><td>Geek Info LLC</td></tr>
            <tr><td>Management</td><td>Trec-Tor Consulting</td></tr>
            <tr><td>Jurisdiction</td><td>New Jersey, United States</td></tr>
          </tbody>
        </table>

        <p className="mt-8 text-sm text-neutral-500">For California residents: You may also contact the California Attorney General at <a href="https://oag.ca.gov/privacy" className="text-green-500" target="_blank" rel="noopener noreferrer">oag.ca.gov/privacy</a> if you believe your CCPA rights have been violated.</p>

        <div className="mt-12 border-t border-neutral-800 pt-6 text-sm text-neutral-500">
          <p>Powered by <a href="https://www.trector.com" target="_blank" rel="noopener noreferrer" className="hover:text-neutral-300">Trec-Tor Consulting</a></p>
        </div>
      </article>
    </div>
  );
}
