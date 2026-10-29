"""Characterize the observable Telegram contracts (callbacks, states, FSM storage, deep links) at commit 18bf94e.

Baseline: ``.venv/bin/python -m pytest tests/characterization/test_callbacks_fsm.py --network=deny``.

The snapshots are read from the source (``ast``) and from the live keyboards/registry on a fresh
``tmp_path`` database; ``WEBHOOK_SECRET`` is in ``test_webhook_secret.py``; later tasks import
``CALLBACK_EXACT`` and ``CALLBACK_PREFIXES`` from this module to check new callback namespaces for
collisions (FR-081; constitution I).

Known unsafe behaviour:
(a) any ``/start`` parameter, even an unknown or invalid one, makes the user permanently force-join exempt (case 9);
(b) an invalid ``disc_`` code and a non-numeric ``prod_`` are dropped silently, and only the first acquisition source, reseller owner and referrer are ever kept (case 9);
(c) the FSM storage silently returns ``{}`` for corrupt data (case 8).
"""

import ast
import asyncio
import contextlib
from pathlib import Path
import sqlite3

from aiogram.fsm.state import StatesGroup
from aiogram.fsm.storage.base import StorageKey

import button_registry
import database
from fsm_storage import SQLiteStorage
import handlers_user
import keyboards as kb
import states
from tests._harness.legacy_bot import (
    FakeMessage,
    FakeUser,
    RecordingBot,
    TelegramLog,
    callback_rows,
    find_handler,
    make_state,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
OWNER = 9001
WELCOME = database.DEFAULT_SETTINGS["welcome_text"]
DISC_ON = "\U0001f39f \u06a9\u062f \u062a\u062e\u0641\u06cc\u0641 \u00ab{code}\u00bb \u0641\u0639\u0627\u0644 \u0634\u062f\u061b \u062f\u0631 \u0627\u0648\u0644\u06cc\u0646 \u062e\u0631\u06cc\u062f \u0628\u0647\u200c\u0635\u0648\u0631\u062a \u062e\u0648\u062f\u06a9\u0627\u0631 \u0627\u0639\u0645\u0627\u0644 \u0645\u06cc\u200c\u0634\u0648\u062f."
PRODUCT_GONE = "\u26d4\ufe0f \u0645\u062d\u0635\u0648\u0644 \u0645\u0648\u0631\u062f\u0646\u0638\u0631 \u06cc\u0627\u0641\u062a \u0646\u0634\u062f \u06cc\u0627 \u062f\u06cc\u06af\u0631 \u0641\u0639\u0627\u0644 \u0646\u06cc\u0633\u062a."
KAF_DAL = "\u06a9\u062f"

CALLBACK_EXACT = (
    'acct:hub',
    'acct:main_menu',
    'adm_abangateway_payments',
    'adm_abangateway_set_key',
    'adm_admin_add',
    'adm_admin_remove',
    'adm_admin_role_change',
    'adm_admins_list',
    'adm_admins_menu',
    'adm_ai_faq_add',
    'adm_ai_set_groq_key',
    'adm_ai_set_key',
    'adm_ai_set_model',
    'adm_ai_set_openrouter_key',
    'adm_ai_set_provider',
    'adm_ai_support_settings',
    'adm_ai_toggle',
    'adm_back_panel',
    'adm_backup_chat2_disable',
    'adm_backup_chat2_menu',
    'adm_backup_chat2_set',
    'adm_backup_full',
    'adm_backup_interval_custom',
    'adm_backup_interval_menu',
    'adm_backup_interval_set:12',
    'adm_backup_interval_set:24',
    'adm_backup_interval_set:48',
    'adm_backup_interval_set:6',
    'adm_backup_menu',
    'adm_backup_now',
    'adm_backup_sftp_auth:key',
    'adm_backup_sftp_auth:password',
    'adm_backup_sftp_clear',
    'adm_backup_sftp_disable',
    'adm_backup_sftp_menu',
    'adm_backup_sftp_start',
    'adm_backup_sync_menu',
    'adm_backup_sync_test',
    'adm_blupal_payments',
    'adm_blupal_set_key',
    'adm_broadcast',
    'adm_broadcast_dur:0',
    'adm_broadcast_dur:21600',
    'adm_broadcast_dur:259200',
    'adm_broadcast_dur:3600',
    'adm_broadcast_dur:86400',
    'adm_broadcast_dur:custom',
    'adm_btn_toggle:miniapp',
    'adm_card_auto',
    'adm_card_auto_card_add',
    'adm_card_auto_cards',
    'adm_card_auto_digits',
    'adm_card_auto_timeout',
    'adm_card_auto_toggle',
    'adm_card_auto_unit_toggle',
    'adm_card_auto_webhook',
    'adm_card_autodel:0',
    'adm_card_autodel:10800',
    'adm_card_autodel:1800',
    'adm_card_autodel:3600',
    'adm_card_autodel:86400',
    'adm_card_autodel:custom',
    'adm_card_toggle',
    'adm_cat:access',
    'adm_cat:alerts',
    'adm_cat:appearance',
    'adm_cat:daily',
    'adm_cat:finance',
    'adm_cat:management',
    'adm_cat:marketing',
    'adm_cat:products',
    'adm_cat:resellers',
    'adm_cat_add',
    'adm_ccp_add',
    'adm_ccp_list',
    'adm_ccpm_all',
    'adm_clear_support_contact',
    'adm_commission_resellers_menu',
    'adm_comres_active',
    'adm_comres_direct_new',
    'adm_comres_pending',
    'adm_connect_edit_text',
    'adm_connect_edit_threshold',
    'adm_connect_toggle',
    'adm_credit_resellers_menu',
    'adm_cres_find',
    'adm_crypto_payments',
    'adm_custom_config_edit_range',
    'adm_custom_config_prefix',
    'adm_custom_config_settings',
    'adm_custom_config_toggle',
    'adm_deliver_individual_toggle',
    'adm_deliver_sublink_toggle',
    'adm_disc_add',
    'adm_disc_scope:all',
    'adm_disc_scope:cat',
    'adm_disc_scope:prod',
    'adm_disc_scope_back',
    'adm_dl_addbtn',
    'adm_dl_build',
    'adm_dl_params_list',
    'adm_dlp_type:buy',
    'adm_dlp_type:custom',
    'adm_dlp_type:disc',
    'adm_dlp_type:prod',
    'adm_dlp_type:test',
    'adm_dlp_type:wheel',
    'adm_early_renewal_edit_days',
    'adm_early_renewal_edit_percent',
    'adm_early_renewal_toggle',
    'adm_exit_panel',
    'adm_factory_reset_cancel',
    'adm_factory_reset_start',
    'adm_factory_reset_step2',
    'adm_forcejoin_set_channel',
    'adm_forcejoin_toggle',
    'adm_mm_toggle_columns',
    'adm_mm_toggle_inline',
    'adm_mm_toggle_reply',
    'adm_newprod_durmode:limited',
    'adm_newprod_durmode:unlimited',
    'adm_newprod_src:bank',
    'adm_newprod_src:direct',
    'adm_newprod_volmode:limited',
    'adm_newprod_volmode:unlimited',
    'adm_no_connect_edit_hours',
    'adm_no_connect_edit_text',
    'adm_no_connect_edit_threshold',
    'adm_no_connect_toggle',
    'adm_noapay_payments',
    'adm_noapay_set_key',
    'adm_noapay_set_rate',
    'adm_noapay_set_secret',
    'adm_noapay_toggle',
    'adm_orphan_db_files',
    'adm_panel_server_add',
    'adm_panel_servers',
    'adm_panel_type:3xui',
    'adm_panel_type:alireza',
    'adm_panel_type:hiddify',
    'adm_panel_type:ibsng',
    'adm_panel_type:marzban',
    'adm_panel_type:marzneshin',
    'adm_panel_type:mikrotik',
    'adm_panel_type:pasarguard',
    'adm_panel_type:rebecca',
    'adm_panel_type:sui',
    'adm_panel_type:wgdashboard',
    'adm_plisio_set_key',
    'adm_pricing_tier_add',
    'adm_pricing_tiers',
    'adm_prod_add',
    'adm_products',
    'adm_referral_commission_max_edit',
    'adm_referral_freeconfig_product',
    'adm_referral_freeconfig_threshold_edit',
    'adm_referral_freeconfig_toggle',
    'adm_referral_invitebonus_amount_edit',
    'adm_referral_invitebonus_max_edit',
    'adm_referral_invitebonus_toggle',
    'adm_referral_percent_edit',
    'adm_referral_settings',
    'adm_referral_toggle',
    'adm_renewal_edit_days',
    'adm_renewal_edit_hours',
    'adm_renewal_edit_percent',
    'adm_renewal_price_day',
    'adm_renewal_price_gb',
    'adm_renewal_toggle',
    'adm_resbot_add',
    'adm_reseller_orphans',
    'adm_reseller_requests_menu',
    'adm_resellers_menu',
    'adm_reset_test_configs',
    'adm_restore_cancel',
    'adm_restore_cancel_wait',
    'adm_restore_confirm',
    'adm_restore_full_cancel',
    'adm_restore_full_cancel_wait',
    'adm_restore_full_confirm',
    'adm_restore_full_start',
    'adm_restore_start',
    'adm_set_card_edit',
    'adm_set_panel_domain',
    'adm_set_support_contact_edit',
    'adm_stats',
    'adm_stats_adv:7',
    'adm_stock_alert_edit',
    'adm_temp_message',
    'adm_tempmsg_dur:21600',
    'adm_tempmsg_dur:259200',
    'adm_tempmsg_dur:3600',
    'adm_tempmsg_dur:86400',
    'adm_tempmsg_dur:custom',
    'adm_tempmsg_target:custom',
    'adm_tempmsg_target:self',
    'adm_test_add',
    'adm_test_menu',
    'adm_test_toggle',
    'adm_tp_add',
    'adm_volume_edit_discount_hours',
    'adm_volume_edit_discount_percent',
    'adm_volume_edit_gb',
    'adm_volume_edit_percent',
    'adm_volume_toggle',
    'adm_volume_toggle_mode',
    'adm_walletpm_all',
    'adm_wheel_edit_cooldown',
    'adm_wheel_edit_expiry',
    'adm_wheel_edit_percent',
    'adm_wheel_edit_prizes',
    'adm_wheel_toggle',
    'adm_xui_inbound_confirm',
    'ai_end',
    'cancel_flow',
    'contact_ai',
    'contact_direct',
    'contact_menu',
    'custom_config_random_username',
    'mo_back',
    'newprodpm_all',
    'newprodpm_done',
    'noop',
    'reseller_new_config',
    'resreq_bot:dedicated',
    'resreq_bot:inline_link',
    'resreq_bot:none',
    'resreq_cancel_payment',
    'resreq_miniapp:0',
    'resreq_miniapp:1',
    'resreq_ownerok',
    'resreq_ownerretry',
    'resreq_supply:fixed_product',
    'resreq_supply:volume_credit',
    'resreq_webpanel:0',
    'resreq_webpanel:1',
    'rrpct:accept',
    'rrpm:ok',
    'rt:close',
    'rt:menu',
    'start_topup',
    'tickets_mine',
    'tickets_new',
)

CALLBACK_PREFIXES = (
    'adm_acct_toggle:',
    'adm_ai_faq_del:',
    'adm_ai_model_pick:',
    'adm_ai_provider_pick:',
    'adm_btn_color_menu:',
    'adm_btn_color_set:',
    'adm_btn_edit:',
    'adm_btn_toggle:',
    'adm_card_auto_card:',
    'adm_card_auto_card_del:',
    'adm_card_auto_card_edit:',
    'adm_card_auto_card_toggle:',
    'adm_cat_del:',
    'adm_cat_toggle:',
    'adm_ccp_delete:',
    'adm_ccp_delete_force:',
    'adm_ccp_duration_mode:',
    'adm_ccp_edit_desc:',
    'adm_ccp_edit_flat_price:',
    'adm_ccp_edit_name:',
    'adm_ccp_edit_panel:',
    'adm_ccp_edit_volume:',
    'adm_ccp_paymethods:',
    'adm_ccp_pricing_mode:',
    'adm_ccp_set_duration_mode:',
    'adm_ccp_set_panel:',
    'adm_ccp_set_pricing_mode:',
    'adm_ccp_tier_add:',
    'adm_ccp_tier_delete:',
    'adm_ccp_tiers:',
    'adm_ccp_toggle:',
    'adm_ccp_view:',
    'adm_ccpm_tgl:',
    'adm_ccppm_all:',
    'adm_ccppm_tgl:',
    'adm_cres_credit:',
    'adm_cres_panel:',
    'adm_cres_panel_set:',
    'adm_cres_toggle:',
    'adm_cres_view:',
    'adm_customgw_minamt:',
    'adm_customgw_toggle:',
    'adm_disc_del:',
    'adm_disc_scope_cat:',
    'adm_disc_scope_prod:',
    'adm_disc_toggle:',
    'adm_dlp_code:',
    'adm_dlp_prod:',
    'adm_dlp_prod_disc:',
    'adm_dlp_prod_nodisc:',
    'adm_dlp_prodcat:',
    'adm_minamt_edit:',
    'adm_newprod_srv:',
    'adm_orphan_db_del:',
    'adm_panel_server_delete:',
    'adm_panel_server_delete_force:',
    'adm_panel_server_suburl:',
    'adm_panel_server_template:',
    'adm_panel_server_test:',
    'adm_panel_server_toggle:',
    'adm_panel_server_usage:custom:',
    'adm_panel_server_usage:reseller:',
    'adm_panel_server_usage:test:',
    'adm_panel_server_view:',
    'adm_pricing_tier_delete:',
    'adm_prod_del:',
    'adm_prod_paymethods:',
    'adm_prod_set_srv:',
    'adm_prod_srv:',
    'adm_prod_toggle:',
    'adm_prod_vol:',
    'adm_prodpm_all:',
    'adm_prodpm_tgl:',
    'adm_referral_freeconfig_setprod:',
    'adm_resbot_del:',
    'adm_resbot_delc:',
    'adm_resbot_level:',
    'adm_resbot_toggle:',
    'adm_resbot_webpanel:',
    'adm_resbot_webpanel_loginlink:',
    'adm_resbot_webpanel_off:',
    'adm_resbot_webpanel_regen:',
    'adm_reseller_orphan_purge:',
    'adm_stats_adv:',
    'adm_stats_p:',
    'adm_ticket_close:',
    'adm_ticket_reply:',
    'adm_ticket_view:',
    'adm_tickets_list:',
    'adm_tp_delete:',
    'adm_tp_delete_force:',
    'adm_tp_edit_duration:',
    'adm_tp_edit_name:',
    'adm_tp_edit_panel:',
    'adm_tp_edit_prefix:',
    'adm_tp_edit_volume:',
    'adm_tp_set_panel:',
    'adm_tp_toggle:',
    'adm_tp_view:',
    'adm_walletpm_tgl:',
    'adm_xui_inbound_toggle:',
    'cancel_abangateway_invoice:',
    'cancel_blupal_invoice:',
    'cancel_crypto_invoice:',
    'cancel_noapay_invoice:',
    'ccf_pick_product:',
    'check_abangateway_invoice:',
    'check_blupal_invoice:',
    'check_noapay_invoice:',
    'comres_approve:',
    'comres_disable:',
    'comres_edit:',
    'comres_reject:',
    'comres_view:',
    'comres_view_active:',
    'mm:',
    'mo_del:',
    'mo_delok:',
    'mo_links:',
    'mo_refresh:',
    'mo_v:',
    'newprodpm_tgl:',
    'order_approve:',
    'order_reject:',
    'qty_dec:',
    'qty_inc:',
    'reply_user:',
    'reseller_fixed:',
    'respay:',
    'resreq_admin_cancel:',
    'resreq_approve:',
    'resreq_cancel:',
    'resreq_ownerx_no:',
    'resreq_ownerx_ok:',
    'resreq_panel:',
    'resreq_pay:',
    'resreq_payok:',
    'resreq_payreject:',
    'resreq_reject:',
    'resreq_supplyprod:',
    'rrpm:t:',
    'rt:go:',
    'rt:goc:',
    'rt:pick:',
    'svc_autorenew:',
    'svc_cut:',
    'svc_cutok:',
    'svc_hist:',
    'svc_inquiry:',
    'svc_qr:',
    'svc_rename:',
    'svc_renew:full:',
    'svc_renew:time:',
    'svc_renew:volume:',
    'svc_renew_pick:',
    'svc_toggle:',
    'svc_transfer:',
    'svc_transok:',
    'ticket_close:',
    'ticket_reply:',
    'ticket_view:',
    'tierreq_no:',
    'tierreq_ok:',
    'topup_approve:',
    'topup_reject:',
    'user_test_plan:',
    'view_abangateway_invoice:',
    'view_blupal_invoice:',
    'view_crypto_invoice:',
    'view_noapay_invoice:',
    'view_order:',
    'view_topup:',
)

ADMIN_ITEM_CALLBACKS = (
    ('daily', 'adm_pending_orders', 'adm_pending_orders'),
    ('daily', 'adm_tickets_menu', 'adm_tickets_menu'),
    ('daily', 'adm_pending_topups', 'adm_pending_topups'),
    ('daily', 'adm_crypto_payments', 'adm_crypto_payments'),
    ('daily', 'adm_abangateway_payments', 'adm_abangateway_payments'),
    ('daily', 'adm_blupal_payments', 'adm_blupal_payments'),
    ('daily', 'adm_noapay_payments', 'adm_noapay_payments'),
    ('daily', 'adm_xgw_pay_zarinpal', 'adm_xgw_payments:zarinpal'),
    ('daily', 'adm_xgw_pay_aqayepardakht', 'adm_xgw_payments:aqayepardakht'),
    ('daily', 'adm_xgw_pay_tetra98', 'adm_xgw_payments:tetra98'),
    ('daily', 'adm_xgw_pay_cubepay', 'adm_xgw_payments:cubepay'),
    ('daily', 'adm_xgw_pay_nowpayments', 'adm_xgw_payments:nowpayments'),
    ('daily', 'adm_xgw_pay_tgstars', 'adm_xgw_payments:tgstars'),
    ('daily', 'adm_reseller_requests_menu', 'adm_reseller_requests_menu'),
    ('products', 'adm_categories', 'adm_categories'),
    ('products', 'adm_products', 'adm_products'),
    ('products', 'adm_add_configs', 'adm_add_configs'),
    ('products', 'adm_random_cfg', 'adm_random_cfg'),
    ('products', 'adm_test_menu', 'adm_test_menu'),
    ('products', 'adm_custom_config_settings', 'adm_custom_config_settings'),
    ('products', 'adm_delivery_settings', 'adm_delivery_settings'),
    ('products', 'adm_renewal_pricing', 'adm_renewal_pricing'),
    ('resellers', 'adm_resellers_menu', 'adm_resellers_menu'),
    ('resellers', 'adm_credit_resellers_menu', 'adm_credit_resellers_menu'),
    ('resellers', 'adm_commission_resellers_menu', 'adm_commission_resellers_menu'),
    ('marketing', 'adm_discounts_menu', 'adm_discounts_menu'),
    ('marketing', 'adm_wheel_settings', 'adm_wheel_settings'),
    ('marketing', 'adm_referral_settings', 'adm_referral_settings'),
    ('marketing', 'adm_broadcast', 'adm_broadcast'),
    ('marketing', 'adm_deeplink_tools', 'adm_deeplink_tools'),
    ('marketing', 'adm_forcejoin_menu', 'adm_forcejoin_menu'),
    ('marketing', 'adm_temp_message', 'adm_temp_message'),
    ('finance', 'adm_set_card', 'adm_set_card'),
    ('finance', 'adm_card_autodelete', 'adm_card_autodelete'),
    ('finance', 'adm_set_plisio', 'adm_set_plisio'),
    ('finance', 'adm_set_abangateway', 'adm_set_abangateway'),
    ('finance', 'adm_set_blupal', 'adm_set_blupal'),
    ('finance', 'adm_set_noapay', 'adm_set_noapay'),
    ('finance', 'adm_set_xgw_zarinpal', 'adm_xgw:zarinpal'),
    ('finance', 'adm_set_xgw_aqayepardakht', 'adm_xgw:aqayepardakht'),
    ('finance', 'adm_set_xgw_tetra98', 'adm_xgw:tetra98'),
    ('finance', 'adm_set_xgw_cubepay', 'adm_xgw:cubepay'),
    ('finance', 'adm_set_xgw_nowpayments', 'adm_xgw:nowpayments'),
    ('finance', 'adm_set_xgw_tgstars', 'adm_xgw:tgstars'),
    ('finance', 'adm_card_auto', 'adm_card_auto'),
    ('finance', 'adm_custom_gateways', 'adm_custom_gateways'),
    ('finance', 'adm_min_amount_settings', 'adm_min_amount_settings'),
    ('finance', 'adm_wallet_paymethods', 'adm_wallet_paymethods'),
    ('finance', 'adm_cc_paymethods', 'adm_cc_paymethods'),
    ('alerts', 'adm_renewal_settings', 'adm_renewal_settings'),
    ('alerts', 'adm_volume_reminder_settings', 'adm_volume_reminder_settings'),
    ('alerts', 'adm_connect_alert_settings', 'adm_connect_alert_settings'),
    ('alerts', 'adm_early_renewal_discount', 'adm_early_renewal_discount'),
    ('alerts', 'adm_stock_alert_settings', 'adm_stock_alert_settings'),
    ('alerts', 'adm_account_settings', 'adm_account_settings'),
    ('access', 'adm_admins_menu', 'adm_admins_menu'),
    ('access', 'adm_set_support_contact', 'adm_set_support_contact'),
    ('access', 'adm_ai_support_settings', 'adm_ai_support_settings'),
    ('appearance', 'adm_edit_buttons', 'adm_edit_buttons'),
    ('appearance', 'adm_main_menu_settings', 'adm_main_menu_settings'),
    ('appearance', 'adm_edit_welcome', 'adm_edit_welcome'),
    ('appearance', 'adm_panel_colors_menu', 'adm_panel_colors_menu'),
    ('appearance', 'adm_buyflow_colors_menu', 'adm_buyflow_colors_menu'),
    ('management', 'adm_stats', 'adm_stats'),
    ('management', 'adm_backup_menu', 'adm_backup_menu'),
)

REGISTRY_GROUPS = (
    ('admin_categories', ('daily', 'products', 'resellers', 'marketing', 'finance', 'alerts', 'access', 'appearance', 'management')),
    ('admin_items__daily', ('adm_pending_orders', 'adm_tickets_menu', 'adm_pending_topups', 'adm_crypto_payments', 'adm_abangateway_payments', 'adm_blupal_payments', 'adm_noapay_payments', 'adm_xgw_pay_zarinpal', 'adm_xgw_pay_aqayepardakht', 'adm_xgw_pay_tetra98', 'adm_xgw_pay_cubepay', 'adm_xgw_pay_nowpayments', 'adm_xgw_pay_tgstars', 'adm_reseller_requests_menu')),
    ('admin_items__products', ('adm_categories', 'adm_products', 'adm_add_configs', 'adm_random_cfg', 'adm_test_menu', 'adm_custom_config_settings', 'adm_delivery_settings', 'adm_renewal_pricing')),
    ('admin_items__resellers', ('adm_resellers_menu', 'adm_credit_resellers_menu', 'adm_commission_resellers_menu')),
    ('admin_items__marketing', ('adm_discounts_menu', 'adm_wheel_settings', 'adm_referral_settings', 'adm_broadcast', 'adm_deeplink_tools', 'adm_forcejoin_menu', 'adm_temp_message')),
    ('admin_items__finance', ('adm_set_card', 'adm_card_autodelete', 'adm_set_plisio', 'adm_set_abangateway', 'adm_set_blupal', 'adm_set_noapay', 'adm_set_xgw_zarinpal', 'adm_set_xgw_aqayepardakht', 'adm_set_xgw_tetra98', 'adm_set_xgw_cubepay', 'adm_set_xgw_nowpayments', 'adm_set_xgw_tgstars', 'adm_card_auto', 'adm_custom_gateways', 'adm_min_amount_settings', 'adm_wallet_paymethods', 'adm_cc_paymethods')),
    ('admin_items__alerts', ('adm_renewal_settings', 'adm_volume_reminder_settings', 'adm_connect_alert_settings', 'adm_early_renewal_discount', 'adm_stock_alert_settings', 'adm_account_settings')),
    ('admin_items__access', ('adm_admins_menu', 'adm_set_support_contact', 'adm_ai_support_settings')),
    ('admin_items__appearance', ('adm_edit_buttons', 'adm_main_menu_settings', 'adm_edit_welcome')),
    ('admin_items__management', ('adm_stats', 'adm_backup_menu')),
    ('buyflow', ('btn_custom_config', 'btn_buy_continue', 'btn_enter_code', 'btn_buy_back', 'btn_cat_select', 'btn_product_select')),
    ('buyflow_confirm', ('btn_buy_continue', 'btn_enter_code')),
    ('account_hub', ('acct_orders', 'acct_referral', 'acct_wallet')),
    ('payment_methods', ('card', 'card_auto', 'abangateway', 'blupal', 'noapay', 'crypto', 'zarinpal', 'aqayepardakht', 'tetra98', 'cubepay', 'nowpayments', 'tgstars')),
)

STATE_NAMES = (
    'AIChatFlow:chatting',
    'AdminAIFaqAdd:waiting_answer',
    'AdminAIFaqAdd:waiting_question',
    'AdminAddAdmin:waiting_id',
    'AdminAddCategory:waiting_name',
    'AdminAddConfigs:waiting_links',
    'AdminAddConfigs:waiting_product',
    'AdminAddCustomConfigProductTier:waiting_from_gb',
    'AdminAddCustomConfigProductTier:waiting_price',
    'AdminAddCustomConfigProductTier:waiting_to_gb',
    'AdminAddPanelServer:waiting_inbound_select',
    'AdminAddPanelServer:waiting_name',
    'AdminAddPanelServer:waiting_password',
    'AdminAddPanelServer:waiting_sub_base_url',
    'AdminAddPanelServer:waiting_template_user',
    'AdminAddPanelServer:waiting_type',
    'AdminAddPanelServer:waiting_url',
    'AdminAddPanelServer:waiting_username',
    'AdminAddPricingTier:waiting_from_gb',
    'AdminAddPricingTier:waiting_price',
    'AdminAddPricingTier:waiting_to_gb',
    'AdminAddProduct:waiting_auto_provision_volume',
    'AdminAddProduct:waiting_auto_provision_volume_mode',
    'AdminAddProduct:waiting_category',
    'AdminAddProduct:waiting_desc',
    'AdminAddProduct:waiting_duration',
    'AdminAddProduct:waiting_name',
    'AdminAddProduct:waiting_payment_methods',
    'AdminAddProduct:waiting_price',
    'AdminAddProduct:waiting_provision_choice',
    'AdminAddProduct:waiting_provision_duration_mode',
    'AdminAddProduct:waiting_provision_server',
    'AdminAddResellerBot:waiting_owner_id',
    'AdminAddResellerBot:waiting_owner_name',
    'AdminAddResellerBot:waiting_token',
    'AdminAddTestConfigs:waiting_links',
    'AdminAddTestPlan:waiting_duration_hours',
    'AdminAddTestPlan:waiting_name',
    'AdminAddTestPlan:waiting_panel',
    'AdminAddTestPlan:waiting_prefix',
    'AdminAddTestPlan:waiting_volume_mb',
    'AdminBackupInterval:waiting_hours',
    'AdminBackupSecondaryChat:waiting_chat_id',
    'AdminBackupSftp:waiting_host',
    'AdminBackupSftp:waiting_key_path',
    'AdminBackupSftp:waiting_password',
    'AdminBackupSftp:waiting_port',
    'AdminBackupSftp:waiting_remote_dir',
    'AdminBackupSftp:waiting_username',
    'AdminBroadcast:waiting_custom_minutes',
    'AdminBroadcast:waiting_duration',
    'AdminBroadcast:waiting_message',
    'AdminC2CCard:waiting_bank',
    'AdminC2CCard:waiting_holder',
    'AdminC2CCard:waiting_number',
    'AdminC2CSettings:waiting_digits',
    'AdminC2CSettings:waiting_timeout',
    'AdminChangeRole:waiting_id',
    'AdminChannelButton:waiting_button_text',
    'AdminChannelButton:waiting_custom_param',
    'AdminChannelButton:waiting_forward',
    'AdminCommissionResellerFlow:waiting_approve_percent',
    'AdminCommissionResellerFlow:waiting_direct_percent',
    'AdminCommissionResellerFlow:waiting_direct_user_id',
    'AdminCommissionResellerFlow:waiting_edit_percent',
    'AdminCommissionResellerFlow:waiting_reject_reason',
    'AdminConnectAlertSettings:waiting_connect_text',
    'AdminConnectAlertSettings:waiting_connect_threshold',
    'AdminConnectAlertSettings:waiting_no_connect_hours',
    'AdminConnectAlertSettings:waiting_no_connect_text',
    'AdminConnectAlertSettings:waiting_no_connect_threshold',
    'AdminCreateDiscount:waiting_code',
    'AdminCreateDiscount:waiting_expiry',
    'AdminCreateDiscount:waiting_max_purchase',
    'AdminCreateDiscount:waiting_maxuses',
    'AdminCreateDiscount:waiting_min_purchase',
    'AdminCreateDiscount:waiting_scope',
    'AdminCreateDiscount:waiting_scope_category',
    'AdminCreateDiscount:waiting_scope_product',
    'AdminCreateDiscount:waiting_type_value',
    'AdminCustomConfigProduct:waiting_description',
    'AdminCustomConfigProduct:waiting_duration_max',
    'AdminCustomConfigProduct:waiting_duration_min',
    'AdminCustomConfigProduct:waiting_duration_mode_pick',
    'AdminCustomConfigProduct:waiting_duration_value',
    'AdminCustomConfigProduct:waiting_flat_price',
    'AdminCustomConfigProduct:waiting_name',
    'AdminCustomConfigProduct:waiting_panel_pick',
    'AdminCustomConfigProduct:waiting_pricing_mode_pick',
    'AdminCustomConfigProduct:waiting_volume_max',
    'AdminCustomConfigProduct:waiting_volume_min',
    'AdminCustomConfigSettings:waiting_max_gb',
    'AdminCustomConfigSettings:waiting_min_gb',
    'AdminCustomConfigSettings:waiting_prefix',
    'AdminCustomGatewayMinAmount:waiting_value',
    'AdminDeepLinkTools:waiting_custom_param',
    'AdminEarlyRenewalDiscount:waiting_days',
    'AdminEarlyRenewalDiscount:waiting_percent',
    'AdminEditButton:waiting_text',
    'AdminEditProduct:waiting_sub_base_url',
    'AdminEditProduct:waiting_volume',
    'AdminEditTestPlan:waiting_duration_hours',
    'AdminEditTestPlan:waiting_name',
    'AdminEditTestPlan:waiting_panel',
    'AdminEditTestPlan:waiting_prefix',
    'AdminEditTestPlan:waiting_volume_mb',
    'AdminEditWelcome:waiting_text',
    'AdminFactoryReset:waiting_confirm_text',
    'AdminForceJoin:waiting_channel',
    'AdminMinAmountSettings:waiting_value',
    'AdminProductPaymentMethods:viewing',
    'AdminReferralCommissionMax:waiting_value',
    'AdminReferralFreeConfigThreshold:waiting_value',
    'AdminReferralInviteBonusAmount:waiting_value',
    'AdminReferralInviteBonusMax:waiting_value',
    'AdminReferralPercent:waiting_value',
    'AdminRemoveAdmin:waiting_id',
    'AdminRenewalPricing:waiting_price_per_day',
    'AdminRenewalPricing:waiting_price_per_gb',
    'AdminRenewalSettings:waiting_days_before',
    'AdminRenewalSettings:waiting_expiry_hours',
    'AdminRenewalSettings:waiting_percent',
    'AdminReplyFlow:waiting_reply',
    'AdminResellerCredit:waiting_delta',
    'AdminResellerCredit:waiting_user_id',
    'AdminResellerRequestFlow:waiting_payment_methods',
    'AdminResellerRequestFlow:waiting_percent',
    'AdminResellerRequestFlow:waiting_price',
    'AdminResellerRequestFlow:waiting_reject_reason',
    'AdminResetTestConfig:waiting_message',
    'AdminRestoreBackup:waiting_confirm',
    'AdminRestoreBackup:waiting_file',
    'AdminRestoreFullBackup:waiting_confirm',
    'AdminRestoreFullBackup:waiting_file',
    'AdminSetAbanGateway:waiting_key',
    'AdminSetBlupal:waiting_key',
    'AdminSetCard:waiting_autodelete_custom',
    'AdminSetCard:waiting_holder',
    'AdminSetCard:waiting_number',
    'AdminSetExtraGateway:waiting_value',
    'AdminSetGeminiKey:waiting_key',
    'AdminSetGroqKey:waiting_key',
    'AdminSetNoapay:waiting_key',
    'AdminSetNoapay:waiting_rate',
    'AdminSetNoapay:waiting_secret',
    'AdminSetOpenRouterKey:waiting_key',
    'AdminSetPanelDomain:waiting_url',
    'AdminSetPanelSubUrl:waiting_url',
    'AdminSetPanelTemplate:waiting_username',
    'AdminSetPlisio:waiting_key',
    'AdminSetSupportContact:waiting_id',
    'AdminStockAlertSettings:waiting_threshold',
    'AdminTempMessage:waiting_custom_minutes',
    'AdminTempMessage:waiting_target_id',
    'AdminTempMessage:waiting_text',
    'AdminTicketReplyFlow:waiting_reply',
    'AdminVolumeReminderSettings:waiting_discount_hours',
    'AdminVolumeReminderSettings:waiting_discount_percent',
    'AdminVolumeReminderSettings:waiting_gb_left',
    'AdminVolumeReminderSettings:waiting_percent',
    'AdminWheelSettings:waiting_cooldown',
    'AdminWheelSettings:waiting_expiry',
    'AdminWheelSettings:waiting_prizes',
    'AdminWheelSettings:waiting_win_percent',
    'BuyFlow:waiting_config_name',
    'BuyFlow:waiting_customgw_phone',
    'BuyFlow:waiting_receipt',
    'CommissionResellerRequestFlow:waiting_percent',
    'ContactFlow:waiting_message',
    'CustomConfigFlow:waiting_duration',
    'CustomConfigFlow:waiting_product_select',
    'CustomConfigFlow:waiting_receipt',
    'CustomConfigFlow:waiting_username',
    'CustomConfigFlow:waiting_volume',
    'DiscountEntry:waiting_code',
    'RenewalFlow:waiting_amount',
    'RenewalFlow:waiting_customgw_phone',
    'RenewalFlow:waiting_receipt',
    'ResellerFlow:waiting_fixed_product_username',
    'ResellerFlow:waiting_username',
    'ResellerFlow:waiting_volume',
    'ResellerRequestFlow:waiting_bot_choice',
    'ResellerRequestFlow:waiting_bot_token',
    'ResellerRequestFlow:waiting_miniapp',
    'ResellerRequestFlow:waiting_owner_id',
    'ResellerRequestFlow:waiting_owner_id_confirm',
    'ResellerRequestFlow:waiting_payment_phone',
    'ResellerRequestFlow:waiting_percent',
    'ResellerRequestFlow:waiting_receipt',
    'ResellerRequestFlow:waiting_supply_model',
    'ResellerRequestFlow:waiting_supply_product',
    'ResellerRequestFlow:waiting_supply_qty',
    'ResellerRequestFlow:waiting_text',
    'ResellerRequestFlow:waiting_volume',
    'ResellerRequestFlow:waiting_web_panel',
    'ServiceRenameFlow:waiting_suffix',
    'ServiceTransferFlow:waiting_target_id',
    'TicketFlow:waiting_message',
    'TicketFlow:waiting_subject',
    'TicketReplyFlow:waiting_message',
    'WalletTopup:waiting_amount',
    'WalletTopup:waiting_customgw_phone',
    'WalletTopup:waiting_receipt',
)


def _callback_literals(path: str) -> tuple[frozenset, frozenset, int]:
    source = (REPO_ROOT / path).read_text(encoding="utf-8")
    tree = ast.parse(source)
    exact = set()
    prefixes = set()
    unresolved = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg == "callback_data":
            val = node.value
            if isinstance(val, ast.Constant) and isinstance(val.value, str):
                exact.add(val.value)
            elif (
                isinstance(val, ast.JoinedStr)
                and val.values
                and isinstance(val.values[0], ast.Constant)
                and isinstance(val.values[0].value, str)
            ):
                prefixes.add(val.values[0].value)
            else:
                unresolved += 1
    return frozenset(exact), frozenset(prefixes), unresolved


def _state_names() -> tuple[int, list[str]]:
    groups = [
        c
        for c in vars(states).values()
        if isinstance(c, type) and issubclass(c, StatesGroup) and c is not StatesGroup and c.__module__ == "states"
    ]
    return len(groups), sorted(s.state for c in groups for s in c.__states__)


def _main(tmp_path: Path) -> database.Database:
    db = database.Database(str(tmp_path / "main.db"))
    db.init_db(OWNER)
    return db


def _user_row(db: database.Database, tg_id: int):
    with db._get_conn() as conn:
        return tuple(
            conn.execute(
                "SELECT owner_reseller_id, referred_by, acquisition_source, force_join_exempt FROM users WHERE telegram_id=?",
                (tg_id,),
            ).fetchone()
        )


# Case 1
def test_keyboards_callback_literals():
    exact, prefixes, unresolved = _callback_literals("keyboards.py")
    assert exact == frozenset(CALLBACK_EXACT)
    assert prefixes == frozenset(CALLBACK_PREFIXES)
    assert unresolved == 20
    assert len(CALLBACK_EXACT) == 243
    assert len(CALLBACK_PREFIXES) == 172
    assert {"noop", "cancel_flow", "acct:hub", "rt:menu", "mo_back"} <= exact
    assert {
        "mm:",
        "mo_v:",
        "svc_renew:full:",
        "qty_dec:",
        "tierreq_ok:",
        "adm_panel_server_usage:custom:",
    } <= prefixes
    assert max(len(v.encode()) for v in exact) <= 64
    assert not any(v.startswith("cmp:") for v in exact | prefixes)
    assert _callback_literals("button_registry.py") == (frozenset(), frozenset(), 0)


# Case 2
def test_admin_panel_item_callbacks():
    actual = tuple(
        (cat_key, key, kb._admin_item_label_and_cb(key)[1])
        for cat_key, _, keys in kb.ADMIN_PANEL_CATEGORIES
        for key in keys
    )
    assert actual == ADMIN_ITEM_CALLBACKS
    assert len(ADMIN_ITEM_CALLBACKS) == 65
    cb_pairs = {(k, cb) for _, k, cb in actual}
    assert ("adm_pending_orders", "adm_pending_orders") in cb_pairs
    assert ("adm_xgw_pay_zarinpal", "adm_xgw_payments:zarinpal") in cb_pairs
    assert ("adm_set_xgw_tgstars", "adm_xgw:tgstars") in cb_pairs
    assert ("adm_panel_colors_menu", "adm_panel_colors_menu") in cb_pairs
    assert kb._admin_item_label_and_cb("zz_unknown") == ("zz_unknown", "zz_unknown")
    assert len(kb.ADMIN_PANEL_ITEMS) == 63


# Case 3
def test_button_registry_groups(tmp_path):
    db = _main(tmp_path)
    actual = tuple(
        (g["key"], tuple(i["key"] for i in g["items"]))
        for g in button_registry.build_registry(db)["groups"]
    )
    assert actual == REGISTRY_GROUPS
    assert [(k, len(items)) for k, items in REGISTRY_GROUPS] == [
        ("admin_categories", 9),
        ("admin_items__daily", 14),
        ("admin_items__products", 8),
        ("admin_items__resellers", 3),
        ("admin_items__marketing", 7),
        ("admin_items__finance", 17),
        ("admin_items__alerts", 6),
        ("admin_items__access", 3),
        ("admin_items__appearance", 3),
        ("admin_items__management", 2),
        ("buyflow", 6),
        ("buyflow_confirm", 2),
        ("account_hub", 3),
        ("payment_methods", 12),
    ]
    assert button_registry.STYLE_CHOICES == ("", "primary", "success", "danger")
    db.close()


# Case 4
def test_main_inline_menu_callbacks(tmp_path):
    db = _main(tmp_path)
    assert callback_rows(kb.main_menu_inline_kb(db, True, True, True)) == [
        ["mm:btn_buy"],
        ["mm:btn_test"],
        ["mm:btn_my_orders"],
        ["mm:btn_referral"],
        ["mm:btn_wheel"],
        ["mm:btn_contact"],
        ["mm:btn_admin_panel"],
        ["mm:btn_reseller_panel"],
    ]
    assert callback_rows(kb.main_menu_inline_kb(db, False)) == [
        ["mm:btn_buy"],
        ["mm:btn_test"],
        ["mm:btn_my_orders"],
        ["mm:btn_referral"],
        ["mm:btn_wheel"],
        ["mm:btn_contact"],
    ]
    db.close()


# Case 5
def test_state_names():
    groups, names = _state_names()
    assert groups == 81
    assert tuple(names) == STATE_NAMES
    assert len(STATE_NAMES) == 203 == len(set(STATE_NAMES))
    assert {
        "BuyFlow:waiting_config_name",
        "BuyFlow:waiting_receipt",
        "BuyFlow:waiting_customgw_phone",
        "WalletTopup:waiting_receipt",
        "DiscountEntry:waiting_code",
        "AIChatFlow:chatting",
    } <= set(names)
    assert states.BuyFlow.waiting_receipt.state == "BuyFlow:waiting_receipt"


# Case 6
def test_fsm_table_and_pragmas(tmp_path):
    path = str(tmp_path / "main.db.fsm.sqlite3")
    s = SQLiteStorage(path)
    with contextlib.closing(sqlite3.connect(path)) as conn:
        assert [(r[1], r[5]) for r in conn.execute("PRAGMA table_info(fsm_storage)")] == [
            ("bot_id", 1),
            ("chat_id", 2),
            ("user_id", 3),
            ("thread_id", 4),
            ("business_connection_id", 5),
            ("destiny", 6),
            ("state", 0),
            ("data", 0),
        ]
        assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    s2 = SQLiteStorage(path)
    asyncio.run(s.close())
    asyncio.run(s2.close())


# Case 7
def test_fsm_round_trip_survives_reopen(tmp_path):
    key = StorageKey(bot_id=1, chat_id=5001, user_id=5001)
    path = str(tmp_path / "main.db.fsm.sqlite3")
    s = SQLiteStorage(path)
    asyncio.run(s.set_state(key, states.BuyFlow.waiting_receipt))
    asyncio.run(s.set_data(key, {"order_id": 7, "label": KAF_DAL}))
    asyncio.run(s.close())

    s2 = SQLiteStorage(path)
    assert asyncio.run(s2.get_state(key)) == "BuyFlow:waiting_receipt"
    assert asyncio.run(s2.get_data(key)) == {"order_id": 7, "label": KAF_DAL}
    with contextlib.closing(sqlite3.connect(path)) as conn:
        assert conn.execute("SELECT * FROM fsm_storage").fetchall() == [
            (
                1,
                5001,
                5001,
                0,
                "",
                "default",
                "BuyFlow:waiting_receipt",
                '{"order_id": 7, "label": "' + KAF_DAL + '"}',
            )
        ]

    asyncio.run(s2.set_state(key, None))
    assert asyncio.run(s2.get_state(key)) is None
    assert asyncio.run(s2.get_data(key)) == {"order_id": 7, "label": KAF_DAL}
    with contextlib.closing(sqlite3.connect(path)) as conn:
        assert len(conn.execute("SELECT * FROM fsm_storage").fetchall()) == 1

    asyncio.run(s2.set_state(StorageKey(bot_id=1, chat_id=5001, user_id=5001, thread_id=9), "X:y"))
    asyncio.run(s2.set_state(StorageKey(bot_id=1, chat_id=5001, user_id=5001, destiny="other"), "X:z"))
    with contextlib.closing(sqlite3.connect(path)) as conn:
        assert conn.execute("SELECT thread_id, destiny, state FROM fsm_storage ORDER BY rowid").fetchall() == [
            (0, "default", None),
            (9, "default", "X:y"),
            (0, "other", "X:z"),
        ]
    asyncio.run(s2.close())


# Case 8
def test_fsm_missing_and_corrupt_data(tmp_path):
    key = StorageKey(bot_id=1, chat_id=5001, user_id=5001)
    path = str(tmp_path / "main.db.fsm.sqlite3")
    s = SQLiteStorage(path)
    assert asyncio.run(s.get_state(key)) is None
    assert asyncio.run(s.get_data(key)) == {}
    asyncio.run(s.set_state(key, "A:b"))
    assert asyncio.run(s.get_data(key)) == {}
    asyncio.run(s.set_data(key, None))
    with contextlib.closing(sqlite3.connect(path)) as conn:
        assert conn.execute("SELECT data FROM fsm_storage").fetchall() == [("{}",)]
        conn.execute("UPDATE fsm_storage SET data='not json'")
        conn.commit()
    assert asyncio.run(s.get_data(key)) == {}
    assert asyncio.run(s.get_state(key)) == "A:b"
    asyncio.run(s.close())


# Case 9
def test_start_deep_link_tokens(tmp_path):
    db = _main(tmp_path)
    db.add_or_update_user(5002, "u2", "U2")
    db.add_or_update_user(5003, "u3", "U3")
    with db._get_conn() as conn:
        conn.execute("UPDATE users SET inline_reseller_enabled=1 WHERE telegram_id IN (5002, 5003)")
    db.create_discount_code("SUMMER10", percent=10)
    router = handlers_user.create_user_router(db, is_main_bot=True)
    handler = find_handler(router, "message", "cmd_start")
    log = TelegramLog()
    bot = RecordingBot(log)

    def start(uid, text):
        state = make_state(uid)
        asyncio.run(handler(FakeMessage(log, uid, from_user=FakeUser(uid, "u", "U"), text=text), state, bot))
        return (
            asyncio.run(state.get_state()),
            asyncio.run(state.get_data()),
            [e.text for e in log.events if e.chat_id == uid],
        )

    # (a)
    st, data, texts = start(5001, "/start resref_5002-disc_summer10-campaignX-nofj-ref5003")
    assert st is None
    assert data == {"pending_discount_code_id": 1, "pending_discount_code_label": "SUMMER10"}
    assert texts == [WELCOME, DISC_ON.format(code="SUMMER10")]
    assert _user_row(db, 5001) == (5002, 5003, "campaignX", 1)

    # (b)
    st, data, texts = start(5001, "/start campaignY-resref_5003-ref5002")
    assert st is None
    assert data == {}
    assert texts == [WELCOME, DISC_ON.format(code="SUMMER10"), WELCOME]
    assert _user_row(db, 5001) == (5002, 5003, "campaignX", 1)

    # (c)
    st, data, texts = start(5004, "/start resref_5004-ref5004-prod_x-disc_NOPE-prod_77")
    assert data == {}
    assert texts == [WELCOME, PRODUCT_GONE]
    assert _user_row(db, 5004) == (None, None, None, 1)

    # (d)
    st, data, texts = start(5005, "/start")
    assert texts == [WELCOME]
    assert _user_row(db, 5005) == (None, None, None, 0)

    # Finally
    assert len(log.events) == 6
    assert _user_row(db, 5002) == (None, None, None, 0)
    db.close()
