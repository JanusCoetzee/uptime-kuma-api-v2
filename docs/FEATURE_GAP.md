# Feature gap: uptime-kuma-api-v2 vs. current Uptime Kuma

Compared on 2026-10-19.

| Source | Version | Notes |
|---|---|---|
| Library | 1.0.3 | README claims support for Kuma 2.0.0-beta.2 |
| Latest stable Kuma | **2.5.6** (tag) | Baseline for this document |
| Kuma `master` | 3.0.0-beta.0 (`b092505`, 2026-10-14) | Breaking for this library, see section 1 |

**Method.** Static comparison of the server source (`server/server.js`, `server/socket-handlers/*`, `server/model/monitor.js`, `server/monitor-types/`, `server/notification-providers/`, `src/pages/EditMonitor.vue`, `src/mixins/socket.js`) against the events the library calls (`_call(...)`) and the handlers it registers. Event lists were extracted with `grep`, so handlers registered through variables (e.g. the `cloudflared` prefix) were checked by hand. Section 0 was verified against a live 2.5.6 server; everything else is static. Items marked **[verify]** need a live check before an agent acts on them.

## 0. Live verification (read-only, no login)

Probed `http://kuma.indlovu.local:3001` on 2026-10-19 with only unauthenticated requests: the public status page API, the Socket.IO handshake, and `needSetup`.

| Check | Result |
|---|---|
| Server reachable, Socket.IO handshake | Works |
| `needSetup` | `False` |
| Events sent before login | `info` (without `version`, matching the library's "drop first info event" workaround) and `loginRequired`. So auth is enabled and the server speaks the Socket.IO login protocol (2.x style, not the 3.0 `better-auth` flow) |
| `GET /api/status-page/homelab` keys | `config`, **`incidents`**, `maintenanceList`, `publicGroupList` |
| `config` keys | include `analyticsType`, `analyticsId`, `analyticsScriptUrl`, `autoRefreshInterval`, `rssTitle`, `showOnlyLastHeartbeat` (as the CHANGELOG describes) |

**New finding (confirmed live and in the 2.5.6 source):** the status page response uses `incidents`, a **list**, and no longer has `incident`. `get_status_page` reads `r2.get("incident")` ([api.py:2020](../uptime_kuma_api/api.py#L2020)), so incidents are silently never returned on 2.5.x. The CHANGELOG entry describing the "missing `incident` key" is actually a rename. The returned shape changes from one dict to a list, which is a public-API decision for the fix.

### 0.1 Authenticated read-only probe (same day)

Logged in over Socket.IO with credentials from the environment (nothing written). Only read events were observed; no monitor, setting or notification was added, edited or deleted.

| Check | Result |
|---|---|
| Server version | **2.5.6** (`latestVersion` reports 2.5.5), Docker, SQLite. The version only appears in the **second** `info` event; the first has no `version` |
| Login | Socket.IO `login` works, so the library's auth flow is valid on 2.5.6 |
| `monitorTypeList` event | Received, 26 types. Not handled by the library. Confirms section 3 |
| Types the server lists that the library lacks | dns excluded; missing: `manual`, `ntp`, `oracledb`, `pm2`, `rabbitmq`, `sftp`, `sip-options`, `smtp`, `snmp`, `system-service`, `websocket-upgrade`, `globalping` |
| Monitor model | 124 distinct keys across the 26 live monitors; 45 of them never appear as a string in `api.py` (list in section 3) |
| `getSettings` | Returned only `keepDataPeriodDays` and `serverTimezone` for this account **[verify]**: either the call needs a different payload or the library's expectation of a full settings dict is wrong |
| Notifications | 1 configured (ntfy) |

**Still unverified:** the delta-event behaviour in 1.1 (needs a write, e.g. create then delete a temporary monitor; not done without approval) and the `uploadBackup` question.

## 1. Critical: compatibility problems (not just missing features)

### 1.1 Monitor list deltas are ignored (stable 2.x) **[verify]**
In 2.5.6 `add`, `editMonitor`, `pauseMonitor`, `resumeMonitor`, `deleteMonitor` (and related paths in `server/server.js`) emit **`updateMonitorIntoList`** and **`deleteMonitorFromList`** instead of re-sending the full `monitorList`. The library registers neither handler (`grep` finds 0 occurrences in `api.py`); it only caches the initial `monitorList`.

Likely consequence: `get_monitors()` after `add_monitor` / `edit_monitor` / `delete_monitor` returns stale data, and `wait_for_event(Event.MONITOR_LIST)` (which only waits for the first event) hides it. This is directly relevant to the existing issue "make `wait_for_event` wait for a new event". The fix should handle the delta events in the cache, not only count events.

### 1.2 Authentication moves off Socket.IO in 3.0 (master)
In master the socket events `login`, `loginByToken`, `logout`, `setup`, `changePassword`, `twoFAStatus`, `prepare2FA`, `save2FA`, `disable2FA`, `verifyToken` are **gone**. Only `needSetup` remains, in `better-auth-socket-handler.ts`. Auth is handled by `better-auth` over HTTP (`server/routers/better-auth-router`), and the server emits a new `session` event. Every login-related method in the library (`login`, `login_by_token`, `logout`, `setup`, 2FA, `change_password`) fails against 3.0.
Decision needed: declare 3.0 unsupported for now, or design a login flow over HTTP (cookie/session or API key). API keys may be the most practical path since the `@better-auth/api-key` dependency is new. This needs investigation.

### 1.3 Library supports far fewer monitor types than the server
See section 3.

## 2. Socket.IO events: server vs. library

The library calls 64 distinct events. Stable 2.5.6 handles 86 `socket.on` events.

### 2.1 Client-to-server events not wrapped

| Event | What it does | Priority |
|---|---|---|
| `getIncidentHistory`, `editIncident`, `resolveIncident`, `deleteIncident` | Full incident lifecycle on status pages. The library only has `postIncident` and `unpinIncident` | High |
| `getMonitorChartData` | Chart data for a monitor and period | Medium |
| `monitorImportantHeartbeatListPaged`, `monitorImportantHeartbeatListCount` | Paged important heartbeats (the library only holds a capped cache) | Medium |
| `getPushExample` | Example push URL/command for a monitor | Low |
| `getPM2ProcessList` | Needed to configure the new PM2 monitor | Low |
| `checkDomain` | Domain expiry check (new domain-expiry feature) | Medium |
| `addRemoteBrowser`, `deleteRemoteBrowser`, `testRemoteBrowser` | Remote browser management. `real-browser` monitors can reference a `remote_browser` | Medium |
| `cloudflared` group: `join`, `leave`, `start`, `stop`, `removeToken` (prefix `cloudflared`) | Cloudflare tunnel management | Low |
| `disconnectOtherSocketClients` | Invalidate other sessions | Low (useful for security tooling) |
| `getWebpushVapidPublicKey` | Needed for the new `webpush` notification provider | Low |
| `getMonitorList`, `getMaintenanceList`, `getAPIKeyList` | Explicit refresh of lists. Currently the library only listens to pushes | Low |

### 2.2 Server-to-client events not handled

| Event | Impact |
|---|---|
| `updateMonitorIntoList`, `deleteMonitorFromList` | **Cache correctness** (see 1.1) |
| `monitorTypeList` | Server tells the client which monitor types it supports. Could drive dynamic validation instead of a hard-coded enum |
| `domainInfo` | Domain expiry data |
| `remoteBrowserList` | Remote browser inventory |
| `loginRequired`, `refresh`, `setup` | Session/lifecycle signals ignored |
| `cloudflared_*` (`installed`, `running`, `token`, `message`, `errorMessage`) | Tunnel state |
| `session` (master only) | New auth session event |

### 2.3 Library-only
`uploadBackup` is in the library but not in 2.5.6 or master (regex-based, **[verify]**). It may have been removed upstream; if so `upload_backup` is dead code on 2.x.

## 3. Monitor types

Library `MonitorType` (22): dns, docker, gamedig, group, grpc-keyword, http, json-query, kafka-producer, keyword, mongodb, mqtt, mysql, ping, port, postgres, push, radius, real-browser, redis, sqlserver, steam, tailscale-ping.

**Missing from the library (all present in 2.5.6 and master):**

| Type | New fields the server exposes (from `Monitor.toJSON`) |
|---|---|
| `manual` | none specific |
| `websocket-upgrade` | `wsSubprotocol`, `wsIgnoreSecWebsocketAcceptHeader` |
| `smtp` | `smtpSecurity` |
| `snmp` | `snmpOid`, `snmpVersion` and related |
| `ntp` | `ntpTimeOffsetThreshold`, `ntpStratumThreshold`, `ntpRootDispersionThreshold` |
| `rabbitmq` | `rabbitmqNodes` |
| `sftp` | `sftpPath`, `sshAuthMethod` |
| `oracledb` | uses the shared database fields |
| `pm2` | process name |
| `system-service` | `system_service_name` |
| `sip-options` | host/port |
| `globalping` | `subtype`, `protocol`, `location`, `ipFamily`, ping options |

The enum also needs: `MonitorType` in `monitor_type.py` (generated), `required_args_by_type` and `_build_monitor_data` in `api.py`, and the shared parameter docstring in `docstrings.py`. Until these are added, `_check_arguments_monitor` raises `KeyError` for any new type (existing bug story).

**Monitor fields in the server model that the library does not send** (89 keys in `toJSON`, those not in `_build_monitor_data`):
`domainExpiryNotification`, `expectedTlsAlert`, `ipFamily`, `jsonPathOperator`, `mqttCheckType`, `ping_count`, `ping_numeric`, `ping_per_request_timeout`, `responseMaxLength`, `retryOnlyOnStatusCodeFailure`, `saveErrorResponse`, `saveResponse`, `screenshot_delay`, `remote_browser`, plus all the per-type fields above. Read-only fields the server returns (`id`, `active`, `tags`, `maintenance`, `childrenIDs`, `validCert`, `certExpiryDaysRemaining`, `dns_last_result`, `weight`, `forceInactive`, `cacheBust`) are not gaps.
**Live-confirmed additions** (present in the real server's monitor objects, absent from `api.py`): `bearer_token`, `oauth_audience`, `gamedigToken`, `includeSensitiveData`, `mqttWebsocketPath`, `location`, `subtype`, `screenshot`, `rabbitmqUsername`, `rabbitmqPassword`, `sshUsername`, `sshPassword`, `sshPrivateKey`, `sshPassphrase`, `path`, `pathName`, and the `ntp*`, `snmp*`, `smtpSecurity`, `ws*`, `sftpPath`, `system_service_name`, `rabbitmqNodes` fields listed above. Several of these are secrets (`sshPassword`, `sshPrivateKey`, `rabbitmqPassword`, `bearer_token`); they should be redacted in logs and `repr` (see the security epic).
Note the existing `conditions` argument is accepted but undocumented in the validators.

## 4. Notification providers

The server has about 108 provider classes (109 files minus the base class) in 2.5.6. The library enum has 53 members.

Not in the library (name-normalised comparison, so a few may be false positives; `rocket.chat` was checked and is present): 360messenger, 46elks, amootsms, bale, bearsms, bitrix24, brevo, callmebot, cellsynt, clickup, egosms, evolution, flowtriq, fluxer, googlesheets, grafanaoncall, gtxmessaging, halopsa, heiioncall, jiraservicemanagement, keep, max, milky, nextcloudtalk, notifery, notifyapp, onechat, onesender, ooredoo, openwa, pinglet, plivo, pumble, pushplus, resend, sendgrid, sevenio, signalgrid, signl4, smsgateway, smsir, smspartner, smsplanet, spugpush, techuluspush, telnyx, teltonika, threema, turbosmtp, vk, vkteams, waha, webpush, whapi, wpush, wxpusher, yzj.

In the library but not in 2.5.6: `linenotify`, `pushbytechulus`. These look removed or renamed upstream, so existing users of them need a deprecation path.

Fix = regenerate `notification_providers.py` with `scripts/build_notifications.py` against the 2.5.6 checkout (see the generated-code story). The script scrapes Vue components and will probably need updating for 2.x.

## 5. Settings

`set_settings` / `get_settings` lack the following keys that the 2.5.6 UI exposes:
- `domainExpiryNotifyDays` (domain expiry feature)
- `globalpingApiToken` (globalping monitor)

`checkBeta`, `checkUpdate`, `chromeExecutable`, `disableAuth`, `entryPage`, `keepDataPeriodDays`, `nscd`, `primaryBaseURL`, `searchEngineIndex`, `serverTimezone`, `steamAPIKey`, `tlsExpiryNotifyDays`, `trustProxy` are covered. `dnsCache` is sent by the library but I did not find it in the settings UI **[verify]**.

## 6. Status pages

Missing: incident edit/resolve/delete/history (section 2.1). `get_status_page` / `save_status_page` already round-trip unknown config keys, so new config fields (`analyticsType`, `autoRefreshInterval`, `rssTitle`, ...) work implicitly but are undocumented and unvalidated.

## 7. Suggested prioritisation

1. **Correctness first:** delta events (1.1). Everything else builds on a trustworthy cache.
2. **Decide the support policy:** stable 2.5.x yes; 3.0 beta no until the auth story is solved (1.2).
3. **Regenerate** `MonitorType` and `NotificationType` from 2.5.6, then add the new monitor types in small PRs, one per type, with unit tests for required args.
4. **Incident lifecycle** and **settings** keys: small, high value.
5. Remote browsers, chart data, paged heartbeats, domain expiry.
6. Cloudflared, PM2 list, session management: low priority.
7. **3.0 auth** (1.2): spike first.

## 8. Not covered

Per-field validation rules for each new type (server-side constraints), notification provider field schemas, rate limiting and error messages, and runtime behaviour. A live comparison against a 2.5.6 container (listing `getMonitorList` JSON for each type) is the best next verification step.
