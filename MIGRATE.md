# Migrate to the Wingify Python FME SDK

This guide explains how to adopt the **Wingify** public API on the Python FME SDK. Existing **VWO** integrations (`vwo-fme-python-sdk`) continue to work without changes.

For installation, requirements, and advanced configuration (storage, logger, gateway, proxy, polling, and more), see [README.md](README.md).

---

## Overview

The FME SDK is published as **two PyPI packages** built from the **same codebase** at the same version:

| PyPI package | Import | Public types |
| --- | --- | --- |
| [`wingify-fme-python-sdk`](https://pypi.org/project/wingify-fme-python-sdk/) | `import wingify` | `WingifyOptionsModel`, `WingifyClient`, … |
| [`vwo-fme-python-sdk`](https://pypi.org/project/vwo-fme-python-sdk/) | `import vwo` | `VWOOptionsModel`, `VWOClient`, … (legacy) |

Pick **one** package for your app — do **not** install both `vwo-fme-python-sdk` and `wingify-fme-python-sdk` in the same environment.

New integrations should use the **Wingify** package and types. When you install and initialize through `wingify-fme-python-sdk`, the SDK uses Wingify edge/collect endpoints and Wingify-branded logging (see [Runtime behavior](#runtime-behavior-wingify-build) below).

---

## Wingify API — implementation guide

Use PyPI package `wingify-fme-python-sdk`. Public types use the `Wingify*` prefix.

Legacy `VWO*` types on `vwo-fme-python-sdk` remain supported; they are thin aliases over the same core implementation.

### Implementation steps

1. **Add the dependency** — use only the Wingify coordinate (same semver you use on VWO today):

   ```bash
   pip install wingify-fme-python-sdk
   ```

2. **Initialize** — call `init()` with `account_id` and `sdk_key`. Returns a `WingifyClient`.

3. **Build user context** — pass a plain dict with at least `id` (string). Optional: `custom_variables`, `user_agent`, `ip_address`, `bucketingSeed`, etc. See [README.md](README.md).

4. **Evaluate flags** — `client.get_flag(feature_key, context)`.

5. **Track and attribute** — `track_event`, `set_attribute`, and `set_alias` on the initialized client.

### Python

```python
from wingify import init

client = init({
    'account_id': '123456',
    'sdk_key': '32-alpha-numeric-sdk-key',
    'logger': {'level': 'DEBUG'},
})

context = {'id': 'unique_user_id', 'custom_variables': {'plan': 'pro'}}

flag = client.get_flag('feature_key', context)

if flag.is_enabled():
    variable = flag.get_variable('feature_variable', 'default-value')
    print('Variable:', variable)

client.track_event('event_name', context, {'cartValue': 10})
client.set_attribute('attribute_key', 'attribute_value', context)
client.set_alias(context, 'alias_id')
```

### Type hints (Wingify package)

```python
from wingify import init, WingifyClient, WingifyOptionsModel

options: WingifyOptionsModel = WingifyOptionsModel({
    'accountId': '123456',
    'sdkKey': '32-alpha-numeric-sdk-key',
})

client: WingifyClient = init({
    'account_id': '123456',
    'sdk_key': '32-alpha-numeric-sdk-key',
})
```

For the legacy VWO package, substitute `VWOClient` and `VWOOptionsModel` — behavior is the same.

---

## Public API mapping

| Legacy (VWO package) | Wingify package |
| --- | --- |
| `init` | `init` |
| `getUUID` | `getUUID` |
| `VWOOptionsModel` | `WingifyOptionsModel` |
| `VWOClient` | `WingifyClient` |
| `vwoBuilder` on options | `wingifyBuilder` (preferred); `vwoBuilder` still accepted |
| `StorageConnector`, `LogLevelEnum` | Same export names |

### Options that stay VWO-named (platform compatibility)

| Option / field | Notes |
| --- | --- |
| `_vwo_meta` | Still supported; use for SDK metadata when needed |
| Context `_vwo` | Still supported for UA / device hints; `_wingify` also accepted |
| Event / payload keys (e.g. `_vwo_meta` in network payloads) | Unchanged for server compatibility |
| `vwoBuilder` | Alias of `wingifyBuilder` on init options |
| Local storage key | `vwo_fme_settings` for both brands |

---

## Legacy VWO API

The following remain available for existing apps on **`vwo-fme-python-sdk`**:

- `import vwo` with `init`, `getUUID`
- `VWOClient`, `VWOBuilder`, `VWOOptionsModel`
- `vwoBuilder`, `StorageConnector`, logger hooks
- VWO build-time hosts and `VWO-SDK` log prefix

No breaking change is required to stay on the VWO package.

---

## Runtime behavior (Wingify build)

When you install and run the **Wingify** PyPI build (not `vwo-fme-python-sdk`):

| Area | Wingify build | VWO build (legacy package) |
| --- | --- | --- |
| Settings / pull / location | `edge.wingify.net` | `dev.visualwebsiteoptimizer.com` |
| Events / batch | `collect.wingify.net` | Same host as settings (single host) |
| Log prefix | `Wingify-SDK` | `VWO-SDK` |
| Log message branding | Wingify where templated | VWO |
| PyPI `name` in metadata | `wingify-fme-python-sdk` | `vwo-fme-python-sdk` |

With **`proxy_url`**, all requests go to your proxy host. Without `proxy_url`, the SDK selects hosts automatically per build brand.

Event and API payload field names (for example `_vwo_meta`, `vwo_*` event names) are **unchanged** for compatibility with the FME platform.

---

## Migrating from `vwo-fme-python-sdk` to `wingify-fme-python-sdk`

1. In `requirements.txt`, replace the dependency:

   ```diff
   - vwo-fme-python-sdk==1.50.0
   + wingify-fme-python-sdk==1.50.0
   ```

2. Update imports:

   ```diff
   - from vwo import init
   + from wingify import init
   ```

3. Rename types: `VWOClient` → `WingifyClient`, `VWOOptionsModel` → `WingifyOptionsModel`.

4. If you pass a custom builder, prefer `wingifyBuilder` instead of `vwoBuilder` (either still works).

5. Reinstall and run your existing tests — flag evaluation, tracking, and attributes behave the same; only package name, exported type names, default hosts, and log branding change.

### What you do **not** need to change

- `account_id`, `sdk_key`, feature keys, event names
- User context shape (`{'id': '...'}` and optional fields)
- Method signatures on the client (`get_flag`, `track_event`, etc.)
- Server-side campaign / settings JSON
- `_vwo` / `_vwo_meta` in context or payloads when you already send them

---

## Architecture note

The SDK follows a **Single Repo Two Pacakge Approach**:

| Package | Role |
| --- | --- |
| `wingify/` | **Core** — `api/`, `constants/`, `enums/`, `services/`, `utils/`, `packages/`, `wingify_client.py`, … |
| `vwo/` | **Legacy facade only** (~10 files) — `init`, `VWOClient`, `VWOBuilder`, `VWOOptionsModel`, `StorageConnector`, `LogLevelEnum`, etc. |

Both PyPI wheels ship `wingify` (core) and `vwo` (facade). Existing apps use `import vwo`; new apps use `import wingify`. Brand-specific hosts, SDK name, and log prefix are selected at **runtime** via `is_via_vwo` (`vwo.init()` sets it to `true`; `wingify.init()` defaults to `false`). PyPI wheel metadata still differs per `SDK_BRAND` at build time.

---

## Related documents

| Document | Content |
| --- | --- |
| [README.md](README.md) | Installation, requirements, configuration |
| [CHANGELOG.md](CHANGELOG.md) | Version history and rebranding notes |
