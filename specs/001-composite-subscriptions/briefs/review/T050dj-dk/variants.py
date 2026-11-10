"""Current production compatibility reference and independent bounded mutations."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('prior',Path(__file__).parents[1]/'T050ct-cu/variants.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
once,change=m.once,m.change
SOURCES=['extra_gateway_payment.py','database.py']
def variants(payment,db):
    yield 'reference',payment,db
    for name,b,a in [
        ('cache_ge','len(last_checked) > 2000','len(last_checked) >= 2000'),
        ('cache_high','len(last_checked) > 2000','len(last_checked) > 2001'),
        ('cache_no_clear','last_checked.clear()','pass'),
        ('cache_clears_small','len(last_checked) > 2000','len(last_checked) > 1998'),
        ('cache_before_process','                result, text = await process_invoice(db, bot, invoice)','                if len(last_checked) > 2000:\n                    last_checked.clear()\n                result, text = await process_invoice(db, bot, invoice)'),
        ('cache_after_process','                last_checked[invoice["id"]] = now\n                result, text = await process_invoice(db, bot, invoice)','                result, text = await process_invoice(db, bot, invoice)\n                last_checked[invoice["id"]] = now'),
        ('send_failure_aborts','                    except Exception:\n                        pass','                    except Exception:\n                        raise'),
    ]:yield name,change(payment,'poll_loop',lambda s:once(s,b,a)),db
    for name,b,a in [
        ('sql_new_only',"status IN ('new','pending')","status IN ('new')"),
        ('sql_pending_only',"status IN ('new','pending')","status IN ('pending')"),
        ('sql_terminal',"status IN ('new','pending')","status IN ('new','pending','completed')"),
        ('sql_stars',"AND gateway != 'tgstars' ",''),
        ('sql_desc','ORDER BY id LIMIT','ORDER BY id DESC LIMIT'),
        ('sql_default','limit: int = 100','limit: int = 50'),
        ('sql_no_limit','(int(limit),)','(-1,)'),
        ('sql_clamp','(int(limit),)','(max(1,min(200,int(limit))),)'),
        ('sql_kind',"AND gateway != 'tgstars'","AND kind='order' AND gateway != 'tgstars'"),
        ('sql_unknown_gateway',"AND gateway != 'tgstars'","AND gateway = 'zarinpal'"),
        ('sql_projection','SELECT * FROM extra_gateway_invoices','SELECT id,gateway,kind,ref_id,user_id,amount_toman+1 AS amount_toman,payable_amount,status FROM extra_gateway_invoices'),
        ('sql_invalid_default','(int(limit),)','(int(limit or 100),)'),
    ]:yield name,payment,change(db,'list_open_extra_invoices',lambda s:once(s,b,a))
