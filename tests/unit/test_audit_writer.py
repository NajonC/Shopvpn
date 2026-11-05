"""T046: real SQLite audit writes, caller-owned transactions and safe diagnostics."""
import dataclasses
import json
import secrets
import sqlite3

import pytest

from composite import audit, migrations
from tests._harness.secret_scan import SecretScan


@pytest.fixture
def conn():
    connection = sqlite3.connect(':memory:')
    # Use the actual already-accepted audit DDL, including immutable-row triggers.
    for statement in migrations._NOTICE_DDL[1:4]:
        connection.execute(statement)
    yield connection
    connection.close()


def event(**changes):
    values = dict(event_id='ae-1', occurred_at=1790000000123,
                  actor_domain='web_admin', actor_id='owner-7', action='batch_authorize',
                  resource_kind='composite_batches', resource_id='bt-19',
                  reason="owner's approved change", evidence_ref='evidence:19')
    values.update(changes)
    return audit.AuditEvent(**values)


def write(conn, value=None, **kwargs):
    return audit.write_audit_event(conn, event() if value is None else value, **kwargs)


@pytest.mark.parametrize('domain', ['telegram', 'web_admin', 'payment_callback', 'system', 'cli'])
def test_write_retains_exact_metadata(conn, domain):
    value = event(actor_domain=domain)
    assert write(conn, value) == 'ae-1'
    assert conn.execute('SELECT * FROM composite_audit_events').fetchone() == (
        'ae-1', 1790000000123, domain, 'owner-7', 'batch_authorize',
        'composite_batches', 'bt-19', "owner's approved change", 'evidence:19', None)
    with pytest.raises(dataclasses.FrozenInstanceError):
        value.action = 'changed'


def test_optional_metadata_and_distinct_event_ids(conn):
    write(conn, event(reason=None, evidence_ref=None))
    write(conn, event(event_id='ae-2'))
    assert conn.execute('SELECT event_id, reason, evidence_ref FROM composite_audit_events ORDER BY event_id').fetchall() == [
        ('ae-1', None, None), ('ae-2', "owner's approved change", 'evidence:19')]


def test_writer_does_not_commit_or_rollback_caller_work(conn):
    conn.execute('CREATE TABLE caller_work (id INTEGER)')
    conn.execute('BEGIN')
    conn.execute('INSERT INTO caller_work VALUES (7)')
    write(conn)
    assert conn.in_transaction
    conn.rollback()
    assert conn.execute('SELECT * FROM composite_audit_events').fetchall() == []
    assert conn.execute('SELECT * FROM caller_work').fetchall() == []
    write(conn)
    conn.commit()
    assert conn.execute('SELECT event_id FROM composite_audit_events').fetchall() == [('ae-1',)]


def test_duplicate_is_explicit_failure_and_does_not_replace(conn):
    write(conn)
    conn.commit()
    conn.execute('CREATE TABLE caller_work (id INTEGER)')
    conn.execute('INSERT INTO caller_work VALUES (7)')
    with pytest.raises(audit.AuditWriteError):
        write(conn, event(reason='changed'))
    assert conn.in_transaction
    assert conn.execute('SELECT reason FROM composite_audit_events').fetchall() == [("owner's approved change",)]
    assert conn.execute('SELECT * FROM caller_work').fetchall() == [(7,)]


@pytest.mark.parametrize('statement', [
    "UPDATE composite_audit_events SET reason = 'changed' WHERE event_id = 'ae-1'",
    "DELETE FROM composite_audit_events WHERE event_id = 'ae-1'",
])
def test_written_rows_remain_immutable(conn, statement):
    write(conn)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(statement)
    assert conn.execute('SELECT reason FROM composite_audit_events').fetchall() == [("owner's approved change",)]


def test_writer_sanitizes_persisted_diagnostics(conn):
    secret = secrets.token_urlsafe(32)
    scan = SecretScan()
    scan.add('token', secret)
    diagnostic = dict(operation='provision', tenant_id=7, record_id=19,
                      error=RuntimeError(secret), token=secret, completed=True)
    write(conn, diagnostic=diagnostic)
    raw = conn.execute('SELECT diagnostics FROM composite_audit_events').fetchone()[0]
    assert json.loads(raw) == {'operation': 'provision', 'tenant_id': 7, 'record_id': 19}
    scan.check_text(raw, source='stored audit diagnostics')
    assert diagnostic['token'] == secret  # The writer does not mutate caller data.


def test_database_error_is_explicit_and_secret_safe():
    secret = secrets.token_urlsafe(32)
    scan = SecretScan()
    scan.add('token', secret)

    class BrokenConnection:
        def execute(self, *args):
            raise sqlite3.OperationalError(secret)

    with pytest.raises(audit.AuditWriteError) as caught:
        write(BrokenConnection())
    scan.check_exception(caught.value)
