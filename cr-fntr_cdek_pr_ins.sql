-- DROP FUNCTION shp.fntr_cdek_pr_ins();

CREATE OR REPLACE FUNCTION shp.fntr_cdek_pr_ins()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
declare 
/*
    ret varchar;
    cdek_num varchar; 
    sts int;
    mail_body varchar default 'error';
*/
BEGIN

perform shp.cdek_download_barcode(NEW.order_uuid);
/*
--ret=cdek_check_uuid(OLD.our_firm, OLD.cdek_uuid);
ret=cdek_check_uuid('api'::varchar, OLD.cdek_uuid::varchar);
select cdek_number, sts_code, ret_msg INTO cdek_num, sts, ret from cdek_preorder_params where shp_id=OLD.shp_id;
if cdek_num Is Not Null then
    mail_body='shp_id: ' || OLD.shp_id::varchar || ' фирма: ' || OLD.our_firm || ' cdek_number: ' || cdek_num;
--  PERFORM send_noreply('petrushenko@kipspb.ru', 'СДЭК', mail_body, 't');
    PERFORM send_noreply('machulin@kipspb.ru', 'СДЭК', mail_body, 't');
else
    PERFORM arc_energo.put_msg('pam_event','e' || OLD.shp_id::varchar) || ret;
    mail_body='shp_id: ' || OLD.shp_id::varchar || ' фирма: ' || OLD.our_firm || ' cdek_number: ' || ret;
--  PERFORM send_noreply('vscherbo@kipspb.ru', 'СДЭК', mail_body, 't');
    PERFORM send_noreply('machulin@kipspb.ru', 'СДЭК', mail_body, 't');
end if;
*/
RETURN NEW;
END;
$function$
;

-- Permissions

ALTER FUNCTION shp.fntr_cdek_pr_ins() OWNER TO arc_energo;
GRANT ALL ON FUNCTION shp.fntr_cdek_pr_ins() TO arc_energo;
