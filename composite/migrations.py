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

# data-model.md §10: lifecycle operations; remote work, one row per desired
# state of one child, and its network attempts (at most five, each 15 s at
# most, an uncertain one quarantined from when its connection closed); drift
# sweeps and the divergences they find; FR-041 discrepancies with the in-use
# descriptors that differ from the panel. Times are UTC epoch milliseconds.
_LIFECYCLE_DDL = (
    """CREATE TABLE composite_operations (
    operation_id TEXT PRIMARY KEY,
    business_key TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL CHECK (kind IN ('fulfillment', 'test_fulfillment', 'checkout_rejection', 'customer_disable', 'customer_resume', 'owner_suspend', 'owner_resume', 'reporting_suspend', 'reporting_resume', 'leak_replacement', 'cancellation', 'move', 'cleanup', 'drift_repair')),
    subscription_id TEXT REFERENCES composite_subscriptions (subscription_id) ON DELETE RESTRICT,
    checkout_id TEXT REFERENCES composite_checkouts (checkout_id) ON DELETE RESTRICT,
    claim_id TEXT REFERENCES composite_test_claims (claim_id) ON DELETE RESTRICT,
    discrepancy_id TEXT REFERENCES composite_discrepancies (discrepancy_id) ON DELETE RESTRICT,
    actor TEXT NOT NULL,
    reason TEXT,
    desired_revision INTEGER CHECK (desired_revision IS NULL OR (typeof(desired_revision) = 'integer' AND desired_revision >= 0)),
    status TEXT NOT NULL CHECK (status IN ('accepted', 'in_progress', 'manual_hold', 'succeeded', 'failed', 'superseded')),
    phase TEXT,
    accepted_at INTEGER NOT NULL,
    authorized_at INTEGER CHECK (authorized_at IS NULL OR authorized_at >= accepted_at),
    ready_at INTEGER CHECK (ready_at IS NULL OR ready_at >= accepted_at),
    final_stage_at INTEGER CHECK (final_stage_at IS NULL OR final_stage_at >= accepted_at),
    target_at INTEGER CHECK (target_at IS NULL OR target_at >= accepted_at),
    deadline_at INTEGER CHECK (deadline_at IS NULL OR deadline_at >= accepted_at),
    escalation_at INTEGER CHECK (escalation_at IS NULL OR escalation_at >= accepted_at),
    missed_target_at INTEGER CHECK (missed_target_at IS NULL OR (target_at IS NOT NULL AND missed_target_at >= target_at)),
    prerequisite_ref TEXT,
    recovery_evidence_ref TEXT,
    worker_epoch INTEGER CHECK (worker_epoch IS NULL OR (typeof(worker_epoch) = 'integer' AND worker_epoch >= 0)),
    restore_epoch INTEGER NOT NULL CHECK (typeof(restore_epoch) = 'integer' AND restore_epoch >= 0),
    last_error TEXT,
    escalation_ref TEXT,
    finished_at INTEGER CHECK (finished_at IS NULL OR finished_at >= accepted_at),
    CHECK ((status IN ('succeeded', 'failed', 'superseded')) = (finished_at IS NOT NULL)),
    CHECK (CASE kind
        WHEN 'fulfillment' THEN checkout_id IS NOT NULL AND claim_id IS NULL AND discrepancy_id IS NULL
        WHEN 'checkout_rejection' THEN checkout_id IS NOT NULL AND claim_id IS NULL
        WHEN 'test_fulfillment' THEN claim_id IS NOT NULL AND checkout_id IS NULL AND discrepancy_id IS NULL
        ELSE subscription_id IS NOT NULL AND checkout_id IS NULL AND claim_id IS NULL AND discrepancy_id IS NULL
    END),
    UNIQUE (checkout_id, kind),
    UNIQUE (claim_id, kind)
)""",
    "CREATE UNIQUE INDEX composite_operations_one_open ON composite_operations (subscription_id, kind) WHERE kind IN ('leak_replacement', 'cancellation') AND status IN ('accepted', 'in_progress', 'manual_hold')",
    "CREATE UNIQUE INDEX composite_operations_subscription_kind ON composite_operations (operation_id, subscription_id, kind)",
    """CREATE TRIGGER composite_operations_identity_fixed BEFORE UPDATE ON composite_operations
    WHEN NEW.business_key IS NOT OLD.business_key OR NEW.kind IS NOT OLD.kind
        OR NEW.checkout_id IS NOT OLD.checkout_id OR NEW.claim_id IS NOT OLD.claim_id
        OR NEW.actor IS NOT OLD.actor OR NEW.accepted_at IS NOT OLD.accepted_at
        OR (OLD.subscription_id IS NOT NULL AND NEW.subscription_id IS NOT OLD.subscription_id)
        OR (OLD.discrepancy_id IS NOT NULL AND NEW.discrepancy_id IS NOT OLD.discrepancy_id)
        OR (OLD.desired_revision IS NOT NULL AND NEW.desired_revision IS NOT OLD.desired_revision)
    BEGIN SELECT RAISE(ABORT, 'an operation keeps its identity'); END""",
    """CREATE TRIGGER composite_operations_clocks_fixed BEFORE UPDATE ON composite_operations
    WHEN (OLD.authorized_at IS NOT NULL AND NEW.authorized_at IS NOT OLD.authorized_at)
        OR (OLD.ready_at IS NOT NULL AND NEW.ready_at IS NOT OLD.ready_at)
        OR (OLD.final_stage_at IS NOT NULL AND NEW.final_stage_at IS NOT OLD.final_stage_at)
        OR (OLD.target_at IS NOT NULL AND NEW.target_at IS NOT OLD.target_at)
        OR (OLD.deadline_at IS NOT NULL AND NEW.deadline_at IS NOT OLD.deadline_at)
        OR (OLD.escalation_at IS NOT NULL AND NEW.escalation_at IS NOT OLD.escalation_at)
        OR (OLD.missed_target_at IS NOT NULL AND NEW.missed_target_at IS NOT OLD.missed_target_at)
    BEGIN SELECT RAISE(ABORT, 'accepted clocks never restart'); END""",
    """CREATE TRIGGER composite_operations_finished_final BEFORE UPDATE ON composite_operations
    WHEN OLD.status IN ('succeeded', 'failed', 'superseded')
    BEGIN SELECT RAISE(ABORT, 'a finished operation never changes'); END""",
    """CREATE TRIGGER composite_operations_no_delete BEFORE DELETE ON composite_operations
    BEGIN SELECT RAISE(ABORT, 'operations are kept'); END""",
    """CREATE TABLE composite_remote_work (
    work_id TEXT PRIMARY KEY,
    operation_id TEXT NOT NULL REFERENCES composite_operations (operation_id) ON DELETE RESTRICT,
    child_id TEXT NOT NULL REFERENCES composite_children (child_id) ON DELETE RESTRICT,
    action TEXT NOT NULL CHECK (action IN ('create', 'enable', 'disable', 'delete')),
    desired_revision INTEGER NOT NULL CHECK (typeof(desired_revision) = 'integer' AND desired_revision >= 0),
    payload_fingerprint TEXT NOT NULL,
    encrypted_ref BLOB CHECK (encrypted_ref IS NULL OR typeof(encrypted_ref) = 'blob'),
    status TEXT NOT NULL CHECK (status IN ('queued', 'dispatched', 'uncertain', 'confirmed', 'manual_hold')),
    next_attempt_at INTEGER,
    observed_state TEXT,
    observed_at INTEGER,
    observed_matches INTEGER CHECK (observed_matches IS NULL OR observed_matches IN (0, 1)),
    runtime_required INTEGER NOT NULL CHECK (runtime_required IN (0, 1)),
    runtime_evidence_ref TEXT,
    confirmed_at INTEGER,
    hold_reason TEXT,
    created_at INTEGER NOT NULL,
    CHECK ((observed_state IS NULL) = (observed_at IS NULL) AND (observed_state IS NULL) = (observed_matches IS NULL)),
    CHECK ((status = 'confirmed') = (confirmed_at IS NOT NULL)),
    CHECK (status != 'confirmed' OR (observed_matches IS 1 AND confirmed_at >= observed_at AND (runtime_required = 0 OR runtime_evidence_ref IS NOT NULL))),
    CHECK ((status = 'manual_hold') = (hold_reason IS NOT NULL)),
    UNIQUE (operation_id, child_id, action, desired_revision),
    UNIQUE (work_id, child_id)
)""",
    """CREATE TRIGGER composite_remote_work_identity_fixed BEFORE UPDATE ON composite_remote_work
    WHEN NEW.operation_id IS NOT OLD.operation_id OR NEW.child_id IS NOT OLD.child_id
        OR NEW.action IS NOT OLD.action OR NEW.desired_revision IS NOT OLD.desired_revision
        OR NEW.payload_fingerprint IS NOT OLD.payload_fingerprint OR NEW.created_at IS NOT OLD.created_at
    BEGIN SELECT RAISE(ABORT, 'remote work keeps its identity'); END""",
    """CREATE TRIGGER composite_remote_work_read_back_after_writes BEFORE UPDATE ON composite_remote_work
    WHEN NEW.status = 'confirmed' AND OLD.status IS NOT 'confirmed' AND EXISTS (
        SELECT 1 FROM composite_remote_attempts
        WHERE work_id = NEW.work_id AND (NEW.observed_at IS NULL OR dispatched_at >= NEW.observed_at))
    BEGIN SELECT RAISE(ABORT, 'confirmation needs a read-back after the latest write'); END""",
    """CREATE TRIGGER composite_remote_work_confirmed_final BEFORE UPDATE ON composite_remote_work
    WHEN OLD.status = 'confirmed'
    BEGIN SELECT RAISE(ABORT, 'confirmed work never changes'); END""",
    """CREATE TRIGGER composite_remote_work_no_delete BEFORE DELETE ON composite_remote_work
    BEGIN SELECT RAISE(ABORT, 'remote work is kept'); END""",
    """CREATE TABLE composite_remote_attempts (
    attempt_id TEXT PRIMARY KEY,
    work_id TEXT NOT NULL REFERENCES composite_remote_work (work_id) ON DELETE RESTRICT,
    attempt_no INTEGER NOT NULL CHECK (typeof(attempt_no) = 'integer' AND attempt_no BETWEEN 1 AND 5),
    dispatched_at INTEGER NOT NULL,
    timeout_ms INTEGER NOT NULL CHECK (typeof(timeout_ms) = 'integer' AND timeout_ms BETWEEN 1 AND 15000),
    worker_epoch INTEGER NOT NULL CHECK (typeof(worker_epoch) = 'integer' AND worker_epoch >= 0),
    outcome TEXT NOT NULL CHECK (outcome IN ('in_flight', 'applied', 'rejected_no_effect', 'uncertain')),
    completed_at INTEGER,
    connection_closed_at INTEGER,
    quarantine_until INTEGER,
    error_ref TEXT,
    CHECK (CASE outcome
        WHEN 'in_flight' THEN completed_at IS NULL AND connection_closed_at IS NULL AND quarantine_until IS NULL
        WHEN 'uncertain' THEN completed_at IS NULL AND connection_closed_at IS NOT NULL AND connection_closed_at >= dispatched_at
            AND quarantine_until IS NOT NULL AND quarantine_until > connection_closed_at
        ELSE completed_at IS NOT NULL AND completed_at BETWEEN dispatched_at AND dispatched_at + timeout_ms AND connection_closed_at IS NULL AND quarantine_until IS NULL
    END),
    CHECK (outcome != 'rejected_no_effect' OR error_ref IS NOT NULL),
    UNIQUE (work_id, attempt_no)
)""",
    """CREATE TRIGGER composite_remote_attempts_not_after_confirmation BEFORE INSERT ON composite_remote_attempts
    WHEN EXISTS (SELECT 1 FROM composite_remote_work WHERE work_id = NEW.work_id AND status = 'confirmed')
    BEGIN SELECT RAISE(ABORT, 'confirmed work takes no further attempts'); END""",
    """CREATE TRIGGER composite_remote_attempts_identity_fixed BEFORE UPDATE ON composite_remote_attempts
    WHEN NEW.work_id IS NOT OLD.work_id OR NEW.attempt_no IS NOT OLD.attempt_no
        OR NEW.dispatched_at IS NOT OLD.dispatched_at OR NEW.timeout_ms IS NOT OLD.timeout_ms
        OR NEW.worker_epoch IS NOT OLD.worker_epoch
    BEGIN SELECT RAISE(ABORT, 'an attempt keeps its identity'); END""",
    """CREATE TRIGGER composite_remote_attempts_decided_final BEFORE UPDATE ON composite_remote_attempts
    WHEN OLD.outcome != 'in_flight'
    BEGIN SELECT RAISE(ABORT, 'a decided attempt never changes'); END""",
    """CREATE TRIGGER composite_remote_attempts_no_delete BEFORE DELETE ON composite_remote_attempts
    BEGIN SELECT RAISE(ABORT, 'attempts are kept'); END""",
    """CREATE TABLE composite_drift_sweeps (
    sweep_id TEXT PRIMARY KEY,
    physical_panel_id TEXT NOT NULL REFERENCES composite_physical_panels (physical_panel_id) ON DELETE RESTRICT,
    inbound_id INTEGER NOT NULL,
    started_at INTEGER NOT NULL,
    timeout_ms INTEGER NOT NULL CHECK (typeof(timeout_ms) = 'integer' AND timeout_ms BETWEEN 1 AND 15000),
    ended_at INTEGER CHECK (ended_at IS NULL OR ended_at >= started_at),
    outcome TEXT CHECK (outcome IS NULL OR outcome IN ('consistent', 'diverged', 'unknown')),
    error_ref TEXT,
    CHECK ((outcome IS NULL) = (ended_at IS NULL)),
    CHECK (CASE WHEN outcome IS NULL THEN error_ref IS NULL ELSE (outcome = 'unknown') = (error_ref IS NOT NULL) END),
    CHECK (outcome IS NOT 'consistent' OR ended_at <= started_at + timeout_ms),
    UNIQUE (sweep_id, physical_panel_id)
)""",
    """CREATE TRIGGER composite_drift_sweeps_starts_running BEFORE INSERT ON composite_drift_sweeps
    WHEN NEW.outcome = 'diverged'
    BEGIN SELECT RAISE(ABORT, 'a sweep cannot start out diverged'); END""",
    """CREATE TRIGGER composite_drift_sweeps_identity_fixed BEFORE UPDATE ON composite_drift_sweeps
    WHEN NEW.physical_panel_id IS NOT OLD.physical_panel_id OR NEW.inbound_id IS NOT OLD.inbound_id
        OR NEW.started_at IS NOT OLD.started_at OR NEW.timeout_ms IS NOT OLD.timeout_ms
    BEGIN SELECT RAISE(ABORT, 'a sweep keeps its identity'); END""",
    """CREATE TRIGGER composite_drift_sweeps_finished_final BEFORE UPDATE ON composite_drift_sweeps
    WHEN OLD.outcome IS NOT NULL
    BEGIN SELECT RAISE(ABORT, 'a finished sweep never changes'); END""",
    """CREATE TRIGGER composite_drift_sweeps_outcome_matches BEFORE UPDATE ON composite_drift_sweeps
    WHEN (NEW.outcome = 'consistent' AND EXISTS (SELECT 1 FROM composite_divergences WHERE sweep_id = NEW.sweep_id))
        OR (NEW.outcome = 'diverged' AND NOT EXISTS (SELECT 1 FROM composite_divergences WHERE sweep_id = NEW.sweep_id))
    BEGIN SELECT RAISE(ABORT, 'a sweep outcome must match its divergences'); END""",
    """CREATE TABLE composite_discrepancies (
    discrepancy_id TEXT PRIMARY KEY,
    kind TEXT NOT NULL CHECK (kind IN ('descriptor', 'repeated_divergence', 'identity')),
    child_id TEXT REFERENCES composite_children (child_id) ON DELETE RESTRICT,
    binding_id TEXT REFERENCES composite_prepared_bindings (binding_id) ON DELETE RESTRICT,
    observed_values TEXT,
    observed_at INTEGER,
    detected_at INTEGER NOT NULL,
    closed_at INTEGER CHECK (closed_at IS NULL OR closed_at >= detected_at),
    closure_reason TEXT,
    CHECK (CASE kind
        WHEN 'descriptor' THEN binding_id IS NOT NULL AND child_id IS NULL AND observed_values IS NOT NULL AND observed_at IS NOT NULL AND observed_at >= detected_at
        ELSE child_id IS NOT NULL AND binding_id IS NULL AND observed_values IS NULL AND observed_at IS NULL
    END),
    CHECK ((closed_at IS NULL) = (closure_reason IS NULL)),
    CHECK (closure_reason IS NULL OR CASE kind
        WHEN 'descriptor' THEN closure_reason IN ('panel_restored', 'no_longer_in_use')
        ELSE closure_reason = 'owner_resolved'
    END),
    UNIQUE (discrepancy_id, child_id),
    UNIQUE (discrepancy_id, kind)
)""",
    "CREATE UNIQUE INDEX composite_discrepancies_one_open_per_binding ON composite_discrepancies (binding_id) WHERE closed_at IS NULL AND binding_id IS NOT NULL",
    "CREATE UNIQUE INDEX composite_discrepancies_one_open_per_child ON composite_discrepancies (child_id, kind) WHERE closed_at IS NULL AND child_id IS NOT NULL",
    """CREATE TRIGGER composite_discrepancies_identity_fixed BEFORE UPDATE ON composite_discrepancies
    WHEN NEW.kind IS NOT OLD.kind OR NEW.binding_id IS NOT OLD.binding_id
        OR NEW.child_id IS NOT OLD.child_id OR NEW.detected_at IS NOT OLD.detected_at
    BEGIN SELECT RAISE(ABORT, 'a discrepancy keeps its identity'); END""",
    """CREATE TRIGGER composite_discrepancies_closed_final BEFORE UPDATE ON composite_discrepancies
    WHEN OLD.closed_at IS NOT NULL
    BEGIN SELECT RAISE(ABORT, 'a closed discrepancy never changes'); END""",
    """CREATE TRIGGER composite_discrepancies_no_delete BEFORE DELETE ON composite_discrepancies
    BEGIN SELECT RAISE(ABORT, 'discrepancies are kept'); END""",
    """CREATE TABLE composite_discrepancy_descriptors (
    discrepancy_id TEXT NOT NULL,
    discrepancy_kind TEXT NOT NULL CHECK (discrepancy_kind = 'descriptor'),
    descriptor TEXT NOT NULL,
    recorded_at INTEGER NOT NULL,
    PRIMARY KEY (discrepancy_id, descriptor),
    FOREIGN KEY (discrepancy_id, discrepancy_kind) REFERENCES composite_discrepancies (discrepancy_id, kind) ON DELETE RESTRICT
)""",
    """CREATE TRIGGER composite_discrepancy_descriptors_open_only BEFORE INSERT ON composite_discrepancy_descriptors
    WHEN EXISTS (SELECT 1 FROM composite_discrepancies WHERE discrepancy_id = NEW.discrepancy_id AND closed_at IS NOT NULL)
    BEGIN SELECT RAISE(ABORT, 'a closed discrepancy takes no descriptor'); END""",
    """CREATE TRIGGER composite_discrepancy_descriptors_no_update BEFORE UPDATE ON composite_discrepancy_descriptors
    BEGIN SELECT RAISE(ABORT, 'discrepancy descriptors are kept as recorded'); END""",
    """CREATE TRIGGER composite_discrepancy_descriptors_no_delete BEFORE DELETE ON composite_discrepancy_descriptors
    BEGIN SELECT RAISE(ABORT, 'discrepancy descriptors are kept as recorded'); END""",
    """CREATE TABLE composite_divergences (
    divergence_id TEXT PRIMARY KEY,
    sweep_id TEXT NOT NULL,
    physical_panel_id TEXT NOT NULL,
    child_id TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('state', 'reappeared', 'missing', 'identity')),
    observed_fields TEXT NOT NULL,
    desired_fields TEXT NOT NULL,
    detected_at INTEGER NOT NULL,
    repeat_count INTEGER NOT NULL CHECK (typeof(repeat_count) = 'integer' AND repeat_count >= 1),
    repair_work_id TEXT,
    repair_state TEXT NOT NULL CHECK (repair_state IN ('pending', 'repaired', 'failed', 'paused', 'not_repairable')),
    repaired_at INTEGER,
    discrepancy_id TEXT,
    exposure TEXT NOT NULL CHECK (exposure IN ('access_lost', 'access_gained', 'none')),
    exposure_from INTEGER,
    exposure_resolved_at INTEGER,
    CHECK (observed_fields != desired_fields),
    CHECK ((kind IN ('missing', 'identity')) = (repair_state = 'not_repairable')),
    CHECK (CASE repair_state
        WHEN 'repaired' THEN repair_work_id IS NOT NULL AND repaired_at IS NOT NULL AND repaired_at >= detected_at
        WHEN 'failed' THEN repair_work_id IS NOT NULL AND repaired_at IS NULL
        WHEN 'paused' THEN discrepancy_id IS NOT NULL AND repaired_at IS NULL
        WHEN 'not_repairable' THEN discrepancy_id IS NOT NULL AND repair_work_id IS NULL AND repaired_at IS NULL
        ELSE repaired_at IS NULL
    END),
    CHECK (CASE exposure
        WHEN 'none' THEN exposure_from IS NULL AND exposure_resolved_at IS NULL
        ELSE exposure_from IS NOT NULL AND exposure_from <= detected_at AND (exposure_resolved_at IS NULL OR exposure_resolved_at >= detected_at)
    END),
    FOREIGN KEY (sweep_id, physical_panel_id) REFERENCES composite_drift_sweeps (sweep_id, physical_panel_id) ON DELETE RESTRICT,
    FOREIGN KEY (child_id, physical_panel_id) REFERENCES composite_children (child_id, physical_panel_id) ON DELETE RESTRICT,
    FOREIGN KEY (repair_work_id, child_id) REFERENCES composite_remote_work (work_id, child_id) ON DELETE RESTRICT,
    FOREIGN KEY (discrepancy_id, child_id) REFERENCES composite_discrepancies (discrepancy_id, child_id) ON DELETE RESTRICT
)""",
    """CREATE TRIGGER composite_divergences_during_the_sweep BEFORE INSERT ON composite_divergences
    WHEN EXISTS (SELECT 1 FROM composite_drift_sweeps WHERE sweep_id = NEW.sweep_id AND outcome IS NOT NULL)
    BEGIN SELECT RAISE(ABORT, 'a finished sweep takes no divergence'); END""",
    """CREATE TRIGGER composite_divergences_evidence_fixed BEFORE UPDATE ON composite_divergences
    WHEN NEW.sweep_id IS NOT OLD.sweep_id OR NEW.physical_panel_id IS NOT OLD.physical_panel_id
        OR NEW.child_id IS NOT OLD.child_id OR NEW.kind IS NOT OLD.kind
        OR NEW.observed_fields IS NOT OLD.observed_fields OR NEW.desired_fields IS NOT OLD.desired_fields
        OR NEW.detected_at IS NOT OLD.detected_at OR NEW.repeat_count IS NOT OLD.repeat_count
        OR NEW.exposure IS NOT OLD.exposure OR NEW.exposure_from IS NOT OLD.exposure_from
    BEGIN SELECT RAISE(ABORT, 'divergence evidence never changes'); END""",
    """CREATE TRIGGER composite_divergences_outcome_final BEFORE UPDATE ON composite_divergences
    WHEN (OLD.repair_state IN ('repaired', 'failed', 'not_repairable') AND NEW.repair_state IS NOT OLD.repair_state)
        OR (OLD.repair_work_id IS NOT NULL AND NEW.repair_work_id IS NOT OLD.repair_work_id)
        OR (OLD.repaired_at IS NOT NULL AND NEW.repaired_at IS NOT OLD.repaired_at)
        OR (OLD.discrepancy_id IS NOT NULL AND NEW.discrepancy_id IS NOT OLD.discrepancy_id)
        OR (OLD.exposure_resolved_at IS NOT NULL AND NEW.exposure_resolved_at IS NOT OLD.exposure_resolved_at)
    BEGIN SELECT RAISE(ABORT, 'a divergence repair outcome never changes'); END""",
    """CREATE TRIGGER composite_divergences_kept_until_resolved BEFORE DELETE ON composite_divergences
    WHEN OLD.repair_state != 'repaired' OR (OLD.exposure != 'none' AND OLD.exposure_resolved_at IS NULL)
    BEGIN SELECT RAISE(ABORT, 'an unresolved divergence is kept'); END""",
)

# data-model.md §10: batch actions, their members and each move member's per-node mapping.
# composite_subscriptions_customer is the parent key of the member foreign key onto
# composite_subscriptions; composite_operations_subscription_kind (in _LIFECYCLE_DDL) is the
# parent key of the one onto composite_operations.
_BATCH_DDL = (
    "CREATE UNIQUE INDEX composite_subscriptions_customer ON composite_subscriptions (subscription_id, customer_telegram_id)",
    """CREATE TABLE composite_batches (
    batch_id TEXT PRIMARY KEY,
    action TEXT NOT NULL CHECK (action IN ('owner_suspend', 'owner_resume', 'cancellation', 'move', 'compensation')),
    preview_digest BLOB NOT NULL UNIQUE CHECK (typeof(preview_digest) = 'blob' AND length(preview_digest) = 32),
    actor TEXT NOT NULL,
    reason TEXT NOT NULL CHECK (reason <> ''),
    emergency INTEGER NOT NULL DEFAULT 0 CHECK (emergency IN (0, 1)),
    emergency_acceptance_ref TEXT,
    amount INTEGER CHECK (amount IS NULL OR (typeof(amount) = 'integer' AND amount > 0)),
    member_count INTEGER NOT NULL CHECK (typeof(member_count) = 'integer' AND member_count > 0),
    total_amount INTEGER,
    previewed_at INTEGER NOT NULL,
    authorized_at INTEGER CHECK (authorized_at IS NULL OR authorized_at >= previewed_at),
    CHECK ((emergency = 1) = (emergency_acceptance_ref IS NOT NULL)),
    CHECK (emergency = 0 OR action = 'move'),
    CHECK ((action = 'compensation') = (amount IS NOT NULL)),
    CHECK ((action = 'compensation') = (total_amount IS NOT NULL)),
    CHECK (total_amount IS NULL OR total_amount = amount * member_count),
    UNIQUE (batch_id, action),
    UNIQUE (batch_id, amount)
)""",
    """CREATE TRIGGER composite_batches_saved_unauthorized BEFORE INSERT ON composite_batches
    WHEN NEW.authorized_at IS NOT NULL
    BEGIN SELECT RAISE(ABORT, 'a batch is authorized only after its members are saved'); END""",
    """CREATE TRIGGER composite_batches_preview_fixed BEFORE UPDATE ON composite_batches
    WHEN NEW.batch_id IS NOT OLD.batch_id OR NEW.action IS NOT OLD.action OR NEW.preview_digest IS NOT OLD.preview_digest
        OR NEW.actor IS NOT OLD.actor OR NEW.reason IS NOT OLD.reason OR NEW.emergency IS NOT OLD.emergency
        OR NEW.emergency_acceptance_ref IS NOT OLD.emergency_acceptance_ref OR NEW.amount IS NOT OLD.amount
        OR NEW.member_count IS NOT OLD.member_count OR NEW.total_amount IS NOT OLD.total_amount
        OR NEW.previewed_at IS NOT OLD.previewed_at
        OR (OLD.authorized_at IS NOT NULL AND NEW.authorized_at IS NOT OLD.authorized_at)
    BEGIN SELECT RAISE(ABORT, 'a batch preview is immutable and its authorization final'); END""",
    """CREATE TRIGGER composite_batches_authorize_exact BEFORE UPDATE OF authorized_at ON composite_batches
    WHEN OLD.authorized_at IS NULL AND NEW.authorized_at IS NOT NULL AND (
        (SELECT count(*) FROM composite_batch_members WHERE batch_id = NEW.batch_id) <> NEW.member_count
        OR EXISTS (SELECT 1 FROM composite_batch_members m WHERE m.batch_id = NEW.batch_id AND m.action = 'move'
            AND NOT EXISTS (SELECT 1 FROM composite_batch_member_nodes n WHERE n.member_id = m.member_id)))
    BEGIN SELECT RAISE(ABORT, 'authorization needs exactly the previewed members and mapping'); END""",
    """CREATE TRIGGER composite_batches_kept BEFORE DELETE ON composite_batches
    WHEN OLD.authorized_at IS NOT NULL
    BEGIN SELECT RAISE(ABORT, 'an authorized batch is kept'); END""",
    """CREATE TABLE composite_batch_members (
    member_id TEXT PRIMARY KEY,
    batch_id TEXT NOT NULL,
    action TEXT NOT NULL,
    subscription_id TEXT,
    customer_telegram_id INTEGER NOT NULL,
    subscription_context TEXT,
    amount INTEGER,
    obligation_kind TEXT CHECK (obligation_kind IS NULL OR obligation_kind = 'support_compensation'),
    operation_id TEXT,
    obligation_id TEXT UNIQUE,
    result TEXT NOT NULL DEFAULT 'pending' CHECK (result IN ('pending', 'succeeded', 'failed')),
    finished_at INTEGER,
    failure_reason TEXT,
    CHECK ((action = 'compensation') = (subscription_id IS NULL)),
    CHECK ((action = 'compensation') = (amount IS NOT NULL)),
    CHECK ((action = 'compensation') = (obligation_kind IS NOT NULL)),
    CHECK (action = 'compensation' OR (obligation_id IS NULL AND subscription_context IS NULL)),
    CHECK (action <> 'compensation' OR operation_id IS NULL),
    CHECK ((result = 'pending') = (finished_at IS NULL)),
    CHECK ((result = 'failed') = (failure_reason IS NOT NULL)),
    CHECK (result = 'pending' OR operation_id IS NOT NULL OR obligation_id IS NOT NULL),
    UNIQUE (batch_id, subscription_id),
    UNIQUE (member_id, action, subscription_id),
    FOREIGN KEY (batch_id, action) REFERENCES composite_batches (batch_id, action) ON DELETE RESTRICT,
    FOREIGN KEY (batch_id, amount) REFERENCES composite_batches (batch_id, amount) ON DELETE RESTRICT,
    FOREIGN KEY (subscription_id, customer_telegram_id) REFERENCES composite_subscriptions (subscription_id, customer_telegram_id) ON DELETE RESTRICT,
    FOREIGN KEY (operation_id, subscription_id, action) REFERENCES composite_operations (operation_id, subscription_id, kind) ON DELETE RESTRICT,
    FOREIGN KEY (obligation_id, customer_telegram_id, obligation_kind, amount) REFERENCES financial_obligations (obligation_id, beneficiary_telegram_id, kind, amount) ON DELETE RESTRICT
)""",
    "CREATE UNIQUE INDEX composite_batch_members_one_credit ON composite_batch_members (batch_id, customer_telegram_id) WHERE action = 'compensation'",
    """CREATE TRIGGER composite_batch_members_saved_with_preview BEFORE INSERT ON composite_batch_members
    WHEN NEW.operation_id IS NOT NULL OR NEW.obligation_id IS NOT NULL
        OR EXISTS (SELECT 1 FROM composite_batches WHERE batch_id = NEW.batch_id AND authorized_at IS NOT NULL)
    BEGIN SELECT RAISE(ABORT, 'members are saved with the preview, before any effect'); END""",
    """CREATE TRIGGER composite_batch_members_effects_after_authorization BEFORE UPDATE OF operation_id, obligation_id ON composite_batch_members
    WHEN (NEW.operation_id IS NOT OLD.operation_id OR NEW.obligation_id IS NOT OLD.obligation_id)
        AND NOT EXISTS (SELECT 1 FROM composite_batches WHERE batch_id = NEW.batch_id AND authorized_at IS NOT NULL)
    BEGIN SELECT RAISE(ABORT, 'a preview has no effects'); END""",
    """CREATE TRIGGER composite_batch_members_fixed BEFORE UPDATE ON composite_batch_members
    WHEN NEW.member_id IS NOT OLD.member_id OR NEW.batch_id IS NOT OLD.batch_id OR NEW.action IS NOT OLD.action
        OR NEW.subscription_id IS NOT OLD.subscription_id OR NEW.customer_telegram_id IS NOT OLD.customer_telegram_id
        OR NEW.subscription_context IS NOT OLD.subscription_context OR NEW.amount IS NOT OLD.amount
        OR NEW.obligation_kind IS NOT OLD.obligation_kind
        OR (OLD.operation_id IS NOT NULL AND NEW.operation_id IS NOT OLD.operation_id)
        OR (OLD.obligation_id IS NOT NULL AND NEW.obligation_id IS NOT OLD.obligation_id)
        OR (OLD.result <> 'pending' AND (NEW.result IS NOT OLD.result OR NEW.finished_at IS NOT OLD.finished_at
            OR NEW.failure_reason IS NOT OLD.failure_reason))
    BEGIN SELECT RAISE(ABORT, 'member identity is fixed and a finished member stays finished'); END""",
    """CREATE TRIGGER composite_batch_members_kept BEFORE DELETE ON composite_batch_members
    WHEN EXISTS (SELECT 1 FROM composite_batches WHERE batch_id = OLD.batch_id AND authorized_at IS NOT NULL)
    BEGIN SELECT RAISE(ABORT, 'members of an authorized batch are kept'); END""",
    """CREATE TABLE composite_batch_member_nodes (
    member_id TEXT NOT NULL,
    member_action TEXT NOT NULL CHECK (member_action = 'move'),
    subscription_id TEXT NOT NULL,
    logical_node_key TEXT NOT NULL,
    target_binding_id TEXT NOT NULL REFERENCES composite_prepared_bindings (binding_id) ON DELETE RESTRICT,
    target_descriptor TEXT NOT NULL,
    owner_pick TEXT,
    read_at INTEGER NOT NULL,
    PRIMARY KEY (member_id, logical_node_key),
    FOREIGN KEY (member_id, member_action, subscription_id) REFERENCES composite_batch_members (member_id, action, subscription_id) ON DELETE RESTRICT,
    FOREIGN KEY (subscription_id, logical_node_key) REFERENCES composite_subscription_nodes (subscription_id, logical_node_key) ON DELETE RESTRICT
)""",
    """CREATE TRIGGER composite_batch_member_nodes_read_at_preview BEFORE INSERT ON composite_batch_member_nodes
    WHEN EXISTS (SELECT 1 FROM composite_batch_members m JOIN composite_batches b ON b.batch_id = m.batch_id
        WHERE m.member_id = NEW.member_id AND (b.authorized_at IS NOT NULL OR NEW.read_at > b.previewed_at))
    BEGIN SELECT RAISE(ABORT, 'the mapping is read at preview and fixed by authorization'); END""",
    """CREATE TRIGGER composite_batch_member_nodes_fixed BEFORE UPDATE ON composite_batch_member_nodes
    BEGIN SELECT RAISE(ABORT, 'a previewed mapping never changes'); END""",
    """CREATE TRIGGER composite_batch_member_nodes_kept BEFORE DELETE ON composite_batch_member_nodes
    WHEN EXISTS (SELECT 1 FROM composite_batch_members m JOIN composite_batches b ON b.batch_id = m.batch_id
        WHERE m.member_id = OLD.member_id AND b.authorized_at IS NOT NULL)
    BEGIN SELECT RAISE(ABORT, 'the mapping of an authorized batch is kept'); END""",
)

# data-model.md §10: audit events and outbound notifications.
# composite_reminders_due is the parent key of the notification foreign key onto
# composite_reminders (reminder_id, original_due_at); composite_subscriptions_customer
# (in _BATCH_DDL) is the parent key of the one onto composite_subscriptions.
_NOTICE_DDL = (
    "CREATE UNIQUE INDEX composite_reminders_due ON composite_reminders (reminder_id, due_at)",
    """CREATE TABLE composite_audit_events (
    event_id TEXT PRIMARY KEY,
    occurred_at INTEGER NOT NULL,
    actor_domain TEXT NOT NULL CHECK (actor_domain IN ('telegram', 'web_admin', 'payment_callback', 'system', 'cli')),
    actor_id TEXT NOT NULL CHECK (actor_id <> ''),
    action TEXT NOT NULL CHECK (action <> ''),
    resource_kind TEXT NOT NULL CHECK (resource_kind <> ''),
    resource_id TEXT NOT NULL CHECK (resource_id <> ''),
    reason TEXT CHECK (reason IS NULL OR reason <> ''),
    evidence_ref TEXT,
    diagnostics TEXT
)""",
    """CREATE TRIGGER composite_audit_events_no_update BEFORE UPDATE ON composite_audit_events
    BEGIN SELECT RAISE(ABORT, 'audit events are immutable'); END""",
    """CREATE TRIGGER composite_audit_events_no_delete BEFORE DELETE ON composite_audit_events
    BEGIN SELECT RAISE(ABORT, 'audit events are kept'); END""",
    """CREATE TABLE composite_notifications (
    notification_id TEXT PRIMARY KEY,
    notice_key TEXT NOT NULL CHECK (notice_key <> ''),
    recipient_telegram_id INTEGER NOT NULL CHECK (typeof(recipient_telegram_id) = 'integer' AND recipient_telegram_id > 0),
    kind TEXT NOT NULL CHECK (kind IN ('fulfillment', 'failure', 'support', 'replacement', 'move', 'owner_alert', 'reminder')),
    subscription_id TEXT,
    reminder_id TEXT UNIQUE,
    operation_id TEXT REFERENCES composite_operations (operation_id) ON DELETE RESTRICT,
    escalation_ref TEXT,
    policy_version TEXT NOT NULL CHECK (policy_version <> ''),
    original_due_at INTEGER NOT NULL,
    original_target_at INTEGER NOT NULL,
    original_missed_at INTEGER,
    status TEXT NOT NULL CHECK (status IN ('waiting_eligibility', 'waiting_transport', 'waiting_opportunity', 'sending', 'uncertain_delivery', 'accepted', 'permanent_failure', 'exhausted', 'obsolete')),
    block_reason TEXT,
    next_opportunity_at INTEGER,
    next_attempt_at INTEGER,
    attempts_used INTEGER NOT NULL DEFAULT 0 CHECK (typeof(attempts_used) = 'integer' AND attempts_used BETWEEN 0 AND 5),
    uncertain_since INTEGER,
    nonacceptance_ref TEXT,
    accepted_at INTEGER,
    acceptance_ref TEXT,
    stop_reason TEXT,
    CHECK ((kind = 'reminder') = (reminder_id IS NOT NULL)),
    CHECK (kind <> 'reminder' OR subscription_id IS NOT NULL),
    CHECK ((kind = 'owner_alert') = (escalation_ref IS NOT NULL)),
    CHECK (kind <> 'owner_alert' OR subscription_id IS NULL),
    CHECK (original_target_at = original_due_at + 300000),
    CHECK (original_missed_at IS NULL OR original_missed_at >= original_target_at),
    CHECK ((status IN ('waiting_eligibility', 'waiting_transport')) = (block_reason IS NOT NULL)),
    CHECK ((status = 'waiting_opportunity') = (next_opportunity_at IS NOT NULL)),
    CHECK (status NOT IN ('waiting_eligibility', 'waiting_transport', 'waiting_opportunity') OR attempts_used < 5),
    CHECK ((status = 'uncertain_delivery') = (uncertain_since IS NOT NULL)),
    CHECK ((status = 'accepted') = (accepted_at IS NOT NULL)),
    CHECK ((accepted_at IS NULL) = (acceptance_ref IS NULL)),
    CHECK (accepted_at IS NULL OR accepted_at >= original_due_at),
    CHECK (original_missed_at IS NULL OR accepted_at IS NULL OR accepted_at > original_target_at),
    CHECK (accepted_at IS NULL OR accepted_at <= original_target_at OR original_missed_at IS NOT NULL),
    CHECK ((status IN ('permanent_failure', 'exhausted', 'obsolete')) = (stop_reason IS NOT NULL)),
    CHECK (status <> 'exhausted' OR attempts_used = 5),
    UNIQUE (notice_key, recipient_telegram_id),
    FOREIGN KEY (subscription_id, recipient_telegram_id) REFERENCES composite_subscriptions (subscription_id, customer_telegram_id) ON DELETE RESTRICT,
    FOREIGN KEY (reminder_id, original_due_at) REFERENCES composite_reminders (reminder_id, due_at) ON DELETE RESTRICT
)""",
    """CREATE TRIGGER composite_notifications_saved_unsent BEFORE INSERT ON composite_notifications
    WHEN NEW.status NOT IN ('waiting_eligibility', 'waiting_transport', 'sending') OR NEW.attempts_used IS NOT 0
    BEGIN SELECT RAISE(ABORT, 'a notice is saved known-unsent with no attempt used'); END""",
    """CREATE TRIGGER composite_notifications_identity_fixed BEFORE UPDATE ON composite_notifications
    WHEN NEW.notification_id IS NOT OLD.notification_id OR NEW.notice_key IS NOT OLD.notice_key
        OR NEW.recipient_telegram_id IS NOT OLD.recipient_telegram_id OR NEW.kind IS NOT OLD.kind
        OR NEW.subscription_id IS NOT OLD.subscription_id OR NEW.reminder_id IS NOT OLD.reminder_id
        OR NEW.operation_id IS NOT OLD.operation_id OR NEW.escalation_ref IS NOT OLD.escalation_ref
        OR NEW.policy_version IS NOT OLD.policy_version OR NEW.original_due_at IS NOT OLD.original_due_at
        OR NEW.original_target_at IS NOT OLD.original_target_at
        OR (OLD.original_missed_at IS NOT NULL AND NEW.original_missed_at IS NOT OLD.original_missed_at)
    BEGIN SELECT RAISE(ABORT, 'a notice identity and its original clocks are immutable'); END""",
    """CREATE TRIGGER composite_notifications_final BEFORE UPDATE ON composite_notifications
    WHEN OLD.status IN ('accepted', 'obsolete')
    BEGIN SELECT RAISE(ABORT, 'an accepted or obsolete notice never rearms'); END""",
    """CREATE TRIGGER composite_notifications_uncertain_held BEFORE UPDATE OF status ON composite_notifications
    WHEN OLD.status = 'uncertain_delivery' AND NEW.status NOT IN ('uncertain_delivery', 'accepted')
        AND (NEW.nonacceptance_ref IS NULL OR NEW.nonacceptance_ref IS OLD.nonacceptance_ref)
    BEGIN SELECT RAISE(ABORT, 'an uncertain send leaves uncertainty only on new nonacceptance evidence'); END""",
    """CREATE TRIGGER composite_notifications_attempts_reserved BEFORE UPDATE OF attempts_used ON composite_notifications
    WHEN NEW.attempts_used IS NOT OLD.attempts_used AND NEW.attempts_used IS NOT OLD.attempts_used + 1
    BEGIN SELECT RAISE(ABORT, 'attempts are reserved one at a time and never returned'); END""",
    """CREATE TRIGGER composite_notifications_backoff_kept BEFORE UPDATE OF next_attempt_at ON composite_notifications
    WHEN OLD.next_attempt_at IS NOT NULL AND (NEW.next_attempt_at IS NULL OR NEW.next_attempt_at < OLD.next_attempt_at)
    BEGIN SELECT RAISE(ABORT, 'a persisted backoff is never shortened'); END""",
    """CREATE TRIGGER composite_notifications_no_delete BEFORE DELETE ON composite_notifications
    BEGIN SELECT RAISE(ABORT, 'notifications are kept'); END""",
)

# data-model.md §10: notification delivery opportunities (the 300-second windows,
# automatic, reconciliation and owner-approved) and the send/lookup attempts made
# in them. The attempt foreign key uses the opportunities UNIQUE
# (opportunity_id, notification_id); both tables refer to _NOTICE_DDL tables.
_DELIVERY_DDL = (
    """CREATE TABLE composite_notification_opportunities (
    opportunity_id TEXT PRIMARY KEY,
    notification_id TEXT NOT NULL REFERENCES composite_notifications (notification_id) ON DELETE RESTRICT,
    reason TEXT NOT NULL CHECK (reason IN ('original_due', 'unblocked', 'processing_resumed', 'retry_due', 'window_replaced', 'reconciliation', 'owner_recovery', 'owner_duplicate_risk')),
    audit_event_id TEXT UNIQUE REFERENCES composite_audit_events (event_id) ON DELETE RESTRICT,
    event_at INTEGER NOT NULL,
    detected_at INTEGER NOT NULL,
    ends_at INTEGER NOT NULL,
    closed_at INTEGER,
    close_reason TEXT CHECK (close_reason IN ('expired', 'blocked', 'accepted', 'uncertain', 'resolved', 'stopped')),
    CHECK ((reason IN ('owner_recovery', 'owner_duplicate_risk')) = (audit_event_id IS NOT NULL)),
    CHECK (detected_at >= event_at),
    CHECK (ends_at = event_at + 300000),
    CHECK ((closed_at IS NULL) = (close_reason IS NULL)),
    CHECK (closed_at IS NULL OR closed_at >= detected_at),
    CHECK (close_reason IS NULL OR (close_reason = 'expired') = (closed_at >= ends_at)),
    UNIQUE (opportunity_id, notification_id)
)""",
    "CREATE UNIQUE INDEX composite_notification_opportunities_open ON composite_notification_opportunities (notification_id) WHERE closed_at IS NULL",
    "CREATE UNIQUE INDEX composite_notification_opportunities_initial ON composite_notification_opportunities (notification_id) WHERE reason = 'original_due'",
    """CREATE TRIGGER composite_notification_opportunities_allowed BEFORE INSERT ON composite_notification_opportunities
    WHEN EXISTS (SELECT 1 FROM composite_notifications n WHERE n.notification_id = NEW.notification_id AND (
        NEW.event_at < n.original_due_at
        OR (NEW.reason IN ('original_due', 'unblocked', 'processing_resumed', 'retry_due', 'window_replaced') AND (n.status NOT IN ('waiting_eligibility', 'waiting_transport', 'waiting_opportunity', 'sending') OR n.attempts_used >= 5))
        OR (NEW.reason = 'reconciliation' AND (n.status <> 'uncertain_delivery' OR n.attempts_used >= 5))
        OR (NEW.reason = 'owner_recovery' AND n.status NOT IN ('exhausted', 'permanent_failure'))
        OR (NEW.reason = 'owner_duplicate_risk' AND n.status <> 'uncertain_delivery')
        OR (NEW.reason = 'original_due' AND NEW.event_at <> n.original_due_at)
        OR (NEW.reason = 'retry_due' AND NEW.event_at IS NOT NULL AND NEW.event_at IS NOT n.next_attempt_at)
        OR (NEW.reason = 'window_replaced' AND NEW.event_at IS NOT NULL AND NEW.event_at IS NOT n.next_opportunity_at)))
    OR EXISTS (SELECT 1 FROM composite_audit_events e WHERE e.event_id = NEW.audit_event_id
        AND (e.resource_kind <> 'composite_notifications' OR e.resource_id IS NOT NEW.notification_id))
    BEGIN SELECT RAISE(ABORT, 'a delivery opportunity opens only for its notice state, time and owner action'); END""",
    """CREATE TRIGGER composite_notification_opportunities_fixed BEFORE UPDATE ON composite_notification_opportunities
    WHEN OLD.closed_at IS NOT NULL
        OR NEW.opportunity_id IS NOT OLD.opportunity_id OR NEW.notification_id IS NOT OLD.notification_id
        OR NEW.reason IS NOT OLD.reason OR NEW.audit_event_id IS NOT OLD.audit_event_id
        OR NEW.event_at IS NOT OLD.event_at OR NEW.detected_at IS NOT OLD.detected_at OR NEW.ends_at IS NOT OLD.ends_at
    BEGIN SELECT RAISE(ABORT, 'an opportunity keeps its identity and closes once'); END""",
    """CREATE TRIGGER composite_notification_opportunities_no_delete BEFORE DELETE ON composite_notification_opportunities
    BEGIN SELECT RAISE(ABORT, 'opportunities are kept'); END""",
    """CREATE TABLE composite_notification_attempts (
    attempt_id TEXT PRIMARY KEY,
    notification_id TEXT NOT NULL,
    opportunity_id TEXT NOT NULL,
    allowance TEXT NOT NULL CHECK (allowance IN ('automatic', 'manual')),
    attempt_number INTEGER NOT NULL CHECK (attempt_number BETWEEN 1 AND CASE WHEN allowance = 'manual' THEN 2 ELSE 5 END),
    call_kind TEXT NOT NULL CHECK (call_kind IN ('send', 'lookup')),
    reserved_at INTEGER NOT NULL,
    dispatched_at INTEGER,
    finished_at INTEGER,
    outcome TEXT CHECK (outcome IN ('no_send', 'accepted', 'rejected', 'uncertain', 'not_accepted')),
    evidence_ref TEXT,
    CHECK ((finished_at IS NULL) = (outcome IS NULL)),
    CHECK (dispatched_at IS NULL OR dispatched_at >= reserved_at),
    CHECK (finished_at IS NULL OR finished_at >= reserved_at),
    CHECK (finished_at IS NULL OR dispatched_at IS NULL OR finished_at >= dispatched_at),
    CHECK (outcome NOT IN ('accepted', 'rejected', 'not_accepted') OR dispatched_at IS NOT NULL),
    CHECK (outcome <> 'rejected' OR call_kind = 'send'),
    CHECK (outcome <> 'not_accepted' OR call_kind = 'lookup'),
    CHECK ((outcome IS NOT NULL AND outcome IN ('accepted', 'not_accepted')) = (evidence_ref IS NOT NULL)),
    FOREIGN KEY (opportunity_id, notification_id) REFERENCES composite_notification_opportunities (opportunity_id, notification_id) ON DELETE RESTRICT
)""",
    "CREATE UNIQUE INDEX composite_notification_attempts_automatic ON composite_notification_attempts (notification_id, attempt_number) WHERE allowance = 'automatic'",
    "CREATE UNIQUE INDEX composite_notification_attempts_in_flight ON composite_notification_attempts (notification_id) WHERE outcome IS NULL",
    """CREATE TRIGGER composite_notification_attempts_allowed BEFORE INSERT ON composite_notification_attempts
    WHEN EXISTS (SELECT 1 FROM composite_notification_opportunities o JOIN composite_notifications n ON n.notification_id = NEW.notification_id
        WHERE o.opportunity_id = NEW.opportunity_id AND (
            o.closed_at IS NOT NULL OR NEW.reserved_at < o.detected_at OR NEW.reserved_at >= o.ends_at
            OR (o.reason IN ('owner_recovery', 'owner_duplicate_risk')) <> (NEW.allowance = 'manual')
            OR (o.reason = 'reconciliation') <> (NEW.call_kind = 'lookup')
            OR n.status <> CASE WHEN o.reason IN ('reconciliation', 'owner_duplicate_risk') THEN 'uncertain_delivery' ELSE 'sending' END
            OR (NEW.allowance = 'automatic' AND (NEW.attempt_number <> n.attempts_used OR NEW.reserved_at < n.next_attempt_at))
            OR (NEW.allowance = 'manual' AND (
                NEW.attempt_number <> 1 + (SELECT count(*) FROM composite_notification_attempts p WHERE p.opportunity_id = NEW.opportunity_id)
                OR (NEW.attempt_number = 2 AND NOT EXISTS (SELECT 1 FROM composite_notification_attempts p
                    WHERE p.opportunity_id = NEW.opportunity_id AND p.attempt_number = 1 AND p.outcome = 'no_send' AND NEW.reserved_at >= p.finished_at + 30000))))))
    BEGIN SELECT RAISE(ABORT, 'an attempt is reserved in an open window of its kind, in order and after its backoff'); END""",
    """CREATE TRIGGER composite_notification_attempts_fixed BEFORE UPDATE ON composite_notification_attempts
    WHEN OLD.outcome IS NOT NULL
        OR NEW.attempt_id IS NOT OLD.attempt_id OR NEW.notification_id IS NOT OLD.notification_id
        OR NEW.opportunity_id IS NOT OLD.opportunity_id OR NEW.allowance IS NOT OLD.allowance
        OR NEW.attempt_number IS NOT OLD.attempt_number OR NEW.call_kind IS NOT OLD.call_kind
        OR NEW.reserved_at IS NOT OLD.reserved_at
        OR (OLD.dispatched_at IS NOT NULL AND NEW.dispatched_at IS NOT OLD.dispatched_at)
    BEGIN SELECT RAISE(ABORT, 'an attempt keeps its identity, dispatch time and outcome'); END""",
    """CREATE TRIGGER composite_notification_attempts_no_delete BEFORE DELETE ON composite_notification_attempts
    BEGIN SELECT RAISE(ABORT, 'attempts are kept'); END""",
)

# data-model.md §11: the installation's one processing-control row (installation
# identity, admission mode, operation generation, restore epoch, worker
# incarnation and the composite issuance switch). migrate creates the table
# empty; the row is written later from the external protected control file.
_CONTROL_DDL = (
    """CREATE TABLE composite_processing_control (
    control_id INTEGER PRIMARY KEY CHECK (control_id = 1),
    installation_id TEXT NOT NULL,
    restore_epoch INTEGER NOT NULL DEFAULT 0 CHECK (restore_epoch >= 0),
    operation_generation INTEGER NOT NULL DEFAULT 0 CHECK (operation_generation >= 0),
    admission_mode TEXT NOT NULL CHECK (admission_mode IN ('open', 'maintenance')),
    maintenance_reason TEXT,
    mode_changed_at INTEGER NOT NULL,
    worker_incarnation TEXT,
    worker_epoch INTEGER,
    issuance_enabled INTEGER NOT NULL DEFAULT 0 CHECK (issuance_enabled IN (0, 1)),
    CHECK ((admission_mode = 'maintenance') = (maintenance_reason IS NOT NULL)),
    CHECK ((worker_incarnation IS NULL) = (worker_epoch IS NULL))
)""",
    """CREATE TRIGGER composite_processing_control_starts_clean
BEFORE INSERT ON composite_processing_control
WHEN NEW.worker_incarnation IS NOT NULL OR NEW.worker_epoch IS NOT NULL OR NEW.issuance_enabled = 1
BEGIN SELECT RAISE(ABORT, 'processing control starts with no worker and issuance off'); END""",
    """CREATE TRIGGER composite_processing_control_kept
BEFORE DELETE ON composite_processing_control
BEGIN SELECT RAISE(ABORT, 'processing control is never deleted'); END""",
    """CREATE TRIGGER composite_processing_control_installation
BEFORE UPDATE ON composite_processing_control
WHEN NEW.installation_id IS NOT OLD.installation_id
BEGIN SELECT RAISE(ABORT, 'installation identity never changes'); END""",
    """CREATE TRIGGER composite_processing_control_generation
BEFORE UPDATE ON composite_processing_control
WHEN (OLD.admission_mode <> 'maintenance' AND NEW.admission_mode = 'maintenance' AND NEW.operation_generation IS NOT OLD.operation_generation + 1)
  OR (NOT (OLD.admission_mode <> 'maintenance' AND NEW.admission_mode = 'maintenance') AND NEW.operation_generation IS NOT OLD.operation_generation)
BEGIN SELECT RAISE(ABORT, 'operation generation rises by one exactly when maintenance begins'); END""",
    """CREATE TRIGGER composite_processing_control_mode_clock
BEFORE UPDATE ON composite_processing_control
WHEN (NEW.admission_mode IS NOT OLD.admission_mode AND NEW.mode_changed_at <= OLD.mode_changed_at)
  OR (NEW.admission_mode IS OLD.admission_mode AND NEW.mode_changed_at IS NOT OLD.mode_changed_at)
BEGIN SELECT RAISE(ABORT, 'mode_changed_at moves forward exactly when the admission mode changes'); END""",
    """CREATE TRIGGER composite_processing_control_epoch
BEFORE UPDATE ON composite_processing_control
WHEN NEW.restore_epoch IS NOT OLD.restore_epoch
 AND (NEW.restore_epoch < OLD.restore_epoch OR OLD.admission_mode <> 'maintenance' OR NEW.admission_mode <> 'maintenance')
BEGIN SELECT RAISE(ABORT, 'the restore epoch only rises, and only during maintenance'); END""",
    """CREATE TRIGGER composite_processing_control_worker_epoch
BEFORE UPDATE ON composite_processing_control
WHEN NEW.worker_epoch IS NOT OLD.worker_epoch AND NEW.worker_incarnation IS OLD.worker_incarnation
BEGIN SELECT RAISE(ABORT, 'a worker incarnation never acknowledges another epoch'); END""",
    """CREATE TRIGGER composite_processing_control_worker_registration
BEFORE UPDATE ON composite_processing_control
WHEN NEW.worker_incarnation IS NOT NULL AND NEW.worker_incarnation IS NOT OLD.worker_incarnation
 AND (NEW.admission_mode <> 'open' OR NEW.worker_epoch IS NOT NEW.restore_epoch)
BEGIN SELECT RAISE(ABORT, 'a new worker registers while admission is open, at the current restore epoch'); END""",
)

# data-model.md §11: validated recovery points and their B-01 delivery attempts.
# Each point starts delivering, unverified, with a deadline derived from its
# predecessor; attempts are reserved before work, keep their path and outcome,
# and a verified attempt must read back the validated archive. Both are kept.
_RECOVERY_DDL = (
    """CREATE TABLE composite_recovery_points (
    recovery_point_id TEXT PRIMARY KEY,
    installation_id TEXT NOT NULL CHECK (installation_id <> ''),
    restore_epoch INTEGER NOT NULL CHECK (typeof(restore_epoch) = 'integer' AND restore_epoch >= 0),
    captured_at INTEGER NOT NULL,
    schema_version INTEGER NOT NULL CHECK (typeof(schema_version) = 'integer' AND schema_version >= 1),
    release TEXT NOT NULL CHECK (release <> ''),
    runtime_inventory TEXT NOT NULL CHECK (runtime_inventory <> ''),
    manifest TEXT NOT NULL CHECK (manifest <> ''),
    manifest_sha256 BLOB NOT NULL CHECK (typeof(manifest_sha256) = 'blob' AND length(manifest_sha256) = 32),
    archive_ref TEXT NOT NULL CHECK (archive_ref <> ''),
    archive_sha256 BLOB NOT NULL CHECK (typeof(archive_sha256) = 'blob' AND length(archive_sha256) = 32),
    archive_bytes INTEGER NOT NULL CHECK (typeof(archive_bytes) = 'integer' AND archive_bytes > 0),
    encryption_key_id TEXT NOT NULL CHECK (encryption_key_id <> ''),
    validation_report TEXT NOT NULL CHECK (validation_report <> ''),
    validated_at INTEGER NOT NULL,
    destination_id TEXT NOT NULL CHECK (destination_id <> ''),
    policy_version TEXT NOT NULL CHECK (policy_version <> ''),
    predecessor_point_id TEXT REFERENCES composite_recovery_points (recovery_point_id) ON DELETE RESTRICT,
    delivery_deadline INTEGER NOT NULL,
    delivery_state TEXT NOT NULL DEFAULT 'delivering' CHECK (delivery_state IN ('delivering', 'verified', 'exhausted', 'stopped')),
    delivery_closed_at INTEGER,
    verified_at INTEGER,
    verified_attempt_id TEXT,
    age_target_missed_at INTEGER,
    CHECK (validated_at >= captured_at),
    CHECK ((delivery_state = 'delivering') = (delivery_closed_at IS NULL)),
    CHECK (delivery_closed_at IS NULL OR delivery_closed_at >= validated_at),
    CHECK ((verified_at IS NULL) = (verified_attempt_id IS NULL)),
    CHECK (verified_at IS NULL OR delivery_state <> 'delivering'),
    CHECK (delivery_state <> 'verified' OR verified_at IS NOT NULL),
    CHECK (age_target_missed_at IS NULL OR (verified_at IS NOT NULL AND age_target_missed_at >= verified_at AND age_target_missed_at >= captured_at + 900000)),
    FOREIGN KEY (verified_attempt_id, recovery_point_id) REFERENCES composite_recovery_delivery_attempts (attempt_id, recovery_point_id) ON DELETE RESTRICT
)""",
    """CREATE TRIGGER composite_recovery_points_captured BEFORE INSERT ON composite_recovery_points
    WHEN NEW.delivery_state IS NOT 'delivering' OR NEW.verified_at IS NOT NULL OR NEW.verified_attempt_id IS NOT NULL OR NEW.age_target_missed_at IS NOT NULL
        OR (NEW.predecessor_point_id IS NULL AND EXISTS (SELECT 1 FROM composite_recovery_points q WHERE q.verified_at <= NEW.captured_at))
        OR EXISTS (SELECT 1 FROM composite_recovery_points p WHERE p.recovery_point_id = NEW.predecessor_point_id AND (
            p.verified_at IS NULL OR p.verified_at > NEW.captured_at
            OR EXISTS (SELECT 1 FROM composite_recovery_points q WHERE q.verified_at <= NEW.captured_at AND q.captured_at > p.captured_at)))
        OR NEW.delivery_deadline IS NOT COALESCE(
            (SELECT min(NEW.captured_at + 600000, p.captured_at + 900000) FROM composite_recovery_points p
             WHERE p.recovery_point_id = NEW.predecessor_point_id AND p.captured_at + 900000 > NEW.captured_at),
            NEW.captured_at + 600000)
    BEGIN SELECT RAISE(ABORT, 'a recovery point starts delivering, unverified, with its predecessor and B-01 deadline'); END""",
    """CREATE TRIGGER composite_recovery_points_fixed BEFORE UPDATE ON composite_recovery_points
    WHEN (NEW.recovery_point_id IS NOT OLD.recovery_point_id OR NEW.installation_id IS NOT OLD.installation_id OR
        NEW.restore_epoch IS NOT OLD.restore_epoch OR NEW.captured_at IS NOT OLD.captured_at OR
        NEW.schema_version IS NOT OLD.schema_version OR NEW.release IS NOT OLD.release OR
        NEW.runtime_inventory IS NOT OLD.runtime_inventory OR NEW.manifest IS NOT OLD.manifest OR
        NEW.manifest_sha256 IS NOT OLD.manifest_sha256 OR NEW.archive_ref IS NOT OLD.archive_ref OR
        NEW.archive_sha256 IS NOT OLD.archive_sha256 OR NEW.archive_bytes IS NOT OLD.archive_bytes OR
        NEW.encryption_key_id IS NOT OLD.encryption_key_id OR
        NEW.validation_report IS NOT OLD.validation_report OR NEW.validated_at IS NOT OLD.validated_at OR
        NEW.destination_id IS NOT OLD.destination_id OR NEW.policy_version IS NOT OLD.policy_version OR
        NEW.predecessor_point_id IS NOT OLD.predecessor_point_id OR
        NEW.delivery_deadline IS NOT OLD.delivery_deadline)
        OR (OLD.delivery_state <> 'delivering' AND (NEW.delivery_state IS NOT OLD.delivery_state OR NEW.delivery_closed_at IS NOT OLD.delivery_closed_at))
        OR (OLD.verified_at IS NOT NULL AND (NEW.verified_at IS NOT OLD.verified_at OR NEW.verified_attempt_id IS NOT OLD.verified_attempt_id))
        OR (OLD.age_target_missed_at IS NOT NULL AND NEW.age_target_missed_at IS NOT OLD.age_target_missed_at)
    BEGIN SELECT RAISE(ABORT, 'a recovery point keeps its capture, deadline and recorded outcomes'); END""",
    """CREATE TRIGGER composite_recovery_points_closed BEFORE UPDATE ON composite_recovery_points
    WHEN OLD.delivery_state = 'delivering' AND NEW.delivery_state IS NOT 'delivering' AND (
        EXISTS (SELECT 1 FROM composite_recovery_delivery_attempts a WHERE a.recovery_point_id = OLD.recovery_point_id AND a.outcome IS NULL)
        OR (NEW.delivery_state IN ('exhausted', 'stopped') AND EXISTS (SELECT 1 FROM composite_recovery_delivery_attempts a WHERE a.recovery_point_id = OLD.recovery_point_id AND a.outcome = 'verified'))
        OR (NEW.delivery_state = 'exhausted' AND NEW.delivery_closed_at < OLD.delivery_deadline
            AND NOT EXISTS (SELECT 1 FROM composite_recovery_delivery_attempts a WHERE a.recovery_point_id = OLD.recovery_point_id AND a.allowance = 'automatic' AND a.attempt_number = 3))
        OR (NEW.delivery_state = 'stopped'
            AND NOT EXISTS (SELECT 1 FROM composite_recovery_delivery_attempts a WHERE a.recovery_point_id = OLD.recovery_point_id AND a.allowance = 'automatic' AND a.outcome = 'rejected'))
        OR (NEW.delivery_state = 'verified'
            AND NOT EXISTS (SELECT 1 FROM composite_recovery_delivery_attempts a WHERE a.attempt_id = NEW.verified_attempt_id AND a.allowance = 'automatic')))
    BEGIN SELECT RAISE(ABORT, 'automatic delivery closes once, with no attempt in flight, for a reason its attempts and deadline support'); END""",
    """CREATE TRIGGER composite_recovery_points_verified BEFORE UPDATE ON composite_recovery_points
    WHEN OLD.verified_at IS NULL AND NEW.verified_at IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM composite_recovery_delivery_attempts a
        WHERE a.attempt_id = NEW.verified_attempt_id AND a.recovery_point_id = OLD.recovery_point_id
          AND a.outcome = 'verified' AND a.finished_at <= NEW.verified_at
          AND (a.allowance = 'automatic') = (NEW.delivery_state = 'verified'))
    BEGIN SELECT RAISE(ABORT, 'a recovery point is verified only by its own verified attempt'); END""",
    """CREATE TRIGGER composite_recovery_points_missed BEFORE UPDATE ON composite_recovery_points
    WHEN OLD.age_target_missed_at IS NULL AND NEW.age_target_missed_at IS NOT NULL AND EXISTS (
        SELECT 1 FROM composite_recovery_points q WHERE q.captured_at > OLD.captured_at AND q.verified_at <= NEW.age_target_missed_at)
    BEGIN SELECT RAISE(ABORT, 'the age target is missed only while no newer capture is verified'); END""",
    """CREATE TRIGGER composite_recovery_points_no_delete BEFORE DELETE ON composite_recovery_points
    BEGIN SELECT RAISE(ABORT, 'recovery points are kept'); END""",
    """CREATE TABLE composite_recovery_delivery_attempts (
    attempt_id TEXT PRIMARY KEY,
    recovery_point_id TEXT NOT NULL REFERENCES composite_recovery_points (recovery_point_id) ON DELETE RESTRICT,
    allowance TEXT NOT NULL CHECK (allowance IN ('automatic', 'recovery')),
    audit_event_id TEXT REFERENCES composite_audit_events (event_id) ON DELETE RESTRICT,
    attempt_number INTEGER NOT NULL CHECK (attempt_number BETWEEN 1 AND 3),
    remote_path TEXT NOT NULL UNIQUE CHECK (remote_path <> ''),
    reserved_at INTEGER NOT NULL,
    dispatched_at INTEGER,
    finished_at INTEGER,
    outcome TEXT CHECK (outcome IN ('no_write', 'rejected', 'partial', 'uncertain', 'verified')),
    failure_kind TEXT CHECK (failure_kind IN ('host_key_mismatch', 'credentials', 'checksum_mismatch', 'destination_space')),
    next_attempt_at INTEGER,
    readback_bytes INTEGER,
    readback_sha256 BLOB,
    completion_manifest_ref TEXT,
    closure_evidence_ref TEXT,
    CHECK ((allowance = 'recovery') = (audit_event_id IS NOT NULL)),
    CHECK ((finished_at IS NULL) = (outcome IS NULL)),
    CHECK (dispatched_at IS NULL OR dispatched_at >= reserved_at),
    CHECK (finished_at IS NULL OR finished_at >= reserved_at),
    CHECK (finished_at IS NULL OR dispatched_at IS NULL OR finished_at >= dispatched_at),
    CHECK (outcome IS NULL OR outcome = 'no_write' OR dispatched_at IS NOT NULL),
    CHECK ((outcome IS NOT NULL AND outcome = 'rejected') = (failure_kind IS NOT NULL)),
    CHECK (next_attempt_at IS (CASE WHEN outcome IN ('no_write', 'partial', 'uncertain') AND attempt_number < 3
        THEN finished_at + CASE attempt_number WHEN 1 THEN 15000 ELSE 45000 END END)),
    CHECK (CASE WHEN outcome = 'verified'
        THEN readback_bytes IS NOT NULL AND readback_sha256 IS NOT NULL AND completion_manifest_ref IS NOT NULL AND closure_evidence_ref IS NOT NULL
        ELSE readback_bytes IS NULL AND readback_sha256 IS NULL AND completion_manifest_ref IS NULL AND closure_evidence_ref IS NULL END),
    UNIQUE (attempt_id, recovery_point_id)
)""",
    "CREATE UNIQUE INDEX composite_recovery_delivery_attempts_automatic ON composite_recovery_delivery_attempts (recovery_point_id, attempt_number) WHERE allowance = 'automatic'",
    "CREATE UNIQUE INDEX composite_recovery_delivery_attempts_recovery ON composite_recovery_delivery_attempts (audit_event_id, attempt_number) WHERE allowance = 'recovery'",
    "CREATE UNIQUE INDEX composite_recovery_delivery_attempts_in_flight ON composite_recovery_delivery_attempts (recovery_point_id) WHERE outcome IS NULL",
    """CREATE TRIGGER composite_recovery_delivery_attempts_reserved BEFORE INSERT ON composite_recovery_delivery_attempts
    WHEN NEW.dispatched_at IS NOT NULL OR NEW.finished_at IS NOT NULL OR NEW.outcome IS NOT NULL OR NEW.failure_kind IS NOT NULL
        OR NEW.next_attempt_at IS NOT NULL OR NEW.readback_bytes IS NOT NULL OR NEW.readback_sha256 IS NOT NULL
        OR NEW.completion_manifest_ref IS NOT NULL OR NEW.closure_evidence_ref IS NOT NULL
        OR EXISTS (SELECT 1 FROM composite_recovery_points p WHERE p.recovery_point_id = NEW.recovery_point_id AND (
            (NEW.allowance = 'automatic' AND (p.delivery_state <> 'delivering' OR NEW.reserved_at < p.validated_at OR NEW.reserved_at >= p.delivery_deadline))
            OR (NEW.allowance = 'recovery' AND (p.delivery_state NOT IN ('exhausted', 'stopped') OR p.verified_at IS NOT NULL))))
        OR EXISTS (SELECT 1 FROM composite_audit_events e WHERE e.event_id = NEW.audit_event_id AND (
            e.resource_kind <> 'composite_recovery_points' OR e.resource_id IS NOT NEW.recovery_point_id
            OR NEW.reserved_at < e.occurred_at OR NEW.reserved_at >= e.occurred_at + 420000))
        OR (NEW.attempt_number > 1 AND NOT EXISTS (SELECT 1 FROM composite_recovery_delivery_attempts prev
            WHERE prev.recovery_point_id = NEW.recovery_point_id AND prev.allowance = NEW.allowance
              AND prev.audit_event_id IS NEW.audit_event_id AND prev.attempt_number = NEW.attempt_number - 1
              AND prev.next_attempt_at <= NEW.reserved_at))
    BEGIN SELECT RAISE(ABORT, 'a delivery attempt is reserved before work, within its budget or audited window, after its backoff'); END""",
    """CREATE TRIGGER composite_recovery_delivery_attempts_fixed BEFORE UPDATE ON composite_recovery_delivery_attempts
    WHEN OLD.outcome IS NOT NULL OR (NEW.attempt_id IS NOT OLD.attempt_id OR NEW.recovery_point_id IS NOT OLD.recovery_point_id OR
        NEW.allowance IS NOT OLD.allowance OR NEW.audit_event_id IS NOT OLD.audit_event_id OR
        NEW.attempt_number IS NOT OLD.attempt_number OR NEW.remote_path IS NOT OLD.remote_path OR
        NEW.reserved_at IS NOT OLD.reserved_at)
        OR (OLD.dispatched_at IS NOT NULL AND NEW.dispatched_at IS NOT OLD.dispatched_at)
    BEGIN SELECT RAISE(ABORT, 'a delivery attempt keeps its identity, path, dispatch time and outcome'); END""",
    """CREATE TRIGGER composite_recovery_delivery_attempts_read_back BEFORE UPDATE ON composite_recovery_delivery_attempts
    WHEN NEW.outcome IS 'verified' AND EXISTS (SELECT 1 FROM composite_recovery_points p WHERE p.recovery_point_id = NEW.recovery_point_id
        AND (NEW.readback_bytes IS NOT p.archive_bytes OR NEW.readback_sha256 IS NOT p.archive_sha256))
    BEGIN SELECT RAISE(ABORT, 'a verified delivery reads back the validated archive'); END""",
    """CREATE TRIGGER composite_recovery_delivery_attempts_no_delete BEFORE DELETE ON composite_recovery_delivery_attempts
    BEGIN SELECT RAISE(ABORT, 'delivery attempts are kept'); END""",
)

# data-model.md §11: recovery cases opened by a restore and the facts each one
# must settle. A case opens held; its facts start unknown and are resolved once;
# a case is released once, by an audited decision the facts allow. A subscription's
# recovery hold names a held case and clears only when that case is released.
_RECOVERY_CASE_DDL = (
    """CREATE TABLE composite_recovery_cases (
    case_id TEXT PRIMARY KEY,
    installation_id TEXT NOT NULL CHECK (installation_id <> ''),
    scope_kind TEXT NOT NULL CHECK (scope_kind IN ('record', 'customer', 'campaign', 'money', 'panel')),
    scope_ref TEXT NOT NULL CHECK (scope_ref <> ''),
    old_restore_epoch INTEGER NOT NULL CHECK (typeof(old_restore_epoch) = 'integer' AND old_restore_epoch >= 0),
    new_restore_epoch INTEGER NOT NULL CHECK (typeof(new_restore_epoch) = 'integer'),
    restored_point_id TEXT NOT NULL CHECK (restored_point_id <> ''),
    restored_captured_at INTEGER NOT NULL,
    restored_manifest_sha256 BLOB NOT NULL
        CHECK (typeof(restored_manifest_sha256) = 'blob' AND length(restored_manifest_sha256) = 32),
    pre_restore_set_ref TEXT NOT NULL CHECK (pre_restore_set_ref <> ''),
    restrictions TEXT NOT NULL CHECK (restrictions <> ''),
    opened_at INTEGER NOT NULL,
    released_at INTEGER,
    release_kind TEXT CHECK (release_kind IN ('verified', 'usage_settlement', 'governed_remediation')),
    release_audit_event_id TEXT REFERENCES composite_audit_events (event_id) ON DELETE RESTRICT,
    follow_up_due_at INTEGER,
    CHECK (new_restore_epoch > old_restore_epoch),
    CHECK (opened_at >= restored_captured_at),
    CHECK ((released_at IS NULL) = (release_kind IS NULL) AND (released_at IS NULL) = (release_audit_event_id IS NULL)),
    CHECK ((release_kind IS 'governed_remediation') = (follow_up_due_at IS NOT NULL)),
    CHECK (follow_up_due_at IS NULL OR follow_up_due_at > released_at),
    UNIQUE (new_restore_epoch, scope_kind, scope_ref)
)""",
    """CREATE TRIGGER composite_recovery_cases_open_held BEFORE INSERT ON composite_recovery_cases
    WHEN NEW.released_at IS NOT NULL OR NEW.release_kind IS NOT NULL OR NEW.release_audit_event_id IS NOT NULL OR
        NEW.follow_up_due_at IS NOT NULL
    BEGIN SELECT RAISE(ABORT, 'a recovery case opens held'); END""",
    """CREATE TRIGGER composite_recovery_cases_identity_fixed BEFORE UPDATE ON composite_recovery_cases
    WHEN NEW.case_id IS NOT OLD.case_id OR NEW.installation_id IS NOT OLD.installation_id OR
        NEW.scope_kind IS NOT OLD.scope_kind OR NEW.scope_ref IS NOT OLD.scope_ref OR
        NEW.old_restore_epoch IS NOT OLD.old_restore_epoch OR NEW.new_restore_epoch IS NOT OLD.new_restore_epoch OR
        NEW.restored_point_id IS NOT OLD.restored_point_id OR NEW.restored_captured_at IS NOT OLD.restored_captured_at OR
        NEW.restored_manifest_sha256 IS NOT OLD.restored_manifest_sha256 OR
        NEW.pre_restore_set_ref IS NOT OLD.pre_restore_set_ref OR NEW.restrictions IS NOT OLD.restrictions OR
        NEW.opened_at IS NOT OLD.opened_at
    BEGIN SELECT RAISE(ABORT, 'recovery case identity is immutable'); END""",
    """CREATE TRIGGER composite_recovery_cases_release_final BEFORE UPDATE ON composite_recovery_cases
    WHEN OLD.released_at IS NOT NULL AND (NEW.released_at IS NOT OLD.released_at OR
        NEW.release_kind IS NOT OLD.release_kind OR NEW.release_audit_event_id IS NOT OLD.release_audit_event_id OR
        NEW.follow_up_due_at IS NOT OLD.follow_up_due_at)
    BEGIN SELECT RAISE(ABORT, 'a released recovery case is final'); END""",
    """CREATE TRIGGER composite_recovery_cases_release_needs_facts BEFORE UPDATE ON composite_recovery_cases
    WHEN OLD.released_at IS NULL AND NEW.released_at IS NOT NULL
        AND NEW.release_kind IS NOT NULL AND NEW.release_audit_event_id IS NOT NULL
        AND (
            NOT EXISTS (SELECT 1 FROM composite_recovery_evidence f WHERE f.case_id = NEW.case_id)
            OR EXISTS (SELECT 1 FROM composite_recovery_evidence f WHERE f.case_id = NEW.case_id AND f.status = 'unknown')
            OR (NEW.release_kind = 'verified' AND EXISTS (
                SELECT 1 FROM composite_recovery_evidence f WHERE f.case_id = NEW.case_id AND f.status <> 'verified'))
            OR (NEW.release_kind = 'usage_settlement' AND (
                NOT EXISTS (SELECT 1 FROM composite_recovery_evidence f
                    WHERE f.case_id = NEW.case_id AND f.status = 'irrecoverable')
                OR EXISTS (SELECT 1 FROM composite_recovery_evidence f
                    WHERE f.case_id = NEW.case_id AND f.status = 'irrecoverable' AND f.fact_kind <> 'usage')))
            OR (NEW.release_kind = 'governed_remediation' AND NOT EXISTS (
                SELECT 1 FROM composite_recovery_evidence f
                WHERE f.case_id = NEW.case_id AND f.status = 'irrecoverable' AND f.fact_kind <> 'usage'))
        )
    BEGIN SELECT RAISE(ABORT, 'the case facts do not allow this release'); END""",
    """CREATE TRIGGER composite_recovery_cases_release_decision BEFORE UPDATE ON composite_recovery_cases
    WHEN OLD.released_at IS NULL AND NEW.released_at IS NOT NULL AND EXISTS (
        SELECT 1 FROM composite_audit_events e
        WHERE e.event_id = NEW.release_audit_event_id AND (
            e.resource_kind <> 'composite_recovery_cases' OR e.resource_id <> NEW.case_id OR e.reason IS NULL
            OR e.occurred_at > NEW.released_at
            OR EXISTS (SELECT 1 FROM composite_recovery_evidence f
                WHERE f.case_id = NEW.case_id AND f.resolved_at > e.occurred_at)
            OR (NEW.release_kind = 'governed_remediation'
                AND (e.actor_domain IN ('system', 'payment_callback') OR e.evidence_ref IS NULL))))
    BEGIN SELECT RAISE(ABORT, 'the release decision does not fit this case'); END""",
    """CREATE TRIGGER composite_recovery_cases_no_delete BEFORE DELETE ON composite_recovery_cases
    BEGIN SELECT RAISE(ABORT, 'recovery cases are kept'); END""",
    """CREATE TABLE composite_recovery_evidence (
    evidence_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL REFERENCES composite_recovery_cases (case_id) ON DELETE RESTRICT,
    fact_kind TEXT NOT NULL CHECK (fact_kind IN ('ownership', 'purchase', 'financial', 'lifecycle', 'token',
        'remote_identity', 'usage', 'coupon', 'test_claim', 'campaign', 'cleanup')),
    subject_ref TEXT NOT NULL CHECK (subject_ref <> ''),
    fact TEXT NOT NULL CHECK (fact <> ''),
    source_ref TEXT CHECK (source_ref <> ''),
    recorded_at INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'unknown' CHECK (status IN ('unknown', 'verified', 'irrecoverable')),
    resolution_ref TEXT CHECK (resolution_ref <> ''),
    resolved_at INTEGER,
    CHECK ((status = 'unknown') = (resolution_ref IS NULL) AND (status = 'unknown') = (resolved_at IS NULL)),
    CHECK (resolved_at IS NULL OR resolved_at >= recorded_at)
)""",
    """CREATE TRIGGER composite_recovery_evidence_case_held BEFORE INSERT ON composite_recovery_evidence
    WHEN EXISTS (SELECT 1 FROM composite_recovery_cases c
        WHERE c.case_id = NEW.case_id AND (c.released_at IS NOT NULL OR NEW.recorded_at < c.opened_at))
    BEGIN SELECT RAISE(ABORT, 'facts are recorded only on a held case after it opened'); END""",
    """CREATE TRIGGER composite_recovery_evidence_identity_fixed BEFORE UPDATE ON composite_recovery_evidence
    WHEN NEW.evidence_id IS NOT OLD.evidence_id OR NEW.case_id IS NOT OLD.case_id OR NEW.fact_kind IS NOT OLD.fact_kind OR
        NEW.subject_ref IS NOT OLD.subject_ref OR NEW.fact IS NOT OLD.fact OR NEW.source_ref IS NOT OLD.source_ref OR
        NEW.recorded_at IS NOT OLD.recorded_at
    BEGIN SELECT RAISE(ABORT, 'recovery fact identity is immutable'); END""",
    """CREATE TRIGGER composite_recovery_evidence_resolved_once BEFORE UPDATE ON composite_recovery_evidence
    WHEN OLD.status <> 'unknown' AND (NEW.status IS NOT OLD.status OR NEW.resolution_ref IS NOT OLD.resolution_ref
        OR NEW.resolved_at IS NOT OLD.resolved_at)
    BEGIN SELECT RAISE(ABORT, 'a resolved fact is final'); END""",
    """CREATE TRIGGER composite_recovery_evidence_no_delete BEFORE DELETE ON composite_recovery_evidence
    BEGIN SELECT RAISE(ABORT, 'recovery facts are kept'); END""",
    """CREATE TRIGGER composite_subscriptions_hold_case_on_insert BEFORE INSERT ON composite_subscriptions
    WHEN NEW.recovery_hold_case IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM composite_recovery_cases c WHERE c.case_id = NEW.recovery_hold_case AND c.released_at IS NULL)
    BEGIN SELECT RAISE(ABORT, 'a recovery hold names a held case'); END""",
    """CREATE TRIGGER composite_subscriptions_hold_case_on_update BEFORE UPDATE OF recovery_hold_case ON composite_subscriptions
    WHEN NEW.recovery_hold_case IS NOT OLD.recovery_hold_case AND (
        (NEW.recovery_hold_case IS NOT NULL AND NOT EXISTS (SELECT 1 FROM composite_recovery_cases c
            WHERE c.case_id = NEW.recovery_hold_case AND c.released_at IS NULL))
        OR (NEW.recovery_hold_case IS NULL AND EXISTS (SELECT 1 FROM composite_recovery_cases c
            WHERE c.case_id = OLD.recovery_hold_case AND c.released_at IS NULL)))
    BEGIN SELECT RAISE(ABORT, 'a recovery hold clears only when its case is released'); END""",
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
    """Report whether composite issuance is enabled: the main file's processing-control switch."""
    conn = _readonly_connect(main_path)
    try:
        if _read_version(conn) > SCHEMA_VERSION:
            return False
        if conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'composite_processing_control'"
        ).fetchone() is None:
            return False
        row = conn.execute("SELECT issuance_enabled FROM composite_processing_control WHERE control_id = 1").fetchone()
        return row is not None and row[0] == 1
    finally:
        conn.close()


def _main_v1(conn: sqlite3.Connection) -> None:
    for table in KIND_TABLES:
        conn.execute(
            f"ALTER TABLE {table} ADD COLUMN service_kind TEXT NOT NULL DEFAULT 'legacy' "
            "CHECK (service_kind IN ('legacy', 'composite'))"
        )
        conn.execute(f"ALTER TABLE {table} ADD COLUMN composite_ref TEXT")
        conn.execute(f"CREATE UNIQUE INDEX idx_{table}_composite_ref ON {table} (composite_ref)")
    for statement in _PANEL_DDL + _CATALOG_DDL + _ACCOUNTING_DDL + _COMMERCE_DDL + _LIFECYCLE_DDL + _BATCH_DDL + _NOTICE_DDL + _DELIVERY_DDL + _CONTROL_DDL + _RECOVERY_DDL + _RECOVERY_CASE_DDL:
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
