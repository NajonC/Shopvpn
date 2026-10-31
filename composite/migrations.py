"""Versioned, additive schema migrations for the composite tables.

The operator must stop every writer of the set before calling ``migrate``. FSM
files are copied but never changed, and each database member changes in its own
explicit transaction.
"""

from dataclasses import dataclass
import os
import sqlite3
import time
from typing import Callable
import urllib.parse

from composite.repository import BUSY_TIMEOUT_S


SCHEMA_VERSION = 1
KIND_TABLES = ("products", "test_config_plans", "orders")

# data-model.md §1: physical panels, aliases and prepared bindings. A panel
# with restartXrayOnClientDisable on or unreadable blocks new binding (RX-D2).
_PANEL_DDL = (
    """CREATE TABLE composite_physical_panels (
    physical_panel_id TEXT PRIMARY KEY,
    provider TEXT NOT NULL CHECK (provider = '3xui'),
    authority_fingerprint TEXT NOT NULL,
    endpoint_ref TEXT NOT NULL,
    tls_trust_ref TEXT NOT NULL,
    panel_version TEXT,
    core_version TEXT,
    capability_manifest_revision TEXT,
    route_namespace_version INTEGER,
    restart_xray_on_client_disable TEXT
        CHECK (restart_xray_on_client_disable IN ('off', 'on', 'unreadable')),
    restart_xray_on_client_disable_checked_at INTEGER,
    write_stall_misses INTEGER NOT NULL DEFAULT 0
        CHECK (typeof(write_stall_misses) = 'integer' AND write_stall_misses >= 0),
    write_stall_escalation_ref TEXT,
    CHECK ((restart_xray_on_client_disable IS NULL) = (restart_xray_on_client_disable_checked_at IS NULL))
)""",
    """CREATE TABLE composite_panel_aliases (
    alias_id TEXT PRIMARY KEY,
    physical_panel_id TEXT NOT NULL
        REFERENCES composite_physical_panels (physical_panel_id) ON DELETE RESTRICT,
    database_installation_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    local_panel_server_id INTEGER NOT NULL,
    UNIQUE (database_installation_id, tenant_id, local_panel_server_id)
)""",
    """CREATE TABLE composite_prepared_bindings (
    binding_id TEXT PRIMARY KEY,
    physical_panel_id TEXT NOT NULL
        REFERENCES composite_physical_panels (physical_panel_id) ON DELETE RESTRICT,
    inbound_id INTEGER NOT NULL,
    settings_fingerprint TEXT NOT NULL,
    egress_key TEXT NOT NULL,
    route_namespace TEXT NOT NULL
)""",
)

# data-model.md §2-§4: plans and versions, plan nodes, immutable offers,
# subscriptions with their current descriptor per logical node, URL tokens
# and config generations. Paid versions last exactly 2,592,000 seconds at a
# positive base price; test and campaign versions last whole hours.
_CATALOG_DDL = (
    """CREATE TABLE composite_plans (
    plan_id TEXT PRIMARY KEY,
    kind TEXT NOT NULL CHECK (kind IN ('paid', 'test', 'campaign')),
    UNIQUE (plan_id, kind)
)""",
    """CREATE TABLE composite_plan_versions (
    plan_version_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    version INTEGER NOT NULL,
    allowance_bytes INTEGER NOT NULL
        CHECK (typeof(allowance_bytes) = 'integer' AND allowance_bytes > 0),
    duration_seconds INTEGER NOT NULL
        CHECK (typeof(duration_seconds) = 'integer' AND duration_seconds > 0),
    base_price INTEGER NOT NULL
        CHECK (typeof(base_price) = 'integer' AND base_price >= 0),
    CHECK (CASE kind
        WHEN 'paid' THEN base_price > 0 AND duration_seconds = 2592000
        ELSE duration_seconds % 3600 = 0 END),
    UNIQUE (plan_id, version),
    FOREIGN KEY (plan_id, kind) REFERENCES composite_plans (plan_id, kind) ON DELETE RESTRICT
)""",
    """CREATE TABLE composite_plan_nodes (
    plan_node_id TEXT PRIMARY KEY,
    plan_version_id TEXT NOT NULL
        REFERENCES composite_plan_versions (plan_version_id) ON DELETE RESTRICT,
    ordinal INTEGER NOT NULL,
    logical_node_key TEXT NOT NULL,
    binding_id TEXT NOT NULL
        REFERENCES composite_prepared_bindings (binding_id) ON DELETE RESTRICT,
    protocol TEXT NOT NULL CHECK (protocol IN ('vless', 'vmess', 'trojan')),
    transport TEXT NOT NULL,
    security TEXT NOT NULL,
    descriptor TEXT NOT NULL,
    owner_pick TEXT,
    remark TEXT,
    egress TEXT,
    UNIQUE (plan_version_id, ordinal),
    UNIQUE (plan_version_id, logical_node_key)
)""",
    """CREATE TRIGGER composite_plan_nodes_version_fixed
    BEFORE UPDATE OF plan_version_id ON composite_plan_nodes
    WHEN NEW.plan_version_id IS NOT OLD.plan_version_id
    BEGIN SELECT RAISE(ABORT, 'plan node version is immutable'); END""",
    """CREATE TABLE composite_offers (
    offer_id TEXT PRIMARY KEY,
    plan_version_id TEXT NOT NULL
        REFERENCES composite_plan_versions (plan_version_id) ON DELETE RESTRICT,
    allowance_bytes INTEGER NOT NULL
        CHECK (typeof(allowance_bytes) = 'integer' AND allowance_bytes > 0),
    duration_seconds INTEGER NOT NULL
        CHECK (typeof(duration_seconds) = 'integer' AND duration_seconds > 0),
    base_price INTEGER NOT NULL
        CHECK (typeof(base_price) = 'integer' AND base_price >= 0),
    payable_price INTEGER NOT NULL
        CHECK (typeof(payable_price) = 'integer' AND payable_price >= 0 AND payable_price <= base_price),
    accepted_by TEXT NOT NULL,
    accepted_at INTEGER NOT NULL
)""",
    """CREATE TRIGGER composite_offers_no_update BEFORE UPDATE ON composite_offers
    BEGIN SELECT RAISE(ABORT, 'offers are immutable'); END""",
    """CREATE TRIGGER composite_offers_no_delete BEFORE DELETE ON composite_offers
    BEGIN SELECT RAISE(ABORT, 'offers are immutable'); END""",
    """CREATE TABLE composite_offer_nodes (
    offer_node_id TEXT PRIMARY KEY,
    offer_id TEXT NOT NULL REFERENCES composite_offers (offer_id) ON DELETE RESTRICT,
    ordinal INTEGER NOT NULL,
    logical_node_key TEXT NOT NULL,
    binding_id TEXT NOT NULL
        REFERENCES composite_prepared_bindings (binding_id) ON DELETE RESTRICT,
    protocol TEXT NOT NULL CHECK (protocol IN ('vless', 'vmess', 'trojan')),
    transport TEXT NOT NULL,
    security TEXT NOT NULL,
    descriptor TEXT NOT NULL,
    owner_pick TEXT,
    egress TEXT,
    UNIQUE (offer_id, ordinal),
    UNIQUE (offer_id, logical_node_key)
)""",
    """CREATE TRIGGER composite_offer_nodes_no_update BEFORE UPDATE ON composite_offer_nodes
    BEGIN SELECT RAISE(ABORT, 'offer nodes are immutable'); END""",
    """CREATE TRIGGER composite_offer_nodes_no_delete BEFORE DELETE ON composite_offer_nodes
    BEGIN SELECT RAISE(ABORT, 'offer nodes are immutable'); END""",
    """CREATE TABLE composite_subscriptions (
    subscription_id TEXT PRIMARY KEY,
    tenant_installation_id TEXT NOT NULL,
    customer_telegram_id INTEGER NOT NULL,
    offer_id TEXT NOT NULL REFERENCES composite_offers (offer_id) ON DELETE RESTRICT,
    kind TEXT NOT NULL CHECK (kind IN ('paid', 'test')),
    lifecycle TEXT NOT NULL
        CHECK (lifecycle IN ('preparing', 'fulfilled', 'cancel_pending', 'cancelled', 'failed_unfulfilled')),
    available_at INTEGER,
    expires_at INTEGER,
    customer_disabled INTEGER NOT NULL DEFAULT 0 CHECK (customer_disabled IN (0, 1)),
    owner_suspended INTEGER NOT NULL DEFAULT 0 CHECK (owner_suspended IN (0, 1)),
    reporting_suspended INTEGER NOT NULL DEFAULT 0 CHECK (reporting_suspended IN (0, 1)),
    recovery_hold_case TEXT,
    replacement_delivery_block INTEGER NOT NULL DEFAULT 0 CHECK (replacement_delivery_block IN (0, 1)),
    initial_delivery_block INTEGER NOT NULL DEFAULT 0 CHECK (initial_delivery_block IN (0, 1)),
    cancel_accepted_at INTEGER,
    cancel_wait_kind TEXT CHECK (cancel_wait_kind IN ('authorized_renewal', 'initial_provisioning')),
    cancel_final_started_at INTEGER,
    CHECK (cancel_wait_kind IS NULL OR cancel_accepted_at IS NOT NULL),
    CHECK (cancel_final_started_at IS NULL
        OR (cancel_accepted_at IS NOT NULL AND cancel_final_started_at >= cancel_accepted_at))
)""",
    """CREATE TRIGGER composite_subscriptions_owner_fixed
    BEFORE UPDATE OF tenant_installation_id, customer_telegram_id ON composite_subscriptions
    WHEN NEW.tenant_installation_id IS NOT OLD.tenant_installation_id
        OR NEW.customer_telegram_id IS NOT OLD.customer_telegram_id
    BEGIN SELECT RAISE(ABORT, 'subscription tenant and customer are immutable'); END""",
    # The current descriptor per logical node: the offer node's at sale, replaced
    # when that subscription's move publishes, unchanged by renewal (RD05-OWN-002).
    """CREATE TABLE composite_subscription_nodes (
    subscription_id TEXT NOT NULL
        REFERENCES composite_subscriptions (subscription_id) ON DELETE RESTRICT,
    logical_node_key TEXT NOT NULL,
    descriptor TEXT NOT NULL,
    PRIMARY KEY (subscription_id, logical_node_key)
)""",
    """CREATE TABLE composite_tokens (
    token_id TEXT PRIMARY KEY,
    subscription_id TEXT NOT NULL
        REFERENCES composite_subscriptions (subscription_id) ON DELETE RESTRICT,
    token_generation INTEGER NOT NULL,
    token_digest BLOB NOT NULL UNIQUE
        CHECK (typeof(token_digest) = 'blob' AND length(token_digest) = 32),
    encrypted_token BLOB,
    status TEXT NOT NULL CHECK (status IN ('candidate', 'current', 'revoked', 'superseded'))
)""",
    "CREATE UNIQUE INDEX composite_tokens_one_current ON composite_tokens (subscription_id) WHERE status = 'current'",
    """CREATE TRIGGER composite_tokens_no_delete BEFORE DELETE ON composite_tokens
    BEGIN SELECT RAISE(ABORT, 'token tombstones are kept'); END""",
    """CREATE TRIGGER composite_tokens_digest_fixed BEFORE UPDATE OF token_digest ON composite_tokens
    WHEN NEW.token_digest IS NOT OLD.token_digest
    BEGIN SELECT RAISE(ABORT, 'token digest is immutable'); END""",
    """CREATE TRIGGER composite_tokens_no_revival BEFORE UPDATE OF status ON composite_tokens
    WHEN OLD.status IN ('revoked', 'superseded') AND NEW.status = 'current'
    BEGIN SELECT RAISE(ABORT, 'a revoked or superseded token never returns'); END""",
    """CREATE TABLE composite_config_generations (
    generation_id TEXT PRIMARY KEY,
    subscription_id TEXT NOT NULL
        REFERENCES composite_subscriptions (subscription_id) ON DELETE RESTRICT,
    generation INTEGER NOT NULL,
    state TEXT NOT NULL
        CHECK (state IN ('preparing', 'complete_verified', 'published', 'retired', 'blocked_uncertain')),
    prepared_at INTEGER,
    verified_at INTEGER,
    published_at INTEGER,
    CHECK (state NOT IN ('complete_verified', 'published') OR verified_at IS NOT NULL),
    CHECK (state <> 'published' OR published_at IS NOT NULL),
    UNIQUE (subscription_id, generation)
)""",
    "CREATE UNIQUE INDEX composite_config_generations_one_published "
    "ON composite_config_generations (subscription_id) WHERE state = 'published'",
)

# data-model.md §5-§7: child credentials, their inbound attachments and
# cleanup obligations; meters, immutable observations, meter deltas and usage
# gaps; entitlement periods, immutable boundary readings, reminder periods and
# reminders. Same-owner rules use composite foreign keys; carried time is in
# milliseconds and capped at 360 hours (1,296,000,000 ms).
_ACCOUNTING_DDL = (
    "CREATE UNIQUE INDEX composite_prepared_bindings_panel ON composite_prepared_bindings (binding_id, physical_panel_id)",
    """CREATE TABLE composite_meters (
    meter_id TEXT PRIMARY KEY,
    subscription_id TEXT NOT NULL REFERENCES composite_subscriptions (subscription_id) ON DELETE RESTRICT,
    physical_panel_id TEXT NOT NULL REFERENCES composite_physical_panels (physical_panel_id) ON DELETE RESTRICT,
    traffic_key TEXT NOT NULL,
    serving_class TEXT NOT NULL CHECK (serving_class IN ('serving', 'retired', 'emergency_exposure')),
    required_current INTEGER NOT NULL DEFAULT 0 CHECK (required_current IN (0, 1)),
    upload_epoch INTEGER NOT NULL DEFAULT 0 CHECK (typeof(upload_epoch) = 'integer' AND upload_epoch >= 0),
    download_epoch INTEGER NOT NULL DEFAULT 0 CHECK (typeof(download_epoch) = 'integer' AND download_epoch >= 0),
    last_observation_id TEXT REFERENCES composite_observations (observation_id) ON DELETE RESTRICT,
    last_observed_at INTEGER,
    failure_state TEXT,
    restart_loss_annotations TEXT,
    CHECK (required_current = 0 OR serving_class = 'serving'),
    UNIQUE (physical_panel_id, traffic_key),
    UNIQUE (meter_id, subscription_id)
)""",
    """CREATE TABLE composite_children (
    child_id TEXT PRIMARY KEY,
    subscription_id TEXT NOT NULL,
    logical_node_key TEXT NOT NULL,
    credential_generation INTEGER NOT NULL CHECK (typeof(credential_generation) = 'integer' AND credential_generation >= 1),
    physical_panel_id TEXT NOT NULL REFERENCES composite_physical_panels (physical_panel_id) ON DELETE RESTRICT,
    remote_email TEXT NOT NULL,
    protocol TEXT NOT NULL CHECK (protocol IN ('vless', 'vmess', 'trojan')),
    encrypted_secret BLOB NOT NULL CHECK (typeof(encrypted_secret) = 'blob'),
    secret_key_id TEXT NOT NULL,
    secret_fingerprint TEXT NOT NULL,
    sub_id_ref TEXT,
    meter_id TEXT,
    desired_state TEXT NOT NULL CHECK (desired_state IN ('enabled', 'disabled', 'removed')),
    desired_revision INTEGER NOT NULL DEFAULT 0 CHECK (typeof(desired_revision) = 'integer' AND desired_revision >= 0),
    confirmed_access TEXT NOT NULL DEFAULT 'unknown' CHECK (confirmed_access IN ('unknown', 'partial', 'confirmed_eligible', 'confirmed_fresh_auth_denied')),
    confirmed_at INTEGER,
    retired_at INTEGER,
    retire_reason TEXT,
    CHECK ((retired_at IS NULL) = (retire_reason IS NULL)),
    UNIQUE (physical_panel_id, remote_email),
    UNIQUE (subscription_id, logical_node_key, credential_generation),
    UNIQUE (child_id, physical_panel_id),
    FOREIGN KEY (subscription_id, logical_node_key) REFERENCES composite_subscription_nodes (subscription_id, logical_node_key) ON DELETE RESTRICT,
    FOREIGN KEY (meter_id, subscription_id) REFERENCES composite_meters (meter_id, subscription_id) ON DELETE RESTRICT
)""",
    """CREATE TRIGGER composite_children_identity_fixed
    BEFORE UPDATE OF subscription_id, logical_node_key, credential_generation, physical_panel_id, remote_email, protocol, secret_fingerprint ON composite_children
    WHEN NEW.subscription_id IS NOT OLD.subscription_id OR NEW.logical_node_key IS NOT OLD.logical_node_key
        OR NEW.credential_generation IS NOT OLD.credential_generation OR NEW.physical_panel_id IS NOT OLD.physical_panel_id
        OR NEW.remote_email IS NOT OLD.remote_email OR NEW.protocol IS NOT OLD.protocol OR NEW.secret_fingerprint IS NOT OLD.secret_fingerprint
    BEGIN SELECT RAISE(ABORT, 'child identity is immutable'); END""",
    """CREATE TRIGGER composite_children_no_delete BEFORE DELETE ON composite_children
    BEGIN SELECT RAISE(ABORT, 'children are kept'); END""",
    """CREATE TABLE composite_child_attachments (
    attachment_id TEXT PRIMARY KEY,
    child_id TEXT NOT NULL,
    physical_panel_id TEXT NOT NULL,
    binding_id TEXT NOT NULL,
    settings_fingerprint TEXT NOT NULL,
    egress_key TEXT NOT NULL,
    expected_member INTEGER NOT NULL CHECK (expected_member IN (0, 1)),
    confirmed_member TEXT NOT NULL DEFAULT 'unknown' CHECK (confirmed_member IN ('unknown', 'present', 'absent')),
    UNIQUE (child_id, binding_id),
    FOREIGN KEY (child_id, physical_panel_id) REFERENCES composite_children (child_id, physical_panel_id) ON DELETE RESTRICT,
    FOREIGN KEY (binding_id, physical_panel_id) REFERENCES composite_prepared_bindings (binding_id, physical_panel_id) ON DELETE RESTRICT
)""",
    """CREATE TABLE composite_cleanup_obligations (
    obligation_id TEXT PRIMARY KEY,
    child_id TEXT NOT NULL REFERENCES composite_children (child_id) ON DELETE RESTRICT,
    meter_id TEXT REFERENCES composite_meters (meter_id) ON DELETE RESTRICT,
    responsible_actor TEXT NOT NULL,
    reason TEXT NOT NULL,
    desired_outcome TEXT NOT NULL CHECK (desired_outcome IN ('fresh_auth_denied', 'removed')),
    status TEXT NOT NULL CHECK (status IN ('open', 'escalated', 'resolved')),
    disabled_at INTEGER,
    final_upload_bytes INTEGER CHECK (final_upload_bytes IS NULL OR (typeof(final_upload_bytes) = 'integer' AND final_upload_bytes >= 0)),
    final_download_bytes INTEGER CHECK (final_download_bytes IS NULL OR (typeof(final_download_bytes) = 'integer' AND final_download_bytes >= 0)),
    deleted_at INTEGER,
    still_growing_at_delete INTEGER CHECK (still_growing_at_delete IN (0, 1)),
    next_check_at INTEGER,
    escalation_ref TEXT,
    CHECK (deleted_at IS NULL OR (disabled_at IS NOT NULL AND deleted_at >= disabled_at
        AND final_upload_bytes IS NOT NULL AND final_download_bytes IS NOT NULL)),
    CHECK ((deleted_at IS NULL) = (still_growing_at_delete IS NULL)),
    CHECK (status <> 'resolved' OR CASE desired_outcome WHEN 'removed' THEN deleted_at IS NOT NULL ELSE disabled_at IS NOT NULL END)
)""",
    """CREATE TRIGGER composite_cleanup_obligations_no_delete BEFORE DELETE ON composite_cleanup_obligations
    BEGIN SELECT RAISE(ABORT, 'cleanup obligations are kept'); END""",
    """CREATE TABLE composite_observations (
    observation_id TEXT PRIMARY KEY,
    meter_id TEXT NOT NULL REFERENCES composite_meters (meter_id) ON DELETE RESTRICT,
    upload_epoch INTEGER NOT NULL CHECK (typeof(upload_epoch) = 'integer' AND upload_epoch >= 0),
    download_epoch INTEGER NOT NULL CHECK (typeof(download_epoch) = 'integer' AND download_epoch >= 0),
    upload_bytes INTEGER NOT NULL CHECK (typeof(upload_bytes) = 'integer' AND upload_bytes >= 0),
    download_bytes INTEGER NOT NULL CHECK (typeof(download_bytes) = 'integer' AND download_bytes >= 0),
    dispatched_at INTEGER,
    received_at INTEGER NOT NULL CHECK (typeof(received_at) = 'integer'),
    outcome TEXT NOT NULL CHECK (outcome IN ('accepted', 'out_of_order')),
    restart_evidence TEXT,
    evidence_hash TEXT NOT NULL,
    UNIQUE (observation_id, meter_id)
)""",
    """CREATE TRIGGER composite_observations_no_update BEFORE UPDATE ON composite_observations
    BEGIN SELECT RAISE(ABORT, 'observations are immutable'); END""",
    """CREATE TABLE composite_entitlement_periods (
    period_id TEXT PRIMARY KEY,
    subscription_id TEXT NOT NULL REFERENCES composite_subscriptions (subscription_id) ON DELETE RESTRICT,
    operation_id TEXT NOT NULL UNIQUE,
    grant_kind TEXT NOT NULL CHECK (grant_kind IN ('initial_paid', 'initial_test', 'renewal', 'conversion')),
    offer_id TEXT NOT NULL REFERENCES composite_offers (offer_id) ON DELETE RESTRICT,
    authorized_at INTEGER,
    effective_at INTEGER NOT NULL CHECK (typeof(effective_at) = 'integer'),
    previous_period_id TEXT REFERENCES composite_entitlement_periods (period_id) ON DELETE RESTRICT,
    previous_expires_at INTEGER,
    timely_payment INTEGER NOT NULL DEFAULT 0 CHECK (timely_payment IN (0, 1)),
    purchased_bytes INTEGER NOT NULL CHECK (typeof(purchased_bytes) = 'integer' AND purchased_bytes > 0),
    purchased_seconds INTEGER NOT NULL CHECK (typeof(purchased_seconds) = 'integer' AND purchased_seconds > 0),
    carried_bytes INTEGER NOT NULL DEFAULT 0 CHECK (typeof(carried_bytes) = 'integer' AND carried_bytes >= 0),
    carried_ms INTEGER NOT NULL DEFAULT 0 CHECK (typeof(carried_ms) = 'integer' AND carried_ms BETWEEN 0 AND 1296000000),
    forfeited_ms INTEGER NOT NULL DEFAULT 0 CHECK (typeof(forfeited_ms) = 'integer' AND forfeited_ms >= 0),
    available_bytes INTEGER NOT NULL CHECK (typeof(available_bytes) = 'integer'),
    expires_at INTEGER NOT NULL,
    uncertainty TEXT,
    CHECK (available_bytes = purchased_bytes + carried_bytes),
    CHECK (expires_at = effective_at + purchased_seconds * 1000 + carried_ms),
    CHECK (CASE WHEN previous_expires_at IS NULL THEN carried_ms = 0 AND forfeited_ms = 0
        ELSE carried_ms = min(max(previous_expires_at - effective_at, 0), 1296000000)
        AND forfeited_ms = max(previous_expires_at - effective_at, 0) - carried_ms END),
    CHECK (timely_payment = 0 OR (authorized_at IS NOT NULL AND previous_expires_at IS NOT NULL AND authorized_at < previous_expires_at)),
    CHECK (carried_bytes = 0 OR timely_payment = 1 OR (previous_expires_at IS NOT NULL AND effective_at < previous_expires_at)),
    UNIQUE (period_id, grant_kind)
)""",
    """CREATE TABLE composite_meter_deltas (
    delta_id TEXT PRIMARY KEY,
    meter_id TEXT NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('upload', 'download')),
    epoch INTEGER NOT NULL CHECK (typeof(epoch) = 'integer' AND epoch >= 0),
    predecessor_observation_id TEXT NOT NULL,
    current_observation_id TEXT NOT NULL,
    delta_bytes INTEGER NOT NULL CHECK (typeof(delta_bytes) = 'integer' AND delta_bytes >= 0),
    interval_start_at INTEGER NOT NULL,
    interval_end_at INTEGER NOT NULL,
    child_id TEXT NOT NULL REFERENCES composite_children (child_id) ON DELETE RESTRICT,
    period_id TEXT REFERENCES composite_entitlement_periods (period_id) ON DELETE RESTRICT,
    allocation_state TEXT NOT NULL CHECK (allocation_state IN ('attributed', 'absorbed_exposure', 'gap_affected')),
    CHECK (predecessor_observation_id <> current_observation_id),
    UNIQUE (meter_id, direction, epoch, predecessor_observation_id),
    FOREIGN KEY (predecessor_observation_id, meter_id) REFERENCES composite_observations (observation_id, meter_id) ON DELETE RESTRICT,
    FOREIGN KEY (current_observation_id, meter_id) REFERENCES composite_observations (observation_id, meter_id) ON DELETE RESTRICT
)""",
    """CREATE TRIGGER composite_meter_deltas_no_delete BEFORE DELETE ON composite_meter_deltas
    BEGIN SELECT RAISE(ABORT, 'deltas are kept'); END""",
    """CREATE TRIGGER composite_meter_deltas_fixed
    BEFORE UPDATE OF meter_id, direction, epoch, predecessor_observation_id, current_observation_id, delta_bytes ON composite_meter_deltas
    WHEN NEW.meter_id IS NOT OLD.meter_id OR NEW.direction IS NOT OLD.direction OR NEW.epoch IS NOT OLD.epoch
        OR NEW.predecessor_observation_id IS NOT OLD.predecessor_observation_id
        OR NEW.current_observation_id IS NOT OLD.current_observation_id OR NEW.delta_bytes IS NOT OLD.delta_bytes
    BEGIN SELECT RAISE(ABORT, 'confirmed deltas are immutable'); END""",
    """CREATE TABLE composite_usage_gaps (
    gap_id TEXT PRIMARY KEY,
    meter_id TEXT NOT NULL,
    subscription_id TEXT NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('upload', 'download')),
    before_observation_id TEXT,
    after_observation_id TEXT,
    lower_bound_bytes INTEGER NOT NULL CHECK (typeof(lower_bound_bytes) = 'integer' AND lower_bound_bytes >= 0),
    upper_bound_bytes INTEGER CHECK (upper_bound_bytes IS NULL OR (typeof(upper_bound_bytes) = 'integer' AND upper_bound_bytes >= lower_bound_bytes)),
    reason TEXT NOT NULL CHECK (reason IN ('decrease', 'reset', 'missing_history')),
    state TEXT NOT NULL CHECK (state IN ('unresolved', 'usage_settled')),
    settled_by TEXT,
    settled_at INTEGER,
    settlement_reason TEXT,
    accepted_risk TEXT,
    remaining_uncertainty TEXT,
    CHECK (state <> 'usage_settled' OR (settled_by IS NOT NULL AND settled_at IS NOT NULL
        AND settlement_reason IS NOT NULL AND accepted_risk IS NOT NULL)),
    FOREIGN KEY (meter_id, subscription_id) REFERENCES composite_meters (meter_id, subscription_id) ON DELETE RESTRICT,
    FOREIGN KEY (before_observation_id, meter_id) REFERENCES composite_observations (observation_id, meter_id) ON DELETE RESTRICT,
    FOREIGN KEY (after_observation_id, meter_id) REFERENCES composite_observations (observation_id, meter_id) ON DELETE RESTRICT
)""",
    """CREATE TRIGGER composite_usage_gaps_no_delete BEFORE DELETE ON composite_usage_gaps
    BEGIN SELECT RAISE(ABORT, 'usage gaps are kept'); END""",
    """CREATE TABLE composite_boundary_readings (
    period_id TEXT NOT NULL REFERENCES composite_entitlement_periods (period_id) ON DELETE RESTRICT,
    meter_id TEXT NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('upload', 'download')),
    epoch INTEGER NOT NULL CHECK (typeof(epoch) = 'integer' AND epoch >= 0),
    observation_id TEXT NOT NULL,
    cumulative_bytes INTEGER NOT NULL CHECK (typeof(cumulative_bytes) = 'integer' AND cumulative_bytes >= 0),
    received_at INTEGER NOT NULL,
    age_ms INTEGER NOT NULL CHECK (typeof(age_ms) = 'integer' AND age_ms >= 0),
    required_current INTEGER NOT NULL CHECK (required_current IN (0, 1)),
    CHECK (required_current = 0 OR age_ms <= 60000),
    PRIMARY KEY (period_id, meter_id, direction),
    FOREIGN KEY (observation_id, meter_id) REFERENCES composite_observations (observation_id, meter_id) ON DELETE RESTRICT
)""",
    """CREATE TRIGGER composite_boundary_readings_no_update BEFORE UPDATE ON composite_boundary_readings
    BEGIN SELECT RAISE(ABORT, 'boundary readings are immutable'); END""",
    """CREATE TRIGGER composite_boundary_readings_no_delete BEFORE DELETE ON composite_boundary_readings
    BEGIN SELECT RAISE(ABORT, 'boundary readings are immutable'); END""",
    """CREATE TABLE composite_reminder_periods (
    reminder_period_id TEXT PRIMARY KEY,
    period_id TEXT NOT NULL UNIQUE,
    grant_kind TEXT NOT NULL CHECK (grant_kind IN ('initial_paid', 'renewal', 'conversion')),
    allowance_bytes INTEGER NOT NULL CHECK (typeof(allowance_bytes) = 'integer' AND allowance_bytes > 0),
    expires_at INTEGER NOT NULL,
    FOREIGN KEY (period_id, grant_kind) REFERENCES composite_entitlement_periods (period_id, grant_kind) ON DELETE RESTRICT
)""",
    """CREATE TABLE composite_reminders (
    reminder_id TEXT PRIMARY KEY,
    reminder_period_id TEXT NOT NULL REFERENCES composite_reminder_periods (reminder_period_id) ON DELETE RESTRICT,
    reminder_type TEXT NOT NULL CHECK (reminder_type IN ('expiry', 'quota')),
    expiry_threshold_seconds INTEGER CHECK (expiry_threshold_seconds IS NULL OR (typeof(expiry_threshold_seconds) = 'integer' AND expiry_threshold_seconds > 0)),
    quota_mode TEXT CHECK (quota_mode IN ('percent', 'remaining_bytes')),
    quota_percent INTEGER CHECK (quota_percent IS NULL OR (typeof(quota_percent) = 'integer' AND quota_percent BETWEEN 1 AND 100)),
    quota_remaining_bytes INTEGER CHECK (quota_remaining_bytes IS NULL OR (typeof(quota_remaining_bytes) = 'integer' AND quota_remaining_bytes > 0)),
    status TEXT NOT NULL DEFAULT 'armed' CHECK (status IN ('armed', 'due', 'accepted', 'cancelled')),
    condition_met_at INTEGER,
    due_at INTEGER,
    CHECK (CASE reminder_type
        WHEN 'expiry' THEN expiry_threshold_seconds IS NOT NULL AND quota_mode IS NULL AND quota_percent IS NULL AND quota_remaining_bytes IS NULL
        ELSE expiry_threshold_seconds IS NULL AND (
        (quota_mode IS 'percent' AND quota_percent IS NOT NULL AND quota_remaining_bytes IS NULL)
        OR (quota_mode IS 'remaining_bytes' AND quota_remaining_bytes IS NOT NULL AND quota_percent IS NULL)) END),
    CHECK (status NOT IN ('due', 'accepted') OR due_at IS NOT NULL),
    CHECK (due_at IS NULL OR (condition_met_at IS NOT NULL AND due_at >= condition_met_at)),
    UNIQUE (reminder_period_id, reminder_type)
)""",
    """CREATE TRIGGER composite_reminders_no_delete BEFORE DELETE ON composite_reminders
    BEGIN SELECT RAISE(ABORT, 'reminders are kept'); END""",
    """CREATE TRIGGER composite_reminders_accepted_final BEFORE UPDATE OF status ON composite_reminders
    WHEN OLD.status = 'accepted' AND NEW.status IS NOT 'accepted'
    BEGIN SELECT RAISE(ABORT, 'an accepted reminder never rearms'); END""",
    """CREATE TRIGGER composite_reminders_due_fixed BEFORE UPDATE OF due_at ON composite_reminders
    WHEN OLD.due_at IS NOT NULL AND NEW.due_at IS NOT OLD.due_at
    BEGIN SELECT RAISE(ABORT, 'the original due time is immutable'); END""",
)

# data-model.md §8-§9: checkouts, payment attempts, manual decisions and
# payment receipts; the shared financial obligations and the wallet ledger
# they settle into; resource reservations, test claims, campaigns and their
# permanent recipients. Amounts are checked integers; times are UTC epoch
# milliseconds; the 15-minute checkout and claim windows are 900,000 ms.
_COMMERCE_DDL = (
    """CREATE TABLE composite_checkouts (
    checkout_id TEXT PRIMARY KEY,
    order_id INTEGER NOT NULL UNIQUE REFERENCES orders (id) ON DELETE RESTRICT,
    tenant_installation_id TEXT NOT NULL,
    customer_telegram_id INTEGER NOT NULL,
    offer_id TEXT NOT NULL UNIQUE REFERENCES composite_offers (offer_id) ON DELETE RESTRICT,
    kind TEXT NOT NULL CHECK (kind IN ('initial', 'renewal', 'conversion')),
    target_subscription_id TEXT REFERENCES composite_subscriptions (subscription_id) ON DELETE RESTRICT,
    principal TEXT NOT NULL,
    request_key TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('quoted', 'awaiting_payment', 'manual_review', 'authorized', 'fulfilling', 'fulfilled', 'rejected', 'cancelled', 'failed')),
    final_price INTEGER NOT NULL CHECK (typeof(final_price) = 'integer' AND final_price >= 0),
    wallet_amount INTEGER NOT NULL DEFAULT 0 CHECK (typeof(wallet_amount) = 'integer' AND wallet_amount >= 0 AND wallet_amount <= final_price),
    authorization_source TEXT CHECK (authorization_source IN ('wallet', 'zero_price', 'receipt')),
    authorized_at INTEGER,
    deadline_at INTEGER,
    original_receipt_id TEXT,
    fulfillment_operation_id TEXT,
    terminal_reason TEXT,
    terminal_at INTEGER,
    created_at INTEGER NOT NULL,
    CHECK ((kind = 'initial') = (target_subscription_id IS NULL)),
    CHECK ((authorization_source IS NULL) = (authorized_at IS NULL)),
    CHECK (deadline_at IS authorized_at + 900000),
    CHECK ((authorization_source IS 'receipt') = (original_receipt_id IS NOT NULL)),
    CHECK (authorization_source IS NOT 'wallet' OR (final_price > 0 AND wallet_amount = final_price)),
    CHECK (authorization_source IS NOT 'zero_price' OR final_price = 0),
    CHECK (authorization_source IS NOT 'receipt' OR final_price > wallet_amount),
    CHECK (CASE WHEN status IN ('quoted', 'awaiting_payment', 'manual_review', 'rejected') THEN authorized_at IS NULL
        WHEN status IN ('authorized', 'fulfilling', 'fulfilled', 'failed') THEN authorized_at IS NOT NULL ELSE 1 END),
    CHECK ((terminal_at IS NULL) = (terminal_reason IS NULL)),
    CHECK ((status IN ('rejected', 'cancelled', 'failed')) = (terminal_at IS NOT NULL)),
    CHECK (status NOT IN ('fulfilling', 'fulfilled') OR fulfillment_operation_id IS NOT NULL),
    UNIQUE (principal, request_key),
    FOREIGN KEY (original_receipt_id, checkout_id) REFERENCES composite_payment_receipts (receipt_id, checkout_id) ON DELETE RESTRICT
)""",
    "CREATE UNIQUE INDEX composite_checkouts_one_open_target ON composite_checkouts (target_subscription_id) WHERE status IN ('quoted', 'awaiting_payment', 'manual_review', 'authorized', 'fulfilling')",
    """CREATE TRIGGER composite_checkouts_no_delete BEFORE DELETE ON composite_checkouts
    BEGIN SELECT RAISE(ABORT, 'checkouts are kept'); END""",
    """CREATE TRIGGER composite_checkouts_terms_fixed BEFORE UPDATE ON composite_checkouts
    WHEN NEW.order_id IS NOT OLD.order_id OR NEW.tenant_installation_id IS NOT OLD.tenant_installation_id
        OR NEW.customer_telegram_id IS NOT OLD.customer_telegram_id OR NEW.offer_id IS NOT OLD.offer_id
        OR NEW.kind IS NOT OLD.kind OR NEW.target_subscription_id IS NOT OLD.target_subscription_id
        OR NEW.principal IS NOT OLD.principal OR NEW.request_key IS NOT OLD.request_key
        OR NEW.final_price IS NOT OLD.final_price OR NEW.wallet_amount IS NOT OLD.wallet_amount
        OR NEW.created_at IS NOT OLD.created_at
    BEGIN SELECT RAISE(ABORT, 'checkout terms are immutable'); END""",
    """CREATE TRIGGER composite_checkouts_clock_fixed BEFORE UPDATE ON composite_checkouts
    WHEN (OLD.authorized_at IS NOT NULL AND NEW.authorized_at IS NOT OLD.authorized_at)
        OR (OLD.authorization_source IS NOT NULL AND NEW.authorization_source IS NOT OLD.authorization_source)
        OR (OLD.original_receipt_id IS NOT NULL AND NEW.original_receipt_id IS NOT OLD.original_receipt_id)
    BEGIN SELECT RAISE(ABORT, 'one authorization clock'); END""",
    """CREATE TRIGGER composite_checkouts_terminal_final BEFORE UPDATE OF status ON composite_checkouts
    WHEN OLD.status IN ('fulfilled', 'rejected', 'cancelled', 'failed') AND NEW.status IS NOT OLD.status
    BEGIN SELECT RAISE(ABORT, 'a finished checkout never reopens'); END""",
    """CREATE TABLE composite_payment_attempts (
    attempt_id TEXT PRIMARY KEY,
    checkout_id TEXT NOT NULL REFERENCES composite_checkouts (checkout_id) ON DELETE RESTRICT,
    method TEXT NOT NULL,
    provider TEXT NOT NULL,
    merchant_namespace TEXT NOT NULL,
    config_version TEXT NOT NULL,
    creation_intent TEXT NOT NULL UNIQUE,
    provider_invoice_ref TEXT,
    create_state TEXT NOT NULL CHECK (create_state IN ('pending', 'uncertain', 'created', 'failed')),
    native_amount INTEGER NOT NULL CHECK (typeof(native_amount) = 'integer' AND native_amount > 0),
    currency TEXT NOT NULL,
    minor_unit_scale INTEGER NOT NULL CHECK (typeof(minor_unit_scale) = 'integer' AND minor_unit_scale >= 0),
    store_remainder INTEGER NOT NULL CHECK (typeof(store_remainder) = 'integer' AND store_remainder > 0),
    invoice_value INTEGER NOT NULL CHECK (typeof(invoice_value) = 'integer' AND invoice_value >= store_remainder),
    quote_rules TEXT NOT NULL,
    quote_version TEXT NOT NULL,
    quote_accepted_at INTEGER NOT NULL,
    valid_until INTEGER,
    recovery_ref TEXT,
    status TEXT NOT NULL CHECK (status IN ('open', 'verified', 'expired', 'closed')),
    CHECK ((create_state = 'created') = (provider_invoice_ref IS NOT NULL)),
    CHECK (valid_until IS NULL OR valid_until > quote_accepted_at),
    UNIQUE (provider, merchant_namespace, provider_invoice_ref),
    UNIQUE (attempt_id, checkout_id)
)""",
    """CREATE TRIGGER composite_payment_attempts_no_delete BEFORE DELETE ON composite_payment_attempts
    BEGIN SELECT RAISE(ABORT, 'attempts are kept'); END""",
    """CREATE TRIGGER composite_payment_attempts_quote_fixed BEFORE UPDATE ON composite_payment_attempts
    WHEN NEW.checkout_id IS NOT OLD.checkout_id OR NEW.method IS NOT OLD.method OR NEW.provider IS NOT OLD.provider
        OR NEW.merchant_namespace IS NOT OLD.merchant_namespace OR NEW.config_version IS NOT OLD.config_version
        OR NEW.creation_intent IS NOT OLD.creation_intent OR NEW.native_amount IS NOT OLD.native_amount
        OR NEW.currency IS NOT OLD.currency OR NEW.minor_unit_scale IS NOT OLD.minor_unit_scale
        OR NEW.store_remainder IS NOT OLD.store_remainder OR NEW.invoice_value IS NOT OLD.invoice_value
        OR NEW.quote_rules IS NOT OLD.quote_rules OR NEW.quote_version IS NOT OLD.quote_version
        OR NEW.quote_accepted_at IS NOT OLD.quote_accepted_at OR NEW.valid_until IS NOT OLD.valid_until
        OR (OLD.provider_invoice_ref IS NOT NULL AND NEW.provider_invoice_ref IS NOT OLD.provider_invoice_ref)
    BEGIN SELECT RAISE(ABORT, 'an accepted quote is immutable'); END""",
    """CREATE TABLE composite_manual_decisions (
    decision_id TEXT PRIMARY KEY,
    attempt_id TEXT NOT NULL REFERENCES composite_payment_attempts (attempt_id) ON DELETE RESTRICT,
    principal TEXT NOT NULL,
    principal_role TEXT NOT NULL CHECK (principal_role = 'owner'),
    interface TEXT NOT NULL CHECK (interface IN ('telegram', 'web')),
    provider_reference TEXT,
    evidence_digest TEXT NOT NULL,
    tenant_installation_id TEXT NOT NULL,
    customer_telegram_id INTEGER NOT NULL,
    amount INTEGER CHECK (amount IS NULL OR (typeof(amount) = 'integer' AND amount > 0)),
    currency TEXT NOT NULL,
    method TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN ('approved', 'rejected', 'mismatch_hold')),
    reason TEXT,
    decided_at INTEGER NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    CHECK (decision <> 'approved' OR (provider_reference IS NOT NULL AND amount IS NOT NULL)),
    CHECK (decision = 'approved' OR reason IS NOT NULL),
    UNIQUE (decision_id, attempt_id)
)""",
    """CREATE TRIGGER composite_manual_decisions_no_update BEFORE UPDATE ON composite_manual_decisions
    BEGIN SELECT RAISE(ABORT, 'decisions are final'); END""",
    """CREATE TRIGGER composite_manual_decisions_no_delete BEFORE DELETE ON composite_manual_decisions
    BEGIN SELECT RAISE(ABORT, 'decisions are final'); END""",
    """CREATE TABLE composite_payment_receipts (
    receipt_id TEXT PRIMARY KEY,
    attempt_id TEXT NOT NULL,
    checkout_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    merchant_namespace TEXT NOT NULL,
    transaction_reference TEXT NOT NULL,
    tenant_installation_id TEXT NOT NULL,
    beneficiary_telegram_id INTEGER NOT NULL,
    native_amount INTEGER NOT NULL CHECK (typeof(native_amount) = 'integer' AND native_amount > 0),
    currency TEXT NOT NULL,
    invoice_value INTEGER CHECK (invoice_value IS NULL OR (typeof(invoice_value) = 'integer' AND invoice_value > 0)),
    verification_source TEXT NOT NULL CHECK (verification_source IN ('provider', 'manual')),
    manual_decision_id TEXT,
    evidence_digest TEXT NOT NULL,
    verified_at INTEGER NOT NULL,
    outcome TEXT NOT NULL CHECK (outcome IN ('original_funding', 'extra_credit', 'terminal_late_credit', 'mismatch_hold')),
    CHECK ((verification_source = 'manual') = (manual_decision_id IS NOT NULL)),
    CHECK (outcome = 'mismatch_hold' OR invoice_value IS NOT NULL),
    UNIQUE (provider, merchant_namespace, transaction_reference),
    UNIQUE (receipt_id, checkout_id),
    FOREIGN KEY (attempt_id, checkout_id) REFERENCES composite_payment_attempts (attempt_id, checkout_id) ON DELETE RESTRICT,
    FOREIGN KEY (manual_decision_id, attempt_id) REFERENCES composite_manual_decisions (decision_id, attempt_id) ON DELETE RESTRICT
)""",
    "CREATE UNIQUE INDEX composite_payment_receipts_one_original ON composite_payment_receipts (checkout_id) WHERE outcome = 'original_funding'",
    """CREATE TRIGGER composite_payment_receipts_no_delete BEFORE DELETE ON composite_payment_receipts
    BEGIN SELECT RAISE(ABORT, 'receipts are kept'); END""",
    """CREATE TRIGGER composite_payment_receipts_evidence_fixed BEFORE UPDATE ON composite_payment_receipts
    WHEN NEW.attempt_id IS NOT OLD.attempt_id OR NEW.checkout_id IS NOT OLD.checkout_id OR NEW.provider IS NOT OLD.provider
        OR NEW.merchant_namespace IS NOT OLD.merchant_namespace OR NEW.transaction_reference IS NOT OLD.transaction_reference
        OR NEW.tenant_installation_id IS NOT OLD.tenant_installation_id OR NEW.beneficiary_telegram_id IS NOT OLD.beneficiary_telegram_id
        OR NEW.native_amount IS NOT OLD.native_amount OR NEW.currency IS NOT OLD.currency
        OR (OLD.invoice_value IS NOT NULL AND NEW.invoice_value IS NOT OLD.invoice_value)
        OR NEW.verification_source IS NOT OLD.verification_source OR NEW.manual_decision_id IS NOT OLD.manual_decision_id
        OR NEW.evidence_digest IS NOT OLD.evidence_digest OR NEW.verified_at IS NOT OLD.verified_at
        OR (OLD.outcome <> 'mismatch_hold' AND NEW.outcome IS NOT OLD.outcome)
    BEGIN SELECT RAISE(ABORT, 'receipt evidence is immutable'); END""",
    """CREATE TABLE financial_obligations (
    obligation_id TEXT PRIMARY KEY,
    effect_key TEXT NOT NULL UNIQUE,
    tenant_installation_id TEXT NOT NULL,
    beneficiary_telegram_id INTEGER NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('wallet_debit', 'wallet_release', 'full_refund', 'late_credit', 'extra_credit', 'support_compensation', 'topup_credit')),
    amount INTEGER NOT NULL CHECK (typeof(amount) = 'integer' AND amount > 0),
    evidence_ref TEXT,
    checkout_id TEXT REFERENCES composite_checkouts (checkout_id) ON DELETE RESTRICT,
    receipt_id TEXT,
    batch_ref TEXT,
    member_ref TEXT,
    triggered_at INTEGER NOT NULL,
    due_at INTEGER NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('owed', 'evidence_hold', 'settled')),
    ledger_seq INTEGER,
    settled_at INTEGER,
    CHECK ((state = 'settled') = (ledger_seq IS NOT NULL)),
    CHECK ((ledger_seq IS NULL) = (settled_at IS NULL)),
    CHECK (kind NOT IN ('wallet_debit', 'wallet_release', 'full_refund') OR checkout_id IS NOT NULL),
    CHECK ((kind IN ('late_credit', 'extra_credit')) = (receipt_id IS NOT NULL)),
    CHECK (receipt_id IS NULL OR checkout_id IS NOT NULL),
    CHECK (CASE WHEN kind IN ('wallet_release', 'full_refund', 'late_credit', 'extra_credit') THEN due_at = triggered_at + 60000
        ELSE due_at >= triggered_at END),
    UNIQUE (obligation_id, beneficiary_telegram_id, kind, amount),
    FOREIGN KEY (receipt_id, checkout_id) REFERENCES composite_payment_receipts (receipt_id, checkout_id) ON DELETE RESTRICT,
    FOREIGN KEY (ledger_seq, obligation_id) REFERENCES wallet_effects (ledger_seq, obligation_id) ON DELETE RESTRICT
)""",
    "CREATE UNIQUE INDEX financial_obligations_once_per_checkout ON financial_obligations (checkout_id, kind) WHERE kind IN ('wallet_debit', 'wallet_release', 'full_refund')",
    "CREATE UNIQUE INDEX financial_obligations_once_per_receipt ON financial_obligations (receipt_id)",
    """CREATE TRIGGER financial_obligations_no_delete BEFORE DELETE ON financial_obligations
    BEGIN SELECT RAISE(ABORT, 'obligations are kept'); END""",
    """CREATE TRIGGER financial_obligations_fixed BEFORE UPDATE ON financial_obligations
    WHEN NEW.effect_key IS NOT OLD.effect_key OR NEW.tenant_installation_id IS NOT OLD.tenant_installation_id
        OR NEW.beneficiary_telegram_id IS NOT OLD.beneficiary_telegram_id OR NEW.kind IS NOT OLD.kind
        OR NEW.amount IS NOT OLD.amount OR NEW.evidence_ref IS NOT OLD.evidence_ref
        OR NEW.checkout_id IS NOT OLD.checkout_id OR NEW.receipt_id IS NOT OLD.receipt_id
        OR NEW.batch_ref IS NOT OLD.batch_ref OR NEW.member_ref IS NOT OLD.member_ref
        OR NEW.triggered_at IS NOT OLD.triggered_at OR NEW.due_at IS NOT OLD.due_at
        OR (OLD.state = 'settled' AND (NEW.state IS NOT OLD.state OR NEW.ledger_seq IS NOT OLD.ledger_seq OR NEW.settled_at IS NOT OLD.settled_at))
    BEGIN SELECT RAISE(ABORT, 'obligation terms are immutable and settlement is final'); END""",
    """CREATE TABLE wallet_effects (
    ledger_seq INTEGER PRIMARY KEY,
    obligation_id TEXT NOT NULL UNIQUE,
    beneficiary_telegram_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    amount INTEGER NOT NULL,
    balance_before INTEGER NOT NULL CHECK (typeof(balance_before) = 'integer'),
    balance_after INTEGER NOT NULL CHECK (typeof(balance_after) = 'integer'),
    applied_at INTEGER NOT NULL,
    CHECK (balance_after = balance_before + CASE WHEN kind = 'wallet_debit' THEN -amount ELSE amount END),
    CHECK (kind <> 'wallet_debit' OR balance_after >= 0),
    UNIQUE (ledger_seq, obligation_id),
    FOREIGN KEY (obligation_id, beneficiary_telegram_id, kind, amount)
        REFERENCES financial_obligations (obligation_id, beneficiary_telegram_id, kind, amount) ON DELETE RESTRICT
)""",
    """CREATE TRIGGER wallet_effects_no_update BEFORE UPDATE ON wallet_effects
    BEGIN SELECT RAISE(ABORT, 'ledger entries are permanent'); END""",
    """CREATE TRIGGER wallet_effects_no_delete BEFORE DELETE ON wallet_effects
    BEGIN SELECT RAISE(ABORT, 'ledger entries are permanent'); END""",
    """CREATE TABLE composite_campaigns (
    campaign_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    plan_kind TEXT NOT NULL DEFAULT 'campaign' CHECK (plan_kind = 'campaign'),
    lifetime_cap INTEGER NOT NULL DEFAULT 150 CHECK (lifetime_cap = 150),
    served_count INTEGER NOT NULL DEFAULT 0 CHECK (typeof(served_count) = 'integer' AND served_count >= 0 AND served_count <= lifetime_cap),
    closed_at INTEGER,
    history_verified_at INTEGER,
    CHECK ((closed_at IS NOT NULL) = (served_count = lifetime_cap)),
    FOREIGN KEY (plan_id, plan_kind) REFERENCES composite_plans (plan_id, kind) ON DELETE RESTRICT
)""",
    """CREATE TRIGGER composite_campaigns_no_delete BEFORE DELETE ON composite_campaigns
    BEGIN SELECT RAISE(ABORT, 'campaigns are kept'); END""",
    """CREATE TRIGGER composite_campaigns_history_fixed BEFORE UPDATE ON composite_campaigns
    WHEN NEW.plan_id IS NOT OLD.plan_id OR NEW.served_count < OLD.served_count
        OR (OLD.closed_at IS NOT NULL AND NEW.closed_at IS NOT OLD.closed_at)
    BEGIN SELECT RAISE(ABORT, 'campaign places never return'); END""",
    """CREATE TABLE composite_test_claims (
    claim_id TEXT PRIMARY KEY,
    tenant_installation_id TEXT NOT NULL,
    customer_telegram_id INTEGER NOT NULL,
    offer_id TEXT NOT NULL UNIQUE REFERENCES composite_offers (offer_id) ON DELETE RESTRICT,
    campaign_id TEXT REFERENCES composite_campaigns (campaign_id) ON DELETE RESTRICT,
    accepted_seq INTEGER NOT NULL UNIQUE CHECK (typeof(accepted_seq) = 'integer' AND accepted_seq > 0),
    accepted_at INTEGER NOT NULL,
    deadline_at INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'fulfilled', 'failed', 'uncertain')),
    fulfilled_at INTEGER,
    retrieval_evidence TEXT,
    terminal_at INTEGER,
    terminal_reason TEXT,
    CHECK (deadline_at = accepted_at + 900000),
    CHECK ((status = 'fulfilled') = (fulfilled_at IS NOT NULL)),
    CHECK (fulfilled_at IS NULL OR (fulfilled_at <= deadline_at AND retrieval_evidence IS NOT NULL)),
    CHECK ((status IN ('failed', 'uncertain')) = (terminal_at IS NOT NULL)),
    CHECK ((terminal_at IS NULL) = (terminal_reason IS NULL)),
    UNIQUE (claim_id, campaign_id),
    UNIQUE (claim_id, campaign_id, customer_telegram_id, status)
)""",
    "CREATE UNIQUE INDEX composite_test_claims_one_pending ON composite_test_claims (customer_telegram_id) WHERE status = 'pending'",
    """CREATE TRIGGER composite_test_claims_no_delete BEFORE DELETE ON composite_test_claims
    BEGIN SELECT RAISE(ABORT, 'claims are kept'); END""",
    """CREATE TRIGGER composite_test_claims_fixed BEFORE UPDATE ON composite_test_claims
    WHEN NEW.tenant_installation_id IS NOT OLD.tenant_installation_id OR NEW.customer_telegram_id IS NOT OLD.customer_telegram_id
        OR NEW.offer_id IS NOT OLD.offer_id OR NEW.campaign_id IS NOT OLD.campaign_id
        OR NEW.accepted_seq IS NOT OLD.accepted_seq OR NEW.accepted_at IS NOT OLD.accepted_at OR NEW.deadline_at IS NOT OLD.deadline_at
        OR (OLD.status IN ('fulfilled', 'failed') AND NEW.status IS NOT OLD.status)
        OR (OLD.status = 'uncertain' AND NEW.status NOT IN ('uncertain', 'failed'))
    BEGIN SELECT RAISE(ABORT, 'claim identity and deadline are immutable'); END""",
    """CREATE TABLE resource_reservations (
    reservation_id TEXT PRIMARY KEY,
    resource TEXT NOT NULL CHECK (resource IN ('coupon', 'ordinary_test', 'campaign_place')),
    checkout_id TEXT REFERENCES composite_checkouts (checkout_id) ON DELETE RESTRICT,
    claim_id TEXT REFERENCES composite_test_claims (claim_id) ON DELETE RESTRICT,
    legacy_order_id INTEGER REFERENCES orders (id) ON DELETE RESTRICT,
    legacy_test_ref TEXT,
    tenant_installation_id TEXT NOT NULL,
    customer_telegram_id INTEGER NOT NULL,
    coupon_code_id INTEGER,
    campaign_id TEXT,
    sequence INTEGER NOT NULL UNIQUE CHECK (typeof(sequence) = 'integer' AND sequence > 0),
    accepted_at INTEGER NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('held', 'consumed', 'release_pending_refund', 'released', 'uncertain_hold')),
    transition_key TEXT,
    transitioned_at INTEGER,
    CHECK ((checkout_id IS NOT NULL) + (claim_id IS NOT NULL) + (legacy_order_id IS NOT NULL) + (legacy_test_ref IS NOT NULL) = 1),
    CHECK (CASE resource
        WHEN 'coupon' THEN (checkout_id IS NOT NULL OR legacy_order_id IS NOT NULL) AND coupon_code_id IS NOT NULL AND campaign_id IS NULL
        WHEN 'ordinary_test' THEN (claim_id IS NOT NULL OR legacy_test_ref IS NOT NULL) AND coupon_code_id IS NULL AND campaign_id IS NULL
        ELSE claim_id IS NOT NULL AND campaign_id IS NOT NULL AND coupon_code_id IS NULL END),
    CHECK ((state = 'held') = (transition_key IS NULL)),
    CHECK ((transition_key IS NULL) = (transitioned_at IS NULL)),
    CHECK (state <> 'release_pending_refund' OR resource = 'coupon'),
    CHECK (state <> 'uncertain_hold' OR resource <> 'coupon'),
    UNIQUE (checkout_id, resource),
    UNIQUE (claim_id, resource),
    UNIQUE (legacy_order_id, resource),
    UNIQUE (legacy_test_ref, resource),
    FOREIGN KEY (claim_id, campaign_id) REFERENCES composite_test_claims (claim_id, campaign_id) ON DELETE RESTRICT
)""",
    """CREATE TRIGGER resource_reservations_no_delete BEFORE DELETE ON resource_reservations
    BEGIN SELECT RAISE(ABORT, 'reservations are kept'); END""",
    """CREATE TRIGGER resource_reservations_fixed BEFORE UPDATE ON resource_reservations
    WHEN NEW.resource IS NOT OLD.resource OR NEW.checkout_id IS NOT OLD.checkout_id OR NEW.claim_id IS NOT OLD.claim_id
        OR NEW.legacy_order_id IS NOT OLD.legacy_order_id OR NEW.legacy_test_ref IS NOT OLD.legacy_test_ref
        OR NEW.tenant_installation_id IS NOT OLD.tenant_installation_id OR NEW.customer_telegram_id IS NOT OLD.customer_telegram_id
        OR NEW.coupon_code_id IS NOT OLD.coupon_code_id OR NEW.campaign_id IS NOT OLD.campaign_id
        OR NEW.sequence IS NOT OLD.sequence OR NEW.accepted_at IS NOT OLD.accepted_at
        OR (OLD.state IN ('consumed', 'released') AND NEW.state IS NOT OLD.state)
        OR (OLD.state = 'release_pending_refund' AND NEW.state NOT IN ('release_pending_refund', 'released'))
    BEGIN SELECT RAISE(ABORT, 'a finished reservation never changes'); END""",
    """CREATE TABLE composite_campaign_recipients (
    campaign_id TEXT NOT NULL REFERENCES composite_campaigns (campaign_id) ON DELETE RESTRICT,
    customer_telegram_id INTEGER NOT NULL,
    claim_id TEXT NOT NULL UNIQUE,
    claim_status TEXT NOT NULL DEFAULT 'fulfilled' CHECK (claim_status = 'fulfilled'),
    fulfilled_at INTEGER NOT NULL,
    PRIMARY KEY (campaign_id, customer_telegram_id),
    FOREIGN KEY (claim_id, campaign_id, customer_telegram_id, claim_status)
        REFERENCES composite_test_claims (claim_id, campaign_id, customer_telegram_id, status) ON DELETE RESTRICT
)""",
    """CREATE TRIGGER composite_campaign_recipients_no_update BEFORE UPDATE ON composite_campaign_recipients
    BEGIN SELECT RAISE(ABORT, 'campaign recipients are permanent'); END""",
    """CREATE TRIGGER composite_campaign_recipients_no_delete BEFORE DELETE ON composite_campaign_recipients
    BEGIN SELECT RAISE(ABORT, 'campaign recipients are permanent'); END""",
)


@dataclass(frozen=True)
class AuthorizedPaths:
    """Paths the operator authorizes for one installation upgrade."""

    main: object
    tenants: tuple
    fsm: tuple
    pre_upgrade_dir: object
    base_dir: object


@dataclass(frozen=True)
class SchemaInfo:
    """The highest composite schema version found in a database."""

    version: int
    supported: bool


@dataclass(frozen=True)
class MemberOutcome:
    """The migration result for one database member."""

    path: str
    role: str
    tenant_id: int | None
    from_version: int
    to_version: int
    status: str


@dataclass(frozen=True)
class MigrationReport:
    """Ordered outcomes for the main and reseller databases."""

    outcomes: tuple[MemberOutcome, ...]


class MigrationError(Exception):
    """Base error for refused or unsuccessful migrations."""


class RegistryError(MigrationError):
    """The main database registry does not match authorized tenant files."""


class UnsupportedSchema(MigrationError):
    """A database uses a schema version newer than this release supports."""

    def __init__(self, path: str, version: int) -> None:
        self.path = path
        self.version = version
        super().__init__(f"{path} has composite schema version {version}; this release supports up to {SCHEMA_VERSION}")


class MigrationFailed(MigrationError):
    """A member failed before the complete installation was migrated."""

    def __init__(self, report: MigrationReport) -> None:
        self.report = report
        super().__init__("migration stopped before every member was migrated; issuance stays disabled")


def _read_version(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'composite_schema_versions'"
    ).fetchone()
    if row is None:
        return 0
    return int(conn.execute("SELECT COALESCE(MAX(version), 0) FROM composite_schema_versions").fetchone()[0])


def _readonly_connect(path: str) -> sqlite3.Connection:
    uri = "file:" + urllib.parse.quote(os.path.realpath(path)) + "?mode=ro"
    return sqlite3.connect(uri, uri=True)


def inspect_schema(path: str) -> SchemaInfo:
    """Read a database's composite schema version without creating the file."""
    conn = _readonly_connect(path)
    try:
        version = _read_version(conn)
        return SchemaInfo(version, version <= SCHEMA_VERSION)
    finally:
        conn.close()


def issuance_enabled(main_path: str) -> bool:
    """Report whether composite issuance is enabled; always ``False`` for now.

    Nothing can enable issuance yet: its switch belongs to the processing-control
    record a later schema step adds, and ``migrate`` never sets it.
    """
    return False


def _main_v1(conn: sqlite3.Connection) -> None:
    for table in KIND_TABLES:
        conn.execute(
            f"ALTER TABLE {table} ADD COLUMN service_kind TEXT NOT NULL DEFAULT 'legacy' "
            "CHECK (service_kind IN ('legacy', 'composite'))"
        )
        conn.execute(f"ALTER TABLE {table} ADD COLUMN composite_ref TEXT")
        conn.execute(f"CREATE UNIQUE INDEX idx_{table}_composite_ref ON {table} (composite_ref)")
    for statement in _PANEL_DDL + _CATALOG_DDL + _ACCOUNTING_DDL + _COMMERCE_DDL:
        conn.execute(statement)


def _reseller_v1(conn: sqlite3.Connection) -> None:
    for table in KIND_TABLES:
        conn.execute(
            f"ALTER TABLE {table} ADD COLUMN service_kind TEXT NOT NULL DEFAULT 'legacy' "
            "CHECK (service_kind = 'legacy')"
        )


_STEPS: dict[int, tuple[Callable[[sqlite3.Connection], None], Callable[[sqlite3.Connection], None]]] = {
    1: (_main_v1, _reseller_v1),
}


def migrate(paths: AuthorizedPaths, expected_release: str, *, crash=None) -> MigrationReport:
    """Back up and migrate every authorized database member in order."""
    if not isinstance(expected_release, str) or expected_release == "":
        raise ValueError("expected_release must be a non-empty str")

    pre = os.path.realpath(paths.pre_upgrade_dir)
    if not os.path.isdir(pre) or os.listdir(pre) != []:
        raise MigrationError("pre-upgrade directory must exist and be empty")

    main = os.path.realpath(paths.main)
    if not os.path.isfile(main):
        raise MigrationError(f"main database is not a regular file: {main}")

    conn = _readonly_connect(main)
    try:
        try:
            rows = conn.execute("SELECT id, db_path FROM reseller_bots ORDER BY id").fetchall()
        except sqlite3.OperationalError as exc:
            raise RegistryError("main database has no reseller_bots registry") from exc
    finally:
        conn.close()

    authorized = {os.path.realpath(t) for t in paths.tenants}
    seen: set[str] = set()
    tenant_members: list[tuple[int, str]] = []
    for tenant_id, db_path in rows:
        if not isinstance(db_path, str):
            raise RegistryError(f"reseller {tenant_id} db_path is not a string")
        candidate = db_path if os.path.isabs(db_path) else os.path.join(os.fspath(paths.base_dir), db_path)
        tenant_path = os.path.realpath(candidate)
        if (
            tenant_path in seen
            or tenant_path == main
            or not os.path.isfile(tenant_path)
            or tenant_path not in authorized
        ):
            raise RegistryError(f"invalid or unauthorized reseller database for tenant {tenant_id}")
        seen.add(tenant_path)
        tenant_members.append((tenant_id, tenant_path))
    if authorized != seen:
        raise RegistryError("authorized tenant files do not match reseller registry")

    fsm_files: list[str] = []
    seen_fsm: set[str] = set()
    for fsm_path in paths.fsm:
        real_fsm = os.path.realpath(fsm_path)
        if not os.path.isfile(real_fsm) or real_fsm in seen_fsm or real_fsm == main or real_fsm in seen:
            raise MigrationError(f"invalid FSM database file: {real_fsm}")
        seen_fsm.add(real_fsm)
        fsm_files.append(real_fsm)

    members: list[tuple[str, str, int | None, int]] = []
    for path, role, tenant_id in [(main, "main", None)] + [
        (path, "reseller", tenant_id) for tenant_id, path in tenant_members
    ]:
        info = inspect_schema(path)
        if not info.supported:
            raise UnsupportedSchema(path, info.version)
        members.append((path, role, tenant_id, info.version))

    copies = [(main, f"main-{os.path.basename(main)}")]
    copies.extend((path, f"reseller-{tenant_id}-{os.path.basename(path)}") for tenant_id, path in tenant_members)
    copies.extend((path, f"fsm-{i}-{os.path.basename(path)}") for i, path in enumerate(fsm_files, 1))
    for source_path, name in copies:
        src = dst = None
        try:
            src = _readonly_connect(source_path)
            dst = sqlite3.connect(os.path.join(pre, name))
            src.backup(dst)
        except Exception as exc:
            raise MigrationError(f"pre-upgrade copy of {source_path} failed") from exc
        finally:
            if dst is not None:
                dst.close()
            if src is not None:
                src.close()

    outcomes: list[MemberOutcome] = []
    for index, (path, role, tenant_id, from_version) in enumerate(members):
        if from_version == SCHEMA_VERSION:
            outcomes.append(MemberOutcome(path, role, tenant_id, from_version, from_version, "unchanged"))
            continue
        conn = None
        commit_started = False
        status = "failed"
        try:
            conn = sqlite3.connect(path, isolation_level=None, timeout=BUSY_TIMEOUT_S)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA synchronous = FULL")
            conn.execute("BEGIN IMMEDIATE")
            if _read_version(conn) != from_version:
                raise MigrationError(f"composite schema version of {path} changed during the run")
            conn.execute(
                "CREATE TABLE IF NOT EXISTS composite_schema_versions "
                "(version INTEGER PRIMARY KEY, release TEXT NOT NULL, applied_at INTEGER NOT NULL)"
            )
            for version in range(from_version + 1, SCHEMA_VERSION + 1):
                step = _STEPS[version][0 if role == "main" else 1]
                step(conn)
                conn.execute(
                    "INSERT INTO composite_schema_versions (version, release, applied_at) VALUES (?, ?, ?)",
                    (version, expected_release, time.time_ns() // 1_000_000),
                )
            if crash is not None:
                crash("before commit")
            commit_started = True
            conn.execute("COMMIT")
            status = "migrated"
            if crash is not None:
                crash("after commit")
            outcomes.append(MemberOutcome(path, role, tenant_id, from_version, SCHEMA_VERSION, status))
        except BaseException as exc:
            if conn is not None and conn.in_transaction:
                try:
                    conn.execute("ROLLBACK")
                except Exception:
                    pass
            if conn is not None:
                conn.close()
                conn = None
            if not isinstance(exc, Exception):
                raise
            if commit_started and status != "migrated":
                # COMMIT itself raised: read the outcome back, never commit again.
                try:
                    committed = inspect_schema(path).version == SCHEMA_VERSION
                except Exception:
                    committed = False
                status = "migrated" if committed else "failed"
            to_version = SCHEMA_VERSION if status == "migrated" else from_version
            outcomes.append(MemberOutcome(path, role, tenant_id, from_version, to_version, status))
            outcomes.extend(
                MemberOutcome(later_path, later_role, later_id, later_version, later_version, "not_attempted")
                for later_path, later_role, later_id, later_version in members[index + 1:]
            )
            raise MigrationFailed(MigrationReport(tuple(outcomes))) from exc
        finally:
            if conn is not None:
                conn.close()
    return MigrationReport(tuple(outcomes))
